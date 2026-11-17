# 知识库归档器（knowledge-base-archiver）

把「正在浏览的好文章」完整读全、深度去噪、按领域惯例翻译成中文、转存正文配图到自建图床，并原子提交归档至个人 GitHub 知识库仓库与更新 README 索引表。

## 安装与使用（WorkBuddy / 智能助手）

### 装法一：上传技能包（推荐）

1. 打开 WorkBuddy → 左侧 **专家 · 技能 · 连接器** → **技能** 页签
2. 点 **添加技能** → **上传技能**
3. 选技能打包 zip（或文件夹）
4. 导入后**新建一个会话**即可生效

### 装法二：手动放置目录

把 `knowledge-base-archiver/` 文件夹放到本地技能目录：

- Windows：`%USERPROFILE%\.workbuddy\skills\knowledge-base-archiver\` 或 `%USERPROFILE%\.workbuddy\plugins\marketplaces\knowledge-base-archiver\`
- macOS / Linux：`~/.workbuddy/skills/knowledge-base-archiver/`

放好后新建会话或重启生效。

## 装完先做两件事

**1. 确认 Node 版本**（脚本全部是原生 Node CLI，要求 18+）：

```bash
node -v
```

**2. 配置凭据与体检**：

首次使用时，确认本目录的 `config.json`（可参考 `config.example.json`）：
- `token`: GitHub fine-grained PAT（只需知识库仓库 `Contents: Read and write` 权限）
- `owner`: 你的 GitHub 用户名
- `repo`: 你的知识库仓库名称
- `imgbed.base`: 你的自建图床 API 地址（如基于 CloudFlare-ImgBed）

在技能目录执行体检：

```bash
node scripts/gh_get_file.js '{"path":"README.md"}'
```

返回 `{"ok":true,"kind":"file",...}` 说明 token 与仓库连通正常。

## ⚠️ 安全与配置提示

- **请勿将填入真实 GitHub Token 的 `config.json` 上传到公开仓库或发给他人**。
- fine-grained PAT 建议仅最小化授予知识库仓库的 Contents 读写权限。
- 技能内置双锁硬门禁机制：必须经用户明确回复确认，且脚本收到 `iHaveUserConsent: true` 才会向远程仓库发起写操作。

## 日常怎么用

直接说人话即可触发：

- 「把这个页面整理成 markdown 存到知识库」
- 「归档这篇文章，顺便提交到知识库」
- 预览整理稿后回复「确认了 / 提交吧」执行单 Commit 原子提交

## 脚本速查

| 脚本 | 作用 |
| --- | --- |
| `gh_get_file.js` | 读文件 / 列目录，参数 `path` |
| `gh_commit_files.js` | 多文件一次提交，需 `iHaveUserConsent: true`、`message`、`files[]` |
| `gh_verify_doc.js` | 提交后校验，参数 `path`、`mustContain[]` |
| `imgbed_upload.js` | 并行上传图片，参数 `folder`、`items[{name,url|localPath}]` |

参数是 JSON，既可当第一个命令行参数，也可从 stdin 管道传入：

```bash
echo '{"path":"README.md"}' | node scripts/gh_get_file.js
```

`gh_commit_files.js` 的 `files[]` 支持三种写法：`{path, localPath}`（从本地读，推荐）、`{path, content}`（内联小文本）、`{path, base64}`（二进制）。

## 目录结构

```
knowledge-base-archiver/
├── SKILL.md              技能主体：流程、硬门禁与去噪规范
├── README.md             本说明文档
├── config.json           运行配置（已脱敏示例，填入个人凭据）
├── config.example.json   配置模板
├── drafts/               本地整理稿暂存目录
│   └── .gitkeep
├── references/
│   ├── extraction.md     各类页面（Discourse/X/PDF/长文）深度读取方法
│   ├── doc-template.md   骨架、去噪、专业术语翻译规范、配图规范
│   ├── github-api.md     仓库约定、索引表倒序追加、Tree Commit API 机制
│   └── imgbed.md         自建图床接口、鉴权与图片取舍标准
└── scripts/              五个 Node CLI 脚本 + lib.js
```
