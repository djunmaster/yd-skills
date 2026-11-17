# 图片转存到自建图床（CloudFlare-ImgBed）

**为什么必须做**：文档里留 `pbs.twimg.com`、论坛附件、各家 CDN 的直链，过几个月就会 403/404（X 的图片要尺寸签名参数，linux.do 附件要登录），私有仓库里的图等于没存。凡是归档带图的文章，图片一律先转存到自己图床，再把 md 里的链接换掉。

**图床实例**：<https://<你的图床域名>/> ｜ 程序：[CloudFlare-ImgBed](https://github.com/MarSeventh/CloudFlare-ImgBed) ｜ API 文档：<https://cfbed.sanyue.de/en/api/upload.html>

## 上传接口（官方文档 + 实测）

- `POST /upload`，`multipart/form-data`，文件字段名固定为 **`file`**
- 鉴权：`authCode` 走 **query 参数**，或 `Authorization: Bearer <API Token>`（token 需 `upload` 权限）。
  → authCode 用 query 而不是自定义 header，可以避免 preflight 请求。
  → 这台实例目前**没设上传码**，不带 authCode 也能传（`config.json` 的 `imgbed.authCode` 留空即可；将来设了码填进去就会自动带上）。
- 常用 query 参数：

| 参数 | 值 | 说明 |
| --- | --- | --- |
| `returnFormat` | `full` | **一定要带**，否则 `src` 只有 `/file/xxx` 相对路径 |
| `uploadFolder` | `knowledge-base/ai` | 远端子目录，相对路径 |
| `uploadNameType` | `origin` | 用我们指定的文件名（`default` 会加时间戳前缀，`short` 是短链） |
| `responseFormat` | `object` | 单文件时返回对象而不是数组；不带就是数组 |
| `uploadChannel` | `telegram`/`cfr2`/`s3`/... | 多通道时才需要，默认走管理员配的通道 |
| `expire` | `7d` / `forever` | 只有管理员开了文件过期才生效 |

- 成功响应：`[{"src":"https://<你的图床域名>/file/<folder>/<name>"}]`
- 体积上限：Pages 部署单次请求 100MB；Telegram 通道单文件 20MB。图片场景基本碰不到。

## 怎么做

1. 从页面里把**正文配图**的 URL 收集出来（markdown 里的 `![..](..)`，或直接读图片元素的 `src`）。
2. 并行转存 —— `scripts/imgbed_upload.js` 内部是 `Promise.all`，一张失败不影响其它张：

```bash
node scripts/imgbed_upload.js '{
  "folder": "knowledge-base/ai",
  "items": [
    {"name": "addyosmani-critical-thinking-01.jpg", "url": "https://pbs.twimg.com/media/HV7huCLbAAAiKaV?format=jpg&name=900x900"},
    {"name": "addyosmani-critical-thinking-02.png", "url": "https://pbs.twimg.com/media/HWLT4glawAA6egZ?format=png&name=900x900"}
  ]
}'
# → {"ok":true,"results":[{"name":"...","from":"https://...","to":"https://.../file/...","bytes":20387,"ok":true}]}
```

3. 用返回的 `to` 替换文档里的原图链接。
4. **回读校验**：脚本对每张转存后的 URL 会自动 `GET` 一次，确认 `status 200` + `content-type` 是 `image/*` + 字节数与上传时一致（结果在 `verified` 字段）。校验不过就保留原链，并在文档里注明「图床转存失败」，不要交一个点不开的图。

### 命名约定

- `<作者或主题>-<序号>.<真实扩展名>`，全小写、连字符，例：`addyosmani-critical-thinking-01.jpg`
- **不要把中文塞进图片 URL 路径**（标题用中文没问题，图片链接用中文会踩编码坑）
- 目录与仓库分类对齐：`uploadFolder=knowledge-base/<分类>` ↔ 仓库 `docs/<分类>/`
- 扩展名按源站 `content-type` 给（twimg 的 `?format=png` 就存 .png）

### 哪些图该转，哪些不该

| 转 | 不转 |
| --- | --- |
| 步骤截图、效果图、报错截图、架构图、配置截图（GIF 长图也转） | 头像、表情图、徽章、二维码、广告/推荐位图、装饰性分隔图 |

判断标准：**这张图没了，读者还能不能照着做**。能 → 不转；不能 → 转。

原图地址在文档文末附录留一份，方便日后回溯来源。

## 删除（需要带 `delete` 权限的 API Token）

- 单文件：`GET /api/manage/delete/{path}`，`path` 是文件 ID（`knowledge-base/ai/x.jpg`，不带域名）
- 批量：`POST /api/manage/delete/batch`，body `{"fileIds":["a.jpg","b.png"]}`
- 目录：`GET /api/manage/delete/{path}?folder=true`
- 鉴权是 `Authorization: Bearer <token>`。**匿名能上传，但删除必须要 token** —— 所以别把测试垃圾文件传上云，探测连通性时优先用 `GET /` 或传到 `uploadFolder=__probe` 再删。
