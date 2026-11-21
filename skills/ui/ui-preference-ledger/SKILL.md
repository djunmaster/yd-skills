---
name: ui-preference-ledger
description: 记录、归纳和维护用户在 UI 任务中的长期个人偏好、反模式黑名单（Anti-Patterns）与当前项目 DESIGN.md 偏好。仅在用户明确要求沉淀、归纳、初始化或查看偏好时调用；不生成或修改业务界面。
---

# UI Preference Ledger (v2.0)

## 1. 跨端路径规范（移除硬编码用户目录）
- **全局个人 Profile**：`~/.codex/design-profiles/universal-ui.md`（Windows 下解析为 `%USERPROFILE%\.codex\design-profiles\universal-ui.md`，禁止硬编码特定用户名路径）。
- **当前项目偏好**：优先写入当前项目 `DESIGN.md` 的 `## UI preference` 小节；无此文件时可按用户授权创建 `.agents/design-context.md`。
- **授权边界**：修改任何本地 Profile 或项目文件前，必须确认当前会话有明确用户授权；无授权时只输出建议写入的 Markdown 片段。

## 2. 四种工作模式
- `record`：记录本次确认的色盘、密度、参考标杆产品、被否决方向与理由。
- `summarize`：从多次记录中归纳 **最多 8 条正面可执行规则** + **最多 8 条负面黑名单（Anti-Patterns）**。
- `review`：展示全局规则、黑名单、项目偏好及两者冲突点。
- `init-design-md`（v2 新增）：根据当前全局偏好，为新项目一键生成简洁的 `DESIGN.md` 脚手架。

## 3. 归属判定规则
- “以后 / 总是 / 我喜欢 / 我讨厌” → 全局规则或 Anti-Patterns 候选
- “这个项目 / 这个客户 / 当前技术栈” → 写入当前项目 `DESIGN.md`
- “这次先 / 临时演示” → 不沉淀
