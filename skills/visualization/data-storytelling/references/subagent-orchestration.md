# Subagent Orchestration

## 何时启用

- 快速路径：1–3 张图、单段文本，主 Agent 顺序完成。
- 并行路径：4 张以上图、完整 HTML 页面、多个案例或多个独立章节。
- 不要在视觉契约尚未确定时启动绘图 Agent；否则每个 Agent 会发明一套间距和风格。

## 角色与写入边界

| 角色 | 责任 | 写入范围 |
|---|---|---|
| Lead Agent | 提炼信息单元、冻结视觉契约、页面骨架、最终集成 | 全局 CSS、shell、清单、最终输出 |
| Figure Worker | 只负责一张图或一个视觉单元 | `runs/<run-id>/figures/<visual-id>/` |
| Geometry Auditor | 运行浏览器几何审计，返回 JSON 与截图 | 只读，不写 SVG |
| Repair Worker | 只修失败图 | 只改对应 `figures/<visual-id>.html` |
| Content Auditor | 对照原文复核语义、物体结构、曲线/区域与标签映射、规则来源及可读性 | 只读报告 |

两个 Agent 不得同时修改同一个 HTML、CSS 或图段。Lead Agent 负责合并，Figure Worker 不得改全局配色和页面结构。

## 冻结契约

启动并行前，Lead Agent 必须一次性确定：

1. **整页逻辑主线与章节承接**：先冻结整页的 `1 → 2 → 3 → 4 → 5 → 6`（按实际章数）因果递进主线（`.story-roadmap`）、每章的承上启下过渡（`.section-bridge` / `.next-bridge`），以及每章内部的 `1、2、3、4、5、6` 分点逻辑大纲（`.logic-points`）。不要把页面规划成一堆互不关联的孤立小图卡片墙。
2. 深色/浅色风格、画布分级宽度（主视觉画面推荐 `920×420`～`960×460`，局部特写推荐 `560×300`～`680×340`）、颜色变量、字体层级。
3. 节点最小间距、文字内边距、连线通道、编号锚点（`data-callout-badge`）与特征引线（`data-callout-leader`）规则。
4. 每张图的**视觉画面方案**（`visualMode` + `visualScene`：选什么具象界面、物理场景或视觉隐喻，必须画出哪些非方框视觉道具，如何通过**去字可辨检验**）以及与图外分点对应的编号锚点清单（`callouts`: `1, 2, 3, 4, 5, 6`）。
5. 每张图的原文片段及定位、规则来源、参考依据与未知点；区分独立核验事实、课程业务简化和示意，不能只传改写后的结论。
   Lead 自行设计的教学记录应明确标为“讲解示例”；Worker 收到 Lead 的任务简报不等于真实用户或原文提供了该记录，禁止在 `evidence` 或 `data-visual-source` 中错误归因。
6. 每张图的视觉焦点、阅读顺序、关键提示和注意事项；不要退化成“几个矩形文字框 + 直线箭头”的框线图，也不要把大段说明塞进 SVG。
7. 涉及曲线时的轴定义、尺度与已知分类映射；涉及现实对象时的朝向、铰链和连接点参考。缺失规则保留待补，不由 Worker 补造。

契约示例：

```json
{
  "theme": "dark",
  "featureViewBox": "0 0 920 420",
  "detailViewBox": "0 0 640 340",
  "nodeGap": 16,
  "textPadding": 8,
  "linkNodeClearance": 6,
  "linkGap": 8,
  "laneGrid": 4,
  "calloutBadgeRadius": 14,
  "requireTextRemovalPass": true
}
```

每张图先输出 `FigureSpec`（必填 `visualMode`、`visualScene` 与 `callouts`），再渲染 SVG。不要让 Figure Worker 直接从散文跳到方框坐标。在 `evidence` 字段记录来源片段、定位和参考，在 `boundary`/`caution` 中记录候选、示意及规则缺口；这些内容也要随任务传给 Auditor。最小格式见 `references/figure-spec.schema.json`：

