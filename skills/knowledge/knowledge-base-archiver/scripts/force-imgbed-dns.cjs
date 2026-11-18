'use strict';
// 可选的 Node 预加载补丁：仅对自建图床域名生效（示例为 imgbed.example.com，请替换为你的自建图床域名）。
// 用途：若本机 DNS 返回被链路重置的 Cloudflare IP（或 IPv6），导致内置 fetch 报 ECONNRESET，
// 可通过此补丁把图床域名固定到可用的 Anycast IP（如 104.21.90.140），并对请求增加有限重试抵御间歇性 RST。
//
// 用法（不改任何技能脚本、不改系统 hosts）：
//   NODE_OPTIONS="--require <本文件绝对路径>" node scripts/imgbed_upload.js '<参数JSON>'
// 该补丁不改变 SNI 与 Host（仍是域名），因此证书校验正常。
const HOST = 'imgbed.example.com';
const IP = '104.21.90.140';

// 1) 固定 DNS 解析
const dns = require('node:dns');
const origLookup = dns.lookup;
dns.lookup = function (hostname, options, callback) {
  if (hostname === HOST) {
    if (typeof options === 'function') { callback = options; options = {}; }
    if (typeof callback === 'function') {
      const all = !!(options && options.all);
      process.nextTick(() => all
        ? callback(null, [{ address: IP, family: 4 }])
        : callback(null, IP, 4));
      return;
    }
  }
  return origLookup.apply(this, arguments);
};
try {
  const origPromises = dns.promises.lookup;
  dns.promises.lookup = function (hostname, options) {
    if (hostname === HOST) {
      return Promise.resolve(options && options.all
        ? [{ address: IP, family: 4 }]
        : { address: IP, family: 4 });
    }
    return origPromises.call(this, hostname, options);
  };
} catch (_) { /* 忽略：Node 版本差异 */ }

// 2) 对该域名加有限重试，抵御间歇性 RST
const origFetch = globalThis.fetch;
const sleep = (ms) => new Promise((r) => setTimeout(r, ms));
globalThis.fetch = async function (input, init) {
  const url = typeof input === 'string' ? input : (input && input.url) || '';
  const isTarget = typeof url === 'string' && url.includes(HOST);
  const attempts = isTarget ? 8 : 1;
  let lastErr;
  for (let i = 0; i < attempts; i++) {
    try { return await origFetch(input, init); }
    catch (e) {
      lastErr = e;
      if (i < attempts - 1) await sleep(120 * (i + 1));
    }
  }
  throw lastErr;
};
