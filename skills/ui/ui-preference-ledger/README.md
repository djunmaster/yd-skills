# UI Preference Ledger (v2.0)

把一次 UI 选择沉淀成可复用的长期规则，同时区分「个人长期偏好」与「当前项目偏好」。个人 Profile 是全集，项目偏好只写入当前项目，不污染全局规则。

本 Skill 只做偏好沉淀，**不生成或修改业务界面**。

## 四种工作模式

| 模式 | 作用 |
| --- | --- |
| `record` | 记录本次确认的色盘、密度、参考标杆、被否决方向与理由 |
| `summarize` | 从多次记录归纳**最多 8 条正面可执行规则** + **最多 8 条反模式黑名单** |
| `review` | 展示全局规则、黑名单、项目偏好及两者冲突点 |
| `init-design-md` | v2 新增：按当前全局偏好，为新项目一键生成简洁的 `DESIGN.md` 脚手架 |

v2.0 相比上一版有两点实质变化：新增 `init-design-md` 模式；`summarize` 明确产出**正负两张清单**（规则 + Anti-Patterns），负面清单与正面规则同等重要——「不要什么」往往比「要什么」更好执行。

## 数据位置

| 类型 | 路径 |
| --- | --- |
| 全局个人 Profile | `~/.codex/design-profiles/universal-ui.md`（Windows 解析为 `%USERPROFILE%\.codex\design-profiles\universal-ui.md`） |
| 当前项目偏好 | 优先写入项目 `DESIGN.md` 的 `## UI preference` 小节 |
| 无 `DESIGN.md` 时 | 经用户授权后创建 `.agents/design-context.md` |

路径一律按环境变量解析，**不硬编码具体用户名**。修改任何本地 Profile 或项目文件前必须确认当前会话有明确授权；无授权时只输出建议写入的 Markdown 片段。

## 归属判定

| 说法 | 归属 |
| --- | --- |
| 「以后 / 总是 / 我喜欢 / 我讨厌」 | 全局规则或 Anti-Patterns 候选 |
| 「这个项目 / 这个客户 / 当前技术栈」 | 写入当前项目 `DESIGN.md` |
| 「这次先 / 临时演示」 | 不沉淀 |

## 使用

```text
使用 $ui-preference-ledger 记录这次选择：
Agent 工作台用稳定三列，左侧导航窄一点，中央消息区最大。
我以后都不喜欢卡片墙和过度留白。
```

```text
使用 $ui-preference-ledger 的 init-design-md，
按我的全局偏好为这个新项目生成一份 DESIGN.md。
```