```json
{
  "id": "double-blind-workbench",
  "claim": "双盲隔断让两名专家独立判定同一工单，冲突自动触发第三方仲裁与规范修订",
  "visualType": "metaphor-mechanism",
  "visualMode": "metaphor",
  "visualScene": {
    "metaphor": "物理隔断双盲工作台 + 印章冲突指示灯 + 仲裁规范台",
    "stageLayout": "上方待审样本托盘，中层左右两间工位被橙色斜纹隔断墙分开，下方冲突检测灯连向摊开的规范书",
    "visualProps": ["深色舞台点阵底", "带折角工单文档与AI候选胶囊", "橙色斜纹不可互见隔断墙", "左右专家头像与不同色判定印章", "冲突警报灯与摊开的规范书"],
    "focalHighlight": "中间的橙色斜纹双盲隔断墙与下方冲突触发器",
    "textRemovalCheck": "抹去文字后仍可一眼看出顶部一份文档分送左右两个被墙隔开的工位、盖下不同颜色印章并在底部汇入冲突仲裁台"
  },
  "callouts": [
    {"number": 1, "target": "顶部待审工单与AI候选徽章", "label": "AI先提候选", "tone": "blue"},
    {"number": 2, "target": "中间斜纹隔断墙", "label": "物理双盲隔离", "tone": "orange"},
    {"number": 3, "target": "左侧专家A工位与蓝色印章", "label": "独立判定A", "tone": "blue"},
    {"number": 4, "target": "右侧专家B工位与橙色印章", "label": "独立判定B", "tone": "orange"},
    {"number": 5, "target": "底部冲突触发指示器", "label": "暴露分歧单", "tone": "red"},
    {"number": 6, "target": "右侧摊开的标注规范书", "label": "仲裁并补规范", "tone": "green"}
  ],
  "focus": "用物理隔断避免互相抄答案，把分歧沉淀成规范",
  "sequence": ["AI提候选", "隔断盲审", "对比印章", "暴露分歧", "第三方仲裁", "修订规范"],
  "callout": "专家只处理分歧与证据，不重复录入",
  "caution": "AI 候选不能跳过复核直接成为训练真值",
  "entities": [
    {"id": "sample-tray", "label": "待审工单托盘", "role": "producer"},
    {"id": "booth-a", "label": "专家 A 工位", "role": "reviewer"},
    {"id": "booth-b", "label": "专家 B 工位", "role": "reviewer"},
    {"id": "arbiter-desk", "label": "仲裁与规范台", "role": "resolver"}
  ],
  "constraints": {
    "direction": "top-to-bottom",
    "minNodeGap": 20,
    "textPadding": 10,
    "minLinkGap": 12,
    "allowEdgeCrossing": false
  }
}
```

## 并行生产流程

1. Lead 建立 `visual-manifest.json`：每项含 `id`、标题、关系句、输入对象、输出判断、证据边界；每图任务附上冻结契约中的原文及参考。
   判断表和执行清单应登记到每个条目，案例应登记到独立关系；不能把一整张文字清单当成一个已覆盖单元。用 `data-required-visuals` 将分组的条目清单带到页面，分别记录结构覆盖和解释是否有效。
2. 为每张图生成 `FigureSpec`，并复制固定 figure shell，保留唯一 id 和 `data-layout-contract="v1"`。
3. 同时派出 4–6 个 Figure Worker；每张图独立输出到 `runs/<run-id>/figures/<id>/figure.html`。
4. Worker 按语义与证据门槛自检，再核对独立对象的 `data-node`、连线的 `data-link/from/to` 和标签的 `data-for`。
5. Geometry Auditor 运行 `audit_svg_layout.py --strict`，Content Auditor 按下方提示独立复核语义和可读性；失败项回到同一 Worker 修复。
6. Lead 合并几何、语义、可读性均通过的片段，运行整页审计、移动端和内容边界检查；规则待补仍须披露。

Shell 中每个位置只放一个占位符：

```html
<!-- FIGURE:case3-double-blind -->
```

然后由脚本按 manifest 和目录结构组装，避免人工复制导致漏图或顺序错乱：

```powershell
node scripts/assemble_story.js runs/<run-id>/shell.html runs/<run-id> `
  runs/<run-id>/body.html
node scripts/build_recap.js runs/<run-id>/body.html final/index.html `
  "页面标题" dark
```

推荐运行目录：

```text
runs/<run-id>/
  manifest.json
  tokens.json
  grammar/
  figures/
    F01/
      brief.json
      spec.json
      figure.html
      qa.json
      screenshot.png
    F02/
      ...
  final/
    index.html
```

只有 Lead 可以写 `manifest.json`、`tokens.json` 和 `final/index.html`。Figure Worker 只拥有自己的目录。

## Figure Worker 提示模板

