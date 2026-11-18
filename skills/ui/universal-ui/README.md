# Universal UI

把用户需求转成可实现的界面方案：从五个整页模板取用局部组件，或通过 36 个布局方案与 56 个克制风格推导新页面。保留目标项目的导航、技术栈和真实数据，不复制产品外壳，也不安装组件包。

## 能力

- **局部复用**：从收入分析、服务监控、模型网关、客户管理和订阅分析模板中只取一个区块。
- **新页面设计**：按任务推导信息架构，从 12 类页面布局中选择结构。
- **风格选择**：用 Style Atlas 比较 56 个克制风格，再压缩为三个候选。
- **参考型转译**：学习 Codex、Notion、Magpie 等产品的布局与交互逻辑，不做品牌像素复刻。

## 离线样例

- [Style Atlas](assets/style-atlas.html)：56 个风格样张
- [Layout Atlas](assets/layout-atlas.html)：12 类页面 × 3 个布局方案
- [收入分析](assets/analytics.html)
- [服务监控](assets/monitoring.html)
- [模型网关](assets/gateway.html)
- [客户管理](assets/crm.html)
- [订阅分析](assets/saas.html)

## 使用

```text
使用 $universal-ui。做一个本地优先的 AI Agent 工作台：
左侧是任务列表，中央是消息与执行轨迹，右侧按需打开文件详情。
先给我三个布局方案，再实现我选择的那一个。
```

偏好读取顺序：本次明确要求 > 当前项目 `DESIGN.md` > 全局 UI Profile > Neutral Core 默认规则。
