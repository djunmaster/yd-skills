# UI Preference Ledger

把一次 UI 选择沉淀为长期规则，同时区分“个人长期偏好”和“当前项目偏好”。个人 Profile 是全集，包含归纳规则与各项目使用记录；项目偏好只写入当前项目，不污染全局规则。

## 工作模式

- **record**：记录本次选择的布局、风格、密度、被否决方向和理由。
- **summarize**：从多次使用记录中归纳最多 8 条可执行规则。
- **review**：查看全局规则、项目偏好、最近记录和两者冲突。

## 数据位置

- 全局个人 Profile：`%USERPROFILE%/.codex/design-profiles/universal-ui.md`
- 项目偏好：当前项目 `DESIGN.md` 的 `UI preference` 小节；没有时才创建 `.agents/design-context.md`
- Skill 本体：只保存流程，不写入任何用户项目信息

## 使用

```text
使用 $ui-preference-ledger 记录这次选择：
Agent 工作台用稳定三列，左侧导航窄一点，中央消息区最大。
我以后都不喜欢卡片墙和过度留白。
```

归属规则：

- “以后”“总是”“我讨厌” → 全局规则候选
- “这个项目”“这个品牌”“当前技术栈” → 项目偏好
- “这次先”“为了演示”“临时” → 不沉淀
