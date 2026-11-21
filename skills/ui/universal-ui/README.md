# Universal UI (v2.0)

把界面需求转成可落地的高审美方案：先调研该领域公认的标杆产品，再锁定一套克制色盘与信息密度，最后按硬规范实现并实测验收。保留目标项目的路由、导航、技术栈与真实数据，不复制演示页外壳，也不安装第二套组件库。

## v2.0 的变化

v1 用「36 个布局 × 56 个风格」做穷举式选择，选项多但收敛慢，也容易拼出四不像。v2.0 改为**一条收敛路径**：

1. **先调研标杆**：设计新领域界面前，先看该领域 2–3 个公认标杆（AI Agent 工作台看 Codex Desktop / Magpie / Pi，金融司库看 Mercury / Stripe，能源监控看 Tesla Energy / Vercel），只提炼外壳重量、视觉重心、灰阶冷暖与核心微交互，不做像素级复刻。
2. **再锁色盘**：从 **6 套克制色盘**中选一套，未锁定时给三个可区分候选（稳妥 / 偏好 / 特色），确认后锁定唯一主导色盘。
3. **正交叠加密度**：色盘与 **3 档密度**（`Airy` / `Balanced` / `Compact`）自由组合，与外观主题（浅/深）互不干扰。
4. **实测验收**：对照评分清单在 `1440 / 1024 / 390px` 与浅深双主题下打分，**≥ 85 分且未触发一票否决**才交付。

## 六套克制色盘

| 色盘 | 标杆参考 | 适用场景 |
| --- | --- | --- |
| `neutral-core` | Linear 浅色 | 通用 B 端后台、管理控制台 |
| `codex-matte` | Codex Desktop / Magpie / Pi | AI Agent 对话工作台、模型路由台 |
| `apple-clarity` | Apple HIG / Things 3 | 经营分析看板、个人健康与效率工具 |
| `mercury-emerald` | Mercury / Stripe / Ramp | 企业司库、财务对账、订阅计费 |
| `warm-editorial` | Notion / Craft / Bear | 知识库、长文阅读、研究报告 |
| `swiss-slate` | Vercel Observability / Tesla Energy | 工业 IoT、虚拟电厂、服务监控 |

## 三条硬规范

- **文字与排版**：7 级光学字阶（12.5 / 14 / 16 / 20 / 26 / 36px），大字收紧负字距，禁止 `< 12px` 元数据与 `Thin/Light` 细字重；所有数字与货币强制 `tabular-nums`。
- **控件精致度**：现代工作台禁止使用未样式化的原生 `<select>`，一律用自定义雾面 Popover，支持 `Escape` 关闭、清晰选中态与双行说明；按下不位移，键盘焦点可见。
- **色彩纪律**：页面 90% 以上保持中性画布与表面，强调色只用于主操作、焦点与关键数据序列；红色仅留给需要立即处理的异常或超限项，状态必须配合文字表达。

## 离线样例

- [Template Atlas](assets/template-atlas.html)：8 大高频布局骨架 + 标杆实景拆解
- [Palette Gallery](assets/palette-gallery.html)：6 套色盘 × 多领域样张
- [Component Kit](assets/component-kit.html)：基础组件标本库与黄金搭配
- [DataViz Kit](assets/dataviz-kit.html)：8 色盘 × 16 个精修可视化组件
- [Codex × Magpie 工作台](assets/codex-magpie-workbench.html)：纯中性雾面 AI Agent 工作台实景
- [司库 × VPP 遥测](assets/treasury-vpp-showcase.html)：企业司库与能源遥测两个标杆实景

`assets/tokens.css` 是设计令牌参考（字阶、间距、色彩语义），供对照取值，不要求引入。

## 使用

```text
使用 $universal-ui。做一个本地优先的 AI Agent 工作台：
左侧是任务列表，中央是消息与执行轨迹，右侧按需打开文件详情。
先给我三个布局方案，再实现我选择的那一个。
```

偏好读取优先级：**本次明确要求 > 当前项目 `DESIGN.md` > 全局 Profile（`~/.codex/design-profiles/universal-ui.md`）> 默认基线**。本 Skill 只读不写，沉淀偏好请用 `$ui-preference-ledger`。

## 边界

本 Skill 不生成业务数据、不接入真实接口、不改动宿主全局样式。演示数据必须明确标注；不允许把演示假能力包装成已接通能力。评分清单用于本次修改区块，需要浏览器实测，不接受仅凭静态读码给满分。
