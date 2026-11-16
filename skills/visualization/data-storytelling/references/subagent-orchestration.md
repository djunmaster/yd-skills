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

1. 页面主题、章节顺序和每张图的 `visual-id`。
2. 深色/浅色风格、viewBox 宽度、颜色变量、字体层级。
3. 节点最小间距、文字内边距、连线通道和标签规则。
4. 每张图只回答的一个关系句。
5. 每张图的原文片段及定位、规则来源、参考依据与未知点；区分独立核验事实、课程业务简化和示意，不能只传改写后的结论。
   Lead 自行设计的教学记录应明确标为“讲解示例”；Worker 收到 Lead 的任务简报不等于真实用户或原文提供了该记录，禁止在 `evidence` 或 `data-visual-source` 中错误归因。
6. 每张图的视觉焦点、阅读顺序、关键提示和注意事项；场景、规则、步骤、结果不得在一张图里混成一张大图。
7. 涉及曲线时的轴定义、尺度与已知分类映射；涉及现实对象时的朝向、铰链和连接点参考。缺失规则保留待补，不由 Worker 补造。

契约示例：

```json
{
  "theme": "dark",
  "viewBoxWidth": 1100,
  "nodeGap": 16,
  "textPadding": 8,
  "linkNodeClearance": 6,
  "linkGap": 8,
  "laneGrid": 4,
  "maxNodesPerFigure": 7,
  "maxLinksPerFigure": 8
}
```

每张图先输出 `FigureSpec`，再渲染 SVG。不要让 Figure Worker 直接从散文跳到坐标。在已有 `evidence` 字段记录来源片段、定位和参考，在 `boundary`/`caution` 中记录候选、示意及规则缺口；这些内容也要随任务传给 Auditor。最小格式见 `references/figure-spec.schema.json`：

```json
{
  "id": "case3-double-blind",
  "claim": "AI 预标注把专家从重复劳动转为分歧复核",
  "visualType": "role-loop",
  "focus": "AI 预标注后由两名专家独立复核",
  "sequence": ["候选生成", "独立复核", "分歧仲裁"],
  "callout": "专家处理分歧，不重复画框",
  "caution": "AI 候选不能直接作为最终标签",
  "entities": [
    {"id": "ai", "label": "AI 预标注", "role": "producer"},
    {"id": "expert-a", "label": "专家 A", "role": "reviewer"},
    {"id": "expert-b", "label": "专家 B", "role": "reviewer"},
    {"id": "arbiter", "label": "第三方仲裁", "role": "resolver"}
  ],
  "relations": [
    {"from": "ai", "to": "expert-a", "label": "候选标注"},
    {"from": "ai", "to": "expert-b", "label": "候选标注"},
    {"from": "expert-a", "to": "arbiter", "label": "分歧"},
    {"from": "expert-b", "to": "arbiter", "label": "分歧"}
  ],
  "constraints": {
    "direction": "left-to-right",
    "minNodeGap": 24,
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
你只负责 visual-id=<id> 的一张图。
关系句：<一句唯一关系>
原文与参考：<本图相关原文片段、行号/位置、图像或结构参考>
规则与缺口：<已给定判别条件及来源；课程业务简化；待定义条件>
视觉焦点：<读者首先应该看见的对象或结论>
阅读顺序：<01 → 02 → 03，最多四步>
关键提示：<需要加粗显示的一句话>
注意事项：<风险、边界或不能误读的地方>
必须出现：<对象/阈值/角色/输入输出>
先输出符合 references/figure-spec.schema.json 的 spec.json，再生成 SVG。
用 evidence 保存上述来源，用 boundary/caution 说明候选、示意和未证实结论。
按 references/svg-layout-protocol.md 的“语义与证据门槛”绘图：
检测框相交只作定位候选，可见接触不能证明电气接通或合规接地；保留原文业务规则的身份。
曲线明确轴和尺度；已有类别映射要直接绑定对应可见曲线/区域，规则缺失时只画事实、待补专家规则和等级输出，不补造阈值或时长，也不强配三色波形。
现实物体按参考核对外形、朝向、铰链、开合及连接点；结构示意不作现场证据。
使用固定 viewBox <width>x<height>、深色技术讲解风格和布局契约 v1。
每个独立对象分别放在 <g data-node="..."> 内，不把整图合成单一节点逃避扫描；连线必须有 data-link/data-from/data-to；
标签必须有 data-link-label/data-for。节点间距 >=16，文字内边距 >=8，
默认零连线交叉，路径仅走水平/垂直通道。
关键对象框和主路径使用较粗线宽，辅助线变细；主标签使用 700–800 字重。
如果输入同时要求场景、规则和执行步骤，先拆成多个 visual-id，不要在这一张图中补齐全部内容。
只输出 runs/<run-id>/figures/<id>/ 下的文件，不修改全局 CSS、页面或其他图。
完成后列出节点 id、连线 id、证据边界和潜在不确定点；分别报告几何、语义与可读性自检，几何 PASS 不能代替另两项。
```

## Auditor 提示模板

```text
你只读审核 visual-id=<id>，不修改 SVG。
输入：<相关原文片段及定位、参考、FigureSpec、图段、几何报告与渲染截图>。
分别报告 geometry、semantics、readability 的 PASS/FAIL/UNVERIFIED、依据及待补项；缺少相应证据时不得默认通过。
Geometry Auditor 运行 audit_svg_layout.py --strict；Content Auditor 对照原文和截图独立检查下列语义及可读性门槛：
1. 唯一关系和结论是否有来源；原文业务简化、已验证事实、示意和待定义条件是否分清。
2. 检测框是否定位原文定义的对象；框相交/可见接触是否被误写成真实电气接通或合规接地。
3. 曲线的轴、单位、方向和比较尺度是否明确；声称的类别能否直接找到对应可见曲线/区域；是否自造阈值、持续时长或波形分级。
   若原文只给等级含义，应保留“曲线事实 → 独立专家规则（待补）→ 等级输出”，无需强配三色曲线。
4. 物体前后朝向、外形、铰链、开合及连接点是否合理且有参考；示意是否被当成现场证据。
5. 独立对象是否各有 data-node，标签是否归属于对象或绑定连线；每条关系箭头是否绑定有效的源/目标节点，箭头尖端是否接到其边界；是否用整图单一节点隐藏重叠或漏扫。旧图基础扫描不验证端点，修改关系箭头后需升级为 v1。
6. 按实际渲染尺寸检查对象、标签与阅读顺序能否辨认；加粗或几何 PASS 都不能替代语义正确性与可读性。
任一项失败应说明具体对象、来源位置和返修原因；任何一项未验证都不能由几何 PASS 覆盖。
清楚披露的规则待补可作为表达边界保留，但不算规则已验证，也不得给示意曲线作实际判级。
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

