# 仓库约定、索引表与 API

## README 索引表

三列，表头固定；**最新一条插在分隔线正下方**（倒序，新在上）。

```markdown
## 索引

| 收录日期 | 标题 | 原文链接 |
| --- | --- | --- |
| 2026-11-11 | [新文章的标题](docs/ai/新文章的标题.md) | https://原文地址 |
| 2026-11-10 | [旧文章的标题](docs/tools/旧文章的标题.md) | https://原文地址 |
```

注意：

- 第二列用 **GitHub 官方绝对 blob 链接**（`https://github.com/<owner>/<repo>/blob/<branch>/docs/<分类>/<文件名>.md`，路径已 percent-encode）。直接取 Contents API / `gh_get_file.js` 返回的 `html_url`，不要手拼、不要解码；标题文本与文档 H1、文件名三者一致。上面示例里的相对路径仅为表格格式示意。
- **不要用仓库内相对链接**（`docs/ai/xxx.md`）：GitHub 的 GFM 渲染（含带仓库 context 的 `/markdown`）输出的 href 仍是相对路径，在仓库首页 URL 基准下可能解析到错误地址；文件名含字面 `%` 时还会被拼成非法转义（`68%%E7...`），点击必然 404。若必须写相对链接，`%` 必须写成 `%25`。
- 第三列是**原文地址**（不是仓库地址），不带反引号、不加尖括号。
- 日期用 `YYYY-MM-DD`，取整理当天。
- 只在末尾追加或插在顶部，不要重排历史行、不要改别人的格式。

## 目录结构与分类词表

路径：`docs/<分类>/<纯中文标题>.md`，文件名**不带日期前缀**。

| 分类 | 收什么 |
| --- | --- |
| `docs/tools` | 软件工具、汉化、破解边界内的使用教程 |
| `docs/network` | 代理、DNS、CDN、网络排查 |
| `docs/server` | 自建服务、部署、运维 |
| `docs/dev` | 编程语言、框架、工程实践 |
| `docs/ai` | 模型、Agent、提示词相关 |
| `docs/frontend` | 前端、浏览器、样式 |
| `docs/security` | 安全、加固、审计 |
| `docs/misc` | 无法归类时用 |

**先复用再新增**：动手前先列一次 `docs/` 看已有目录，别为同义分类再造一个（`tools` 和 `工具` 不能并存）。

## API 要点

- 全部经 `scripts/` 里的脚本走，不要在对话里手拼 curl。
- 认证头：`Authorization: Bearer <fine-grained PAT>`、`Accept: application/vnd.github+json`、`X-GitHub-Api-Version: 2022-11-28`。
- 私有仓库**不能**靠浏览器登录态调 api.github.com——Cookie 不被 API 接受，必须用 PAT。
- 路径含中文/空格：按 `/` 切开逐段 `encodeURIComponent` 再拼回去（整串 `encodeURI` 会把 `/` 和 `#` 漏掉）。脚本已处理。
- 分支是 **`master`**。若用户改了默认分支，读 `repo.default_branch` 而不是猜 `main`。
- 匿名请求会被共享 IP 限流（403 "API rate limit exceeded"），带 token 后不受影响——看到 403 先怀疑 token 没传对。
- fine-grained PAT 只要对该仓库给了 `Contents: Read and write`，tree+commit+ref 全套就够用，不需要额外 Git Data 权限。

## 提交方式：一个 commit

用 `gh_commit_files.js` 一次带上文档 + README，主路径是 git tree + 单次 commit（原子）。文档用 `localPath` 从本地读，别把几万字节内联进命令行：

```bash
node scripts/gh_commit_files.js '{
  "message": "入库：<标题>（docs/<分类>）",
  "iHaveUserConsent": true,
  "files": [
    {"path": "docs/ai/标题.md", "localPath": "./drafts/标题.md"},
    {"path": "README.md", "content": "# ...整份 README..."}
  ]
}'
```

README 这种几百字节的才内联；大文档一律 `localPath`。

## 故障对照

| 现象 | 处理 |
| --- | --- |
| `404 Bad credentials` / `Not Found` | token 失效或仓库名写错。fine-grained token 必须显式包含该仓库授权，私有库没授权时 GitHub 一律报 404 而非 403 |
| 输出里出现 `mode: "contents-fallback"` | 多文件退化成了**一文件一 commit**，内容对但不再原子。查 `treeFailure.step`：若是 `update-ref` + 404，几乎都是 ref 更新 URL 写成单数 `/git/ref/heads/…`（PATCH 必须复数 `/git/refs/heads/…`，GET 才是单数）。这条已修，别改回去 |
| `409 Conflict` / `update-ref` 失败（非 404） | 期间有人推了新提交。重新读一次 README 拿到新 sha 和 base tree 再提交，别硬改 ref |
| `422` 且提到 sha | Contents PUT 缺了已存在文件的 `sha`——脚本会自动先 GET 取 sha，仍失败说明路径变了，列目录确认 |
| 内容乱码 | 编码没走 UTF-8；脚本内部用 `content` 原文字段和 `Buffer.from(...,'utf8')`，正常不会遇到 |
| 连续 3 次失败 | 停手，把原始 API 报错贴给用户，让他确认 token 权限范围 |
| `fetch failed` / `ECONNRESET`（提交脚本） | 链路间歇性连接重置，不是 token 失效。`gh_commit_files.js` 的 `call` 已内置 3 次有限重试 + 30s 超时；仍失败时先用 `gh_get_file.js` 确认 API 可读，再重跑，别连续盲试 |

## 提交后自检

用 `gh_verify_doc.js`（**不要**用 `gh_get_file.js` 拉正文——几万 token 白烧）：传 `mustContain` 断言（中文标题、至少一个术语译法、图床图片地址、附录图床索引），它只回报大小/行数/头尾片段和断言结果。再 `gh_get_file.js` 读一次 README 确认索引行在位。

比对要点：落库字节数应与本地文件一致，首行是 `# <中文标题>`；不一致就是路径写错或内容被中途改动，别急着回执。