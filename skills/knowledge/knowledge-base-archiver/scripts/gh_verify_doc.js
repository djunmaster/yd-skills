'use strict';
// 提交后校验：只回报大小/行数/头尾片段 + 断言结果，不把整篇正文拉回上下文。
// 用法：node scripts/gh_verify_doc.js '{"path":"docs/ai/x.md","mustContain":["关键词A","关键词B"]}'
// 输出：{ok, size, chars, lines, head, tail, checks[], allFound}
const { getArgs, needFetch, run, b64ToText, encPath } = require('./lib');

run(async () => {
  const a = await getArgs();
  const { owner, repo, token, path: p, branch = 'master', mustContain = [] } = a;
  if (!p) throw new Error('缺少 path');

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
  const t = await r.text();
  let j = null;
  try { j = JSON.parse(t); } catch (e) { /* 非 JSON */ }

  if (!r.ok || !j || !j.content) return { ok: false, status: r.status, error: (j && j.message) || t.slice(0, 200) };

  const text = b64ToText(j.content);
  const lines = text.split('\n');
  const checks = mustContain.map((s) => ({ needle: s, found: text.includes(s) }));

  return {
    ok: true,
    path: p,
    sha: j.sha,
    size: Buffer.byteLength(text, 'utf8'),
    chars: text.length,
    lines: lines.length,
    head: lines.slice(0, 6).join('\n'),
    tail: lines.slice(-4).join('\n'),
    checks,
    allFound: checks.every((c) => c.found),
  };
});