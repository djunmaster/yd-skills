'use strict';
// 并行上传图片到 CloudFlare-ImgBed 图床。
// 用法：node scripts/imgbed_upload.js '{"folder":"knowledge-base/ai","items":[{"name":"a-01.jpg","url":"https://..."}]}'
// 参数：
//   folder   远端子目录（相对），会与 config.imgbed.folderPrefix 拼接
//   items[]  每项 { name, url } 或 { name, localPath }
//   authCode 可选，缺省取 config.imgbed.authCode
//   channel  可选，多通道时指定 uploadChannel
// 输出：{ok, endpoint, count, results:[{name, from, to, bytes, ok, error?}]}
const fs = require('fs');
const path = require('path');
const { getArgs, needFetch, run } = require('./lib');

const MIME = { jpg: 'image/jpeg', jpeg: 'image/jpeg', png: 'image/png', gif: 'image/gif', webp: 'image/webp', svg: 'image/svg+xml', avif: 'image/avif' };
const mimeOf = (name) => MIME[String(name).split('.').pop().toLowerCase()] || 'application/octet-stream';

run(async () => {
  const a = await getArgs();
  const ib = a.imgbed || {};
  const base = String(a.base || ib.base || '').replace(/\/+$/, '');
  const authCode = a.authCode !== undefined ? a.authCode : (ib.authCode || '');
  const prefix = ib.folderPrefix || '';
  const folder = a.folder || prefix;
  const items = a.items || [];
  if (!base) throw new Error('缺少图床地址（config.json 的 imgbed.base）');
  if (!Array.isArray(items) || !items.length) throw new Error('items 不能为空');

  const f = needFetch();

  const query = new URLSearchParams();
  query.set('returnFormat', 'full');   // 必须：否则 src 只有相对路径
  query.set('uploadNameType', 'origin'); // 用我们给的文件名，不加时间戳前缀
  if (folder) query.set('uploadFolder', folder);
  if (authCode) query.set('authCode', authCode);
  if (a.channel) query.set('uploadChannel', a.channel);
  const endpoint = base + '/upload?' + query.toString();

  // 单张上传；失败只影响自己
  const uploadOne = async (it) => {
    const name = String(it.name || '').trim();
    if (!name) return { name, ok: false, error: '缺少 name（文件名决定图床里的路径）' };
    try {
      let buf;
      let from = it.url || null;
      if (it.url) {
        const r = await f(it.url);
        if (!r.ok) return { name, from, ok: false, error: '源图下载失败 HTTP ' + r.status };
        buf = Buffer.from(await r.arrayBuffer());
      } else if (it.localPath) {
        const abs = path.isAbsolute(it.localPath) ? it.localPath : path.resolve(process.cwd(), it.localPath);
        buf = fs.readFileSync(abs);
        from = abs;
      } else {
        return { name, ok: false, error: '需要 url 或 localPath' };
      }

      const fd = new FormData();
      fd.append('file', new Blob([new Uint8Array(buf)], { type: mimeOf(name) }), name);
      const r = await f(endpoint, { method: 'POST', body: fd });
      const t = await r.text();
      let j = null;
      try { j = JSON.parse(t); } catch (e) { /* 非 JSON */ }
      const arr = Array.isArray(j) ? j : (j ? [j] : []);
      const src = arr.length && (arr[0].src || arr[0].url);
      if (!r.ok || !src) return { name, from, ok: false, error: 'HTTP ' + r.status + ' ' + t.slice(0, 200) };

      // 回读校验：能打开、是图片、字节数对得上
      let verified = { status: null, type: null, bytes: null, match: false };
      try {
        const v = await f(src, { method: 'GET' });
        const vb = Buffer.from(await v.arrayBuffer());
        verified = { status: v.status, type: v.headers.get('content-type'), bytes: vb.length, match: v.ok && vb.length === buf.length };
      } catch (e) {
        verified = { status: null, type: null, bytes: null, match: false, error: String(e.message || e) };
      }

      return { name, from, to: src, bytes: buf.length, ok: verified.match, verified };
    } catch (e) {
      return { name, ok: false, error: String((e && e.message) || e) };
    }
  };

  const results = await Promise.all(items.map(uploadOne)); // 并行
  return {
    ok: results.every((r) => r.ok),
    endpoint: base + '/upload' + (folder ? '?uploadFolder=' + folder : ''),
    count: results.length,
    results,
  };
});