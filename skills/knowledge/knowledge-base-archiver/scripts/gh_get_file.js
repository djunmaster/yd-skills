'use strict';
// 读仓库里的单个文件，或列目录。
// 用法：node scripts/gh_get_file.js '{"path":"README.md"}'
//      echo '{"path":"docs/ai"}' | node scripts/gh_get_file.js
// 参数：path 必填；owner/repo/branch/token 缺省取 config.json
// 输出：文件 → {ok,kind:'file',sha,size,content}；目录 → {ok,kind:'dir',entries:[...]}
const { getArgs, needFetch, run, b64ToText, encPath } = require('./lib');

run(async () => {
  const a = await getArgs();
  const { owner, repo, token, path: p, branch = 'master' } = a;
  if (!p) throw new Error('缺少 path');
  if (!owner || !repo || !token) throw new Error('缺少 owner/repo/token，请在 config.json 里填好');

  const f = needFetch();
  const url = 'https://api.github.com/repos/' + owner + '/' + repo + '/contents/' + encPath(p) + '?ref=' + encodeURIComponent(branch);
  const r = await f(url, {
    headers: {
      Authorization: 'Bearer ' + token,
      Accept: 'application/vnd.github+json',
      'X-GitHub-Api-Version': '2022-11-28',
      'User-Agent': 'workbuddy-knowledge-base-archiver',
    },
  });
  const txt = await r.text();
  let j = null;
  try { j = JSON.parse(txt); } catch (e) { /* 非 JSON */ }

  if (!r.ok) return { ok: false, status: r.status, error: (j && j.message) || txt.slice(0, 300) };
  if (Array.isArray(j)) {
    return { ok: true, kind: 'dir', path: p, entries: j.map((e) => ({ name: e.name, path: e.path, type: e.type, sha: e.sha })) };
  }
  return {
    ok: true,
    kind: 'file',
    path: p,
    sha: j.sha,
    size: j.size,
    content: j.content ? b64ToText(j.content) : null,
  };
});