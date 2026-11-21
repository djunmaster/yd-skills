---
name: yd-editorial-tech-illustrations
description: "用于技术文章、AI 教程、系统架构与流程配图。用户在图解上下文中只需提供内容，本技能自动沿用固定的暖白、深靛蓝、浅紫蓝与陶土橙编辑式风格，无需重复指定画风。"
---
# 编辑式技术图解（v1.2.1）

将技术内容转换为有文字解释、关系完整、色彩层次克制而饱满的编辑式技术图解，并持续沿用本技能内置母版。风格版本与参数锁见 [style-lock.json](references/style-lock.json)，历史实测见 [验证记录](references/validation.md)。

`v1.2.1` 相对 `1.1.0-rc.1` 的核心升级：
1. **节点与总字数硬上限**：`max_nodes` 从 12 收紧到 **8**（理想 5–7 个），新增全图总字数上限 **180 字**，`caption` 统一收紧到 ≤20 字（推荐 6–16 字），`summary` 推荐 ≤24 字以减少左栏折行叠字。
2. **三级卡片色阶与定制微图示**：保留原版高辨识度配色丰度，避免整图变素——顶部/阶段用实心深靛蓝 `#29277B` 紧凑胶囊；普通节点用 `#EFEBE3` 暖灰底；1–2 个核心引擎/决策节点用浅紫蓝 `#E6E9F8` + `#777FC3` 描边；命中/成功捷径可用淡鼠尾草绿 `#EDF2EA` + `#5C7A4E`；关键节点配定制几何微图示，不用千篇一律的小圆点。
3. **单语义陶土橙 + 外围反馈走廊**：右侧仅一条声明的核心证据/风险/跨区转移线用陶土橙 `#D7704E`（左侧金句块可用浅陶土底 `#F2E7DF` + 细橙竖条呼应）；去掉装饰性像素点；每条边强制单线出口，反馈虚线一律走画布外围走廊，严禁交叉实线。
4. **出图后逐字核验门禁**：`prepare_prompt.py` 自动导出 `verification_checklist`，成图必须逐项比对汉字后才可交付。

## 默认输入与调用

当用户要求技术文章、AI 教程、系统架构或技术流程配图时，默认使用本技能。将用户提供的文字视为内容数据，自动整理受众、结论、节点和关系；不要求用户重复指定配色、字体或版式。只有用户明确要求另一种画风时才覆盖本次默认值。

## 内置版式

| 版式 | 用途 | 附加母版 |
| :--- | :--- | :--- |
| `editorial`（默认） | 文章主图、概念原理、分支架构 | 无 |
| `chapters` | 按阶段逐段说明原理 | [章节母版](references/layout-chapters.png) |
| `lanes` | 区分不同执行主体或系统泳道 | [泳道母版](references/layout-lanes.png) |

## 工作流程

1. 提炼核心结论、必要节点（控制在 5–8 个）和有向关系；超过 8 个节点或总字数超过 180 字时优先拆成两张图。
2. 参照 [内容输入示例](references/content-example.json) 编写本次内容 JSON，声明唯一的 `kind: "accent"` 核心关系；没有品牌工具时不添加 Logo。
3. 运行 `scripts/prepare_prompt.py` 生成请求 JSON 与 `verification_checklist`：
   ```text
   python -X utf8 <skill目录>/scripts/prepare_prompt.py --content <本次内容.json> --layout editorial --out <本次请求.json> --image-path <交付图片的绝对路径.png>
   ```
4. 调用本地生图工具（如 Magpie Image MCP）按请求 JSON 生成 1 张图。
5. **强制逐字与结构验收**：打开成图，对照请求 JSON 里的 `verification_checklist` 逐项核对 `headline → summary → section.title → node.title → node.caption → connection.label`，重点排查窄栏折行叠字和形近错字；同时核查每条连线是否单线出口、终点准确、无交叉、满幅无外框投影。
6. 发现错字、错连或配色失衡时，最多针对具体缺陷自动定向返修 **2 次**；仍有复杂回环瑕疵时如实说明或建议拆图，绝不把带错字样张当成通过。
