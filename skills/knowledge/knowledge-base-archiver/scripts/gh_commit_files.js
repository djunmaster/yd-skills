'use strict';
// 一次提交多个文件（文档 + README）到分支。主路径是 git tree + 单次 commit（原子），失败自动退化为逐文件 Contents PUT。
// 用法：node scripts/gh_commit_files.js '{...}'
// 参数：
//   message           必填，提交信息
//   iHaveUserConsent  必须为 true —— 用户没明确确认就别传，脚本会拒绝写库
//   files[]           每项三选一：
//                       { path, localPath }  从本地文件读（推荐，大文档不占上下文）
//                       { path, content }    内联 UTF-8 文本（README 这类小文件）
//                       { path, base64 }     二进制
// 输出：{ok, mode:'tree'|'contents-fallback', commitSha, url, committed[]}
const fs = require('fs');
const path = require('path');
const { getArgs, needFetch, run, textToB64, encPath } = require('./lib');

run(async () => {
  const a = await getArgs();
  const { token, owner, repo, branch = 'master', message, files, iHaveUserConsent } = a;

  if (!token || !owner || !repo || !message || !Array.isArray(files) || !files.length) {
    throw new Error('缺少参数：需要 message 与 files[]（token/owner/repo 可来自 config.json）');
  }
  if (iHaveUserConsent !== true) {
    return { ok: false, error: '未收到用户确认（iHaveUserConsent 必须为 true），拒绝写仓库。先把文档给用户看，等他明确同意。' };
  }

  const f = needFetch();
  const API = 'https://api.github.com';
  const B = encodeURIComponent(branch);
  const H = {
    Authorization: 'Bearer ' + token,
    Accept: 'application/vnd.github+json',
    'Content-Type': 'application/json',
    'X-GitHub-Api-Version': '2022-11-28',
    'User-Agent': 'workbuddy-knowledge-base-archiver',
  };

  // 链路偶发连接重置（fetch failed / ECONNRESET）：加超时与有限重试，避免整套提交白跑。
  // 只重试网络层异常；HTTP 4xx/5xx 是业务结果，原样交给上层判断。
  const call = async (method, url, body) => {
    const payload = body === undefined ? undefined : JSON.stringify(body);
    let lastErr;
    for (let attempt = 1; attempt <= 3; attempt++) {
      try {
        const r = await f(API + url, {
          method, headers: H, body: payload,
          signal: AbortSignal.timeout(30000),
        });
        const t = await r.text();
        let j = null;
        try { j = JSON.parse(t); } catch (e) { /* 非 JSON */ }
        return { status: r.status, j, t };
      } catch (e) {
        lastErr = e;
        if (attempt < 3) continue;
      }
    }
    throw new Error('GitHub API 网络请求失败（已重试 3 次）：' + String((lastErr && (lastErr.cause?.code || lastErr.message)) || lastErr));
  };

  // 把 files[] 统一成 {path, content} 或 {path, base64}
  const items = files.map((x) => {
    if (typeof x.content === 'string') return { path: x.path, content: x.content };
    if (x.base64) return { path: x.path, base64: x.base64 };
    if (x.localPath) {
      const abs = path.isAbsolute(x.localPath) ? x.localPath : path.resolve(process.cwd(), x.localPath);
      return { path: x.path, content: fs.readFileSync(abs, 'utf8') };
    }
    throw new Error('files 项需要 localPath / content / base64 之一：' + x.path);
  });

  // —— 主路径 ——
  const runTree = async () => {
    const ref = await call('GET', '/repos/' + owner + '/' + repo + '/git/ref/heads/' + B);
    if (!ref.j || !ref.j.object) return { step: 'get-ref', status: ref.status, error: (ref.j && ref.j.message) || ref.t.slice(0, 200) };
    const refSha = ref.j.object.sha;

    const cmt = await call('GET', '/repos/' + owner + '/' + repo + '/git/commits/' + refSha);
    if (!cmt.j || !cmt.j.tree) return { step: 'get-commit', status: cmt.status, error: (cmt.j && cmt.j.message) || cmt.t.slice(0, 200) };

    const tree = [];
    for (const it of items) {
      if (it.base64) {
        const bl = await call('POST', '/repos/' + owner + '/' + repo + '/git/blobs', { content: it.base64, encoding: 'base64' });
        if (!bl.j || !bl.j.sha) return { step: 'blob', path: it.path, status: bl.status, error: (bl.j && bl.j.message) || bl.t.slice(0, 200) };
        tree.push({ path: it.path, mode: '100644', type: 'blob', sha: bl.j.sha });
      } else {
        tree.push({ path: it.path, mode: '100644', type: 'blob', content: it.content });
      }
    }

    const tr = await call('POST', '/repos/' + owner + '/' + repo + '/git/trees', { base_tree: cmt.j.tree.sha, tree });
    if (!tr.j || !tr.j.sha) return { step: 'create-tree', status: tr.status, error: (tr.j && tr.j.message) || tr.t.slice(0, 200) };

    const nc = await call('POST', '/repos/' + owner + '/' + repo + '/git/commits', { message, tree: tr.j.sha, parents: [refSha] });
    if (!nc.j || !nc.j.sha) return { step: 'create-commit', status: nc.status, error: (nc.j && nc.j.message) || nc.t.slice(0, 200) };

    // 注意：更新引用必须用复数 /git/refs/heads/，单数 /git/ref/heads/ 只有 GET 能用，PATCH 会 404
    const up = await call('PATCH', '/repos/' + owner + '/' + repo + '/git/refs/heads/' + B, { sha: nc.j.sha, force: false });
    if (up.status !== 200 && up.status !== 204) {
      return { step: 'update-ref', status: up.status, error: (up.j && up.j.message) || up.t.slice(0, 200), partialCommit: nc.j.sha };
    }

    return {
      commitSha: nc.j.sha,
      url: 'https://github.com/' + owner + '/' + repo + '/commit/' + nc.j.sha,
      committed: items.map((x) => x.path),
      bytes: items.map((x) => ({ path: x.path, size: x.content ? Buffer.byteLength(x.content, 'utf8') : null })),
    };
  };

  // —— 兜底：逐文件 Contents API（每文件一个 commit）——
  const runFallback = async () => {
    const done = [];
    for (const it of items) {
      if (it.base64) { done.push({ path: it.path, skipped: 'Contents 兜底只处理文本，二进制请修好 tree 流程' }); continue; }
      const cur = await call('GET', '/repos/' + owner + '/' + repo + '/contents/' + encPath(it.path) + '?ref=' + B);
      const body = { message: message + ' — ' + it.path, content: textToB64(it.content), branch };
      if (cur.status === 200 && cur.j && cur.j.sha) body.sha = cur.j.sha;
      const put = await call('PUT', '/repos/' + owner + '/' + repo + '/contents/' + encPath(it.path), body);
      if (!put.j || !put.j.commit) done.push({ path: it.path, status: put.status, error: (put.j && put.j.message) || put.t.slice(0, 200) });
      else done.push({ path: it.path, commitSha: put.j.commit.sha });
    }
    return done;
  };

  const primary = await runTree();
  if (primary.error) {
    const fb = await runFallback();
    return { ok: fb.every((x) => x.commitSha), mode: 'contents-fallback', treeFailure: primary, commits: fb };
  }
  return Object.assign({ ok: true, mode: 'tree' }, primary);
});