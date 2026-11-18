# 把页面读全：按类型选路数

目标只有一个——**正文一层不漏**，包括散在评论/回复里的实质补充。下面按页面类型给做法；类型拿不准就先抓一遍 markdown 扫一眼再定。

| 页面类型 | 怎么读 |
| --- | --- |
| 博客 / 文档 / 新闻 | 正文抽取模式（reader mode）；正文长就落盘再分段读 |
| 列表 / 表格密集页 | markdown 模式，保结构 |
| 论坛贴（Discourse 系，如 linux.do） | 见下方「论坛懒加载抓取」，一次抓取只有开头 |
| GitHub 仓库 | 读渲染后的 README；需要逐字原文时打开 `.../blob/<branch>/README.md?plain=1` |
| PDF | 先看页数和目录再抽文本；抽出来是空的说明是扫描件，改成截图看 |
| 需要登录 / 折叠 / 展开才可见 | 先点开展开控件（"Show more"/"展开"）再读 |
| Canvas / 图片型内容 | 截图 + 视觉读取 |
| X（Twitter）长文 / Article | 见下方「X 长文」，**reader mode 会截断且丢外链** |

## 通用注意事项

- 页面上「展开阅读全文」「加载中」「Load more」「折叠内容」这类控件，不点就少一截内容。
- 代码块常带「复制」按钮文本，抽取后会粘连在代码尾部，整理时剔掉。
- 图片：**不要在文档里留站点外链**（`pbs.twimg.com`、论坛附件、各家 CDN 迟早 403）。整理正文时先把配图收集出来，走 ②.5 转存自建图床，见 `references/imgbed.md`；文档里用图床地址，文末附录留一份原图地址。头像/表情/徽章/二维码不收集、不转存。
- 评论区筛选：过滤「感谢分享」「插眼」「+1」这类寒暄，留下**路径纠正、版本兼容性问题、作者本人的后续更正、替代方案、失败案例**——这些是文档里最值钱的部分。
- 抓取时凡是可能返回大对象的，先截断（`.slice(0, N)`、每条 `text.slice(0, 300)`），别把整页 HTML 灌进上下文。

## 论坛懒加载抓取（Discourse / linux.do）

难点：Discourse 是**虚拟化 DOM**——只渲染视口附近约 3 个楼层，`querySelectorAll('.topic-post')` 一次拿不全；滚动（`scrollTo`）之后还要等它补渲染。所以必须「滚动 → 采集 → 去重」循环，并点几次「加载下方更多帖子」。

用浏览器的 JS 执行能力跑这段（已按 post 编号 + 用户 + 前缀去重）：

```js
const sleep = ms => new Promise(r => setTimeout(r, ms));
const map = new Map();
const harvest = () => document.querySelectorAll('.topic-post').forEach(p => {
  const cooked = p.querySelector('.cooked'); if (!cooked) return;
  const text = cooked.innerText.trim().replace(/\n+/g, ' | ');
  if (text.length < 25) return;                       // 剔掉寒暄短回复
  const user = p.querySelector('.username')?.textContent?.trim() || '?';
  const num  = p.querySelector('.post-number a')?.textContent?.trim() || '';
  map.set(num || (user + text.slice(0, 30)), { num, user, text: text.slice(0, 300) });
});
for (let round = 0; round < 8; round++) {
  const H = window.innerHeight;
  for (let y = 0; y < document.body.scrollHeight; y += Math.round(H * 0.45)) {
    window.scrollTo(0, y); await sleep(170); harvest();
  }
  const more = [...document.querySelectorAll('button,a')].find(e => /加载下方更多帖子/.test(e.textContent || ''));
  if (!more) break;
  more.scrollIntoView(); await sleep(300); more.click(); await sleep(1500); harvest();
}
return { count: map.size, items: Array.from(map.values()) };   // 注意是 Array.from(map.values())
```

配合一次整页 markdown 抽取（主楼 + 原帖配图 URL + 浏览量/标签等元信息从这里拿）。

坑：

- `Map` 取值要写 `Array.from(map.values())`，`[...map.values]`（漏括号）会报 not iterable。
- 楼层里的图片只有缩略图 URL，需要原图时从 `.cooked a[href]` 里挑 `original/` 路径那条。
- 「作者 xx 于 日期 发布」这类楼层壳文本不是内容，整理时丢掉；但里面的用户名和日期是有用的元信息，留到头部。
- 帖子有编辑历史时以当前正文为准；作者「后来更正」的回复要单独标注时间，别和首发正文混成一体。

## X（Twitter）长文 / Article

X 的长文（`x.com/<user>/status/<id>` 里的 Article，不是普通推文）有两个坑：

- reader mode **会在约 1.4 万字符处截断，并且吞掉引用外链和 @ 提及的链接目标**。别用 reader mode，直接抓 markdown 落盘（实测 2.2 万字节可全量拿到），再分段读。
- markdown 里图片形如 `![图像](https://pbs.twimg.com/media/<id>?format=jpg&name=900x900)`；按 URL 路径判断去留：`/media/` 是正文配图（收），`/profile_images/` 是头像、`/emoji/` 是表情（丢）。`?name=900x900` 只是尺寸参数。
- 各小节末尾的引用出处列表是文章最有长期价值的部分之一，必须逐条保留（作者名、标题、真实链接），别因为 reader mode 拿不到就略过——回到落盘的 markdown 里逐条抠。
- 主楼之后的回复/讨论区会跟在 markdown 尾部，按「评论区筛选」那条过滤寒暄，只留有信息量的。
- 作者、发布时间从页面头部读，不要凭推文 ID 反推时间；「首次发布」和「最近更新」分两个字段写。

## 读完之后自检

问自己三句，任一句答不上来就回去补读：

1. 正文的步骤/结论我是不是全拿到了（有没有截断在「展开更多」处）？
2. 代码、命令、路径、版本号是不是逐字符准确（不能靠脑补补全）？
3. 评论区有没有人指出正文的错（路径少了 `resources` 一层、某版本会挂）？这些必须进文档。