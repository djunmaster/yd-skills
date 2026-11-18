# Layout Research

## 结论

复杂业务场景图不适合完全交给自动布局。最稳的方案是混合式：

1. AI 负责语义拆解、对象选择、视觉隐喻和美术方向。
2. 布局算法负责网格、端口、正交布线和交叉惩罚。
3. 浏览器几何审计负责验证真实渲染结果。
4. 并行子 Agent 负责独立图的批量生产。

Graphviz/ELK 适合“节点和边”关系，不适合要求场景化轮廓、目标框、经验带和长尾分布的深色技术插画。手写 SVG 更自由，但必须加几何契约和自动验收。

## 方案对比

| 方案 | 适合 | 优点 | 局限 |
|---|---|---|---|
| Graphviz `overlap` + `splines` | 普通流程图、依赖图 | 成熟的避重叠和曲线路由；`sep` 可扩大节点附近空间 | 风格偏通用；复杂边路由成本高；难以复刻定制场景图 |
| ELK Layered / Libavoid | 分层架构、端口固定、正交路由 | 支持端口约束、节点/边间距、交叉惩罚和正交布线 | 接入成本较高；对场景化视觉对象仍需二次绘制 |
| dagre / D3 | 轻量 DAG、树、简单层级 | 易嵌入浏览器，开发快 | 复杂避障、标签避让、任意形状支持有限 |
| 手写 SVG + Layout v1 + Playwright | 深色技术讲解、案例场景图 | 视觉可控，能画对象/空间/阈值/角色；可机器验收 | 需要严格执行网格、通道和 QA 契约 |

## 可用规则

### Graphviz

- `overlap=false` 通过迭代消除节点重叠。
- `splines=true` 用样条减少边穿过节点，但官方文档提示复杂度较高，不适合几十个以上节点的图。
- `sep` 以节点包围盒比例为节点与边保留间距。
- 适合作为“先算草图布局”的后端，不适合作为最终深色插画成品的唯一样式来源。

### ELK

- Layered 算法把节点分层，支持 straight/orthogonal/splines。
- 固定端口和任意端口约束可用于块图、角色图和数据管线。
- 可设置节点间距、层间边距、边边距、边节点间距。
- Libavoid 提供正交边路由、交叉惩罚、形状缓冲和端口方向偏好，适合作为高级路由参考。

### 浏览器几何

- `getBBox()` 读取 SVG 元素在用户坐标中的真实包围盒。
- `getScreenCTM()` 与实际渲染缩放结合，可把局部坐标统一映射回根 viewBox。
- `getPointAtLength()` 可对路径采样，用于检测穿框、穿文字、交叉和标签压线。
- Playwright 能输出 `boundingBox()`、截图、控制台错误，适合作为生成后的验收层。

## 推荐实现

### 1. 语义层

每张图只保留一个关系句，拆成节点、连线、标签和证据边界。不要让一个图同时解释五个独立结论。

### 2. 约束层

锁定 viewBox、24px 安全边距、16px 节点间距、8px 文字内边距、6px 连线净距和零交叉默认值。

### 3. 路由层

优先网格 + 手工正交通道。需要算法时，可只在局部使用 ELK/Libavoid 的路由思想；不要用自动布局替换案例场景中的人工视觉关系。

### 4. 审计层

用 `scripts/audit_svg_layout.py` 检查真实 DOM，而不是让模型“目测”。每个错误带修复建议；最多两轮修复，仍失败就拆图。

### 5. 并行层

Lead Agent 先冻结契约，再按图分派 Figure Worker。每张图一个文件、一个写入者、一个审计结果；Lead 只做合并和整页验收。

### 6. 页面层

除 SVG 内部几何外，还要检查 `.viz-scroll` 与图注、`figure` 与上下正文的距离。用户感受到的“图表和文字挨得太近”很多来自页面级间距，而不是图内坐标。

### 7. 加速边界

- 一图一目录并行、共享浏览器实例、每图独立 Page。
- 先几何 QA，通过后才截图，避免重复渲染。
- 以 `FigureSpec + grammarVersion + tokens` 做缓存键，未变化不重画。
- 4–6 个 Figure Worker 并行通常能缩短墙钟时间，但实际加速比取决于模型延迟、浏览器和机器资源，不能承诺线性加速。

## 参考来源

- Graphviz FAQ: https://graphviz.org/faq/
- Graphviz `splines` 属性: https://graphviz.org/docs/attrs/splines/
- Graphviz neato overlap 指南: https://graphviz.org/pdf/neatoguide.pdf
- ELK Layered: https://eclipse.dev/elk/reference/algorithms/org-eclipse-elk-layered.html
- ELK Libavoid: https://eclipse.dev/elk/reference/algorithms/org-eclipse-elk-alg-libavoid.html
- ELK spacing options: https://eclipse.dev/elk/reference/options/org-eclipse-elk-layered-spacing-edgeNodeBetweenLayers.html
- MDN `getBBox`: https://developer.mozilla.org/en-US/docs/Web/API/SVGGraphicsElement/getBBox
- MDN `getPointAtLength`: https://developer.mozilla.org/en-US/docs/Web/API/SVGGeometryElement/getPointAtLength
- Playwright Locator bounding box: https://playwright.dev/python/docs/api/class-locator#locator-bounding-box
- dagre: https://github.com/dagrejs/dagre/wiki
- D3 force collide: https://d3js.org/d3-force/collide
- libavoid: https://www.adaptagrams.org/documentation/libavoid.html

## 边界

- 几何审计只能证明“没有重叠/交叉/越界”，不能证明箭头语义一定正确。
- 自动布局不能自动决定业务上“谁应该连接谁”。
- 没有实测数值时仍只能画相对示意；布局精度不等于数据真实性。
- 复杂场景图若节点超过 7 个、连线超过 8 条，应优先拆图而不是增加自动路由复杂度。