```text
你只负责 visual-id=<id> 的一张可视化 SVG 图画。
视觉模式：data-visual-mode=<interface|scene|metaphor|mechanism|before-after|cutaway|chart>
画面隐喻/界面方案：<用什么具体视觉界面、物理场景或机制机关呈现，而非普通框线图>
关系句：<一句核心判断>
原文与参考：<本图相关原文片段、行号/位置、图像或结构参考>
规则与缺口：<已给定判别条件及来源；业务简化；待定义条件>
视觉焦点：<读者第一眼应该看见的画面中心或对比>
编号锚点清单（与图外 1、2、3、4、5、6 分点说明一一对应）：<1:... 2:... 3:... 4:... 5:... 6:...>
注意事项：<风险、边界或不能误读的地方>

绘图前必读 references/visual-svg-cookbook.md 与 references/svg-layout-protocol.md：
1. 先输出符合 references/figure-spec.schema.json 的 spec.json（含 visualMode、visualScene 与 callouts），再生成 SVG。
2. 严禁退化成“几个矩形文字框 + 箭头”的框线图！必须通过“去字可辨检验”：把全部中文抹掉后，画面仍能一眼辨认出具体的界面形态、物理结构、视觉隐喻或前后状态对比。
3. 画面占 60%–75%，文字标注占 25%–40%；长解释留给图外 1、2、3、4、5、6 分点说明，不往方框里塞多行大段文字。
4. 使用深色技术讲解四层质感：Layer 0 低对比舞台背景（data-backdrop="true" 或 <pattern>），Layer 1 具象界面/物件表面，Layer 2 语义高亮/斜纹/空槽/挂锁/放大镜，Layer 3 圆形编号锚点（data-callout-badge="1..6" + data-badge-shape="true"）和精准特征引线（data-callout-leader="1..6"，不加 data-link，严禁压字）。
5. 严格遵守“语义与证据门槛”：检测框相交只作定位候选，不宣称真实物理接通；曲线明确轴和尺度，缺失规则不自造阈值或三色波形；现实物体按参考核对朝向和结构，教学示例明确标明身份。
6. 使用固定 viewBox <width>x<height>（主视觉画面推荐 920x420～960x460）和布局契约 v1：独立容器放 <g data-node="...">，关系连线用 data-link/data-from/data-to，节点间距 >=16，文字内边距 >=8，核心文字 >=14px。
7. 只输出 runs/<run-id>/figures/<id>/ 下的文件，不修改全局 CSS、页面或其他图。
8. 完成后报告：视觉隐喻说明、去字可辨自检、编号锚点清单（1–6）、证据边界，以及几何/语义/可视化可读性自检结果。
```

## Auditor 提示模板

```text
你只读审核 visual-id=<id>（或整页逻辑与视觉质量），不修改 SVG。
输入：<相关原文片段及定位、参考、FigureSpec、图段/页面 HTML、几何报告与渲染截图>。
分别报告 geometry、visual_craft（去框线图检验）、logic_coherence（1–6 分点与承上启下）、semantics、readability 的 PASS/FAIL/UNVERIFIED、依据及待补项；缺少相应证据时不得默认通过。
Geometry Auditor 运行 audit_svg_layout.py --strict；Content Auditor 对照原文和截图独立检查：
1. 【去字可辨检验】抹掉全部文字后，是否能看出具象界面、物体、视觉隐喻或前后对比？如果退化成均匀圆角矩形 + 箭头（或触发 VISUAL_TOO_SCHEMATIC），直接判 FAIL 退回重画。
2. 【逻辑连贯与编号联动】图内 data-callout-badge（1–6）是否按自然阅读顺序分布，并与图外 .logic-points 的 1、2、3、4、5、6 分点说明一一对应？页面章节之间是否有承上启下的逻辑主线，而非孤立卡片堆叠？
3. 【语义与证据边界】唯一关系和结论是否有来源；业务简化、已验证事实、教学示意和待定义条件是否分清。
4. 【对象与空间边界】检测框是否定位原文定义的对象；框相交/可见接触是否被误写成真实物理/电气接通；物体朝向、外形、铰链和连接点是否合理。
5. 【曲线与规则边界】曲线轴、单位、方向和尺度是否明确；是否自造阈值、持续时长或未给定映射的三色波形。
6. 【几何与可读性】核心文字 >=14px，无文字重叠、描边穿字、锚点越界或箭头悬空；按实际渲染截图确认阅读顺序清晰。
任一项失败应说明具体对象、来源位置和返修原因；几何 PASS 不能替代视觉质量、逻辑连贯性、语义正确性与可读性。
```

## 加速策略

- 先规划后并行：语义拆解只做一次，避免每个 Agent 重读全文。
- 图与图并行，图内串行：一张图内部的节点、通道、标签必须依次确定。
- 只跑两轮几何修复：第一轮修重叠/越界，第二轮修连线/标签；仍失败就拆图。
- 共享视觉原语和固定坐标网格，减少每个 Worker 重新设计布局。
- 统一在最后做一次浏览器整页验收，而不是每改一个文字就重跑整页。
- 每张图只保留一个关系主图；复杂内容拆成多图比在一张图里挤更稳定、更快。
- 所有图共用一个浏览器实例，每张图使用独立 Page；只在通过几何审计后截图。
- 用 `hash(原文片段 + FigureSpec + 语义/布局协议内容 + grammarVersion + tokens)` 缓存结果；语义规则变化后重新复核，不能直接复用旧 `PASS`。
- 常见结构优先走模板车道（流水线、问题→动作→结果、阈值、长尾、角色闭环、版本、矩阵）；只有空间场景走定制车道。

## 验收门槛

- 每个契约图的几何结果：`PASS`，不得有 `error`；语义和可读性另行通过，不能由几何结果代替。
- 整页：无横向溢出、无控制台错误、移动端无裁切；图示与图注间隔 >=12px，图与相邻正文间隔 >=16px。
- 视觉：截图检查箭头方向、文字可读性和语义连接。
- 内容：每个数字和判别条件有来源；课程/访谈陈述及业务简化保留证据边界，缺失规则标为待补，不能把候选或示意写成已证实结论。
- 自动审计、截图或语义复核任一失败都回修并重检，记录原因；人工观感不能豁免几何失败，几何 `PASS` 也不能豁免语义或可读性失败。

