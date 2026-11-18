---
name: universal-ui
description: 设计或精修用户指定的 UI：可从五个整页模板取用局部组件，也可按需求推导布局并推荐可选风格。适用于局部组件复用、新工具原型和参考型界面转译；不复制产品外壳，不安装组件包，也不负责写入 UI 偏好。
---

# Universal UI

Universal UI 用于局部复用已确认组件、为新工具推导布局和风格、转译参考型界面。用户决定功能、字段、操作和页面位置；保留目标项目的导航、框架和数据接入。

| 原参考页 | Skill 模板 | 可单独取用 |
| --- | --- | --- |
| 收入分析 | [analytics.html](assets/analytics.html) | 周期切换、四列指标带、收入趋势与数据明细 |
| 服务监控 | [monitoring.html](assets/monitoring.html) | 服务筛选、状态时间线、可用率与状态说明 |
| 模型网关 | [gateway.html](assets/gateway.html) | 提供方配置行、状态标签、延迟与启停开关 |
| 客户管理 | [crm.html](assets/crm.html) | 工具行、搜索与负责人筛选、可排序记录表 |
| 订阅分析 | [saas.html](assets/saas.html) | 逾期提示、收款摘要与进度、账单状态 |

## 选择工作方式

- **局部复用**：用户明确指定一个区块时，只读取对应模板和所需样式，按“固定风格”实现。
- **新页面 / 新工具**：先读 [design-workflow.md](references/design-workflow.md)，再从 [layout-atlas.html](assets/layout-atlas.html) 的 36 个页面布局方案中选择结构，完成需求定位、信息架构、布局选择和风格候选。
- **风格可选**：当用户没有锁定视觉方向，先看 [style-atlas.html](assets/style-atlas.html) 的 56 个克制样张，再按 [style-selection.md](references/style-selection.md) 给出三个可区分的候选；确认后按 [style-library.md](references/style-library.md) 执行。
- **偏好读取**：生成方案前，优先读取当前项目 `DESIGN.md`，再读取 `%USERPROFILE%/.codex/design-profiles/universal-ui.md`；不要写入这两个文件。用户要求沉淀偏好时，交给 `$ui-preference-ledger`。

## 局部复用方式

1. 先定位目标页面与区块，确认现有技术栈、字段、数据来源和主要操作。只读取匹配的一个 HTML 模板及其所需样式；仅当用户需要多个区块时再组合。
2. 保留参考区块的阅读顺序、密度、状态和语义配色。用目标项目现有的控件、主题和图表机制实现；没有可用控件时才移植必要的 HTML/CSS。不要复制演示页标题、主题按钮、导航或数据，也不要引入另一套依赖或全局重置。
3. 用真实数据驱动读数和操作。图表、指标与表格使用相同筛选范围和统计口径。数据区按需覆盖加载、空、无匹配、错误和重试；CRM 模板可用 `?state=loading`、`?state=empty` 或 `?state=error` 预览这些差异。示例操作只改本地状态。
4. 在浅色、深色和窄屏实际检查所选区块；按 [验收清单](references/visual-quality.md) 修正再交付。只交付用户指定的 UI，不顺手重做旁边区块。

## 默认风格

- 柔和中性画布、弱分隔线、克制的圆角和阴影。主操作用 `--action`（浅色石墨、深色反白）；紫色用于焦点、选中和轻强调，状态色同时配文字。不加渐变装饰、玻璃效果、嵌套卡片或重阴影。
- 正文 14px，辅助文字不低于 12px，常用行内控件 32px，数据表行约 44px。标题、筛选、主体、反馈各有固定位置；数字等宽并对齐，长内容优先折行，窄屏让工具栏换行、表格区内部滚动。
- 标签只表状态，可操作项用原生控件或目标项目的可访问封装。按下不位移，键盘焦点清楚；图表有单位、范围和文本/数据替代；异步反馈只用一个播报区，表单失败指向具体字段。

Neutral Core 是默认基线。用户在完整流程中确认其他风格后，该风格成为当前项目的锁定风格；不要在同一项目内反复切换。

个人偏好优先级：本次明确要求 > 项目 `DESIGN.md` > 全局 Profile > Neutral Core 默认规则。Profile 不存在时，按 Neutral Core 和用户本次要求执行。

HTML 可直接离线打开。配套文件只有 [语义 tokens](assets/tokens.css)、[区块样式](assets/blocks.css) 和 [本地演示交互](assets/demo.js)。主题由 `data-theme` 切换；复用时将需要的语义变量映射到目标区块，避免覆盖宿主的全局主题。
