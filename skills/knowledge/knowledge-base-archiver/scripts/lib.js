'use strict';
// 共用工具：读配置、解析参数、统一输出。四个脚本都 require 这个文件。
const fs = require('fs');
const path = require('path');

const SKILL_ROOT = path.resolve(__dirname, '..');

function loadConfig() {
  const p = path.join(SKILL_ROOT, 'config.json');
  try {
    return JSON.parse(fs.readFileSync(p, 'utf8'));
  } catch (e) {
    if (e.code === 'ENOENT') throw new Error('找不到配置文件：' + p + '（可从 config.example.json 复制一份）');
    throw new Error('config.json 解析失败：' + e.message);
  }
}

function readStdin() {
  if (process.stdin.isTTY) return Promise.resolve('');
  return new Promise((resolve) => {
    let buf = '';
    let settled = false;
    const done = () => { if (!settled) { settled = true; resolve(buf.trim()); } };
    process.stdin.setEncoding('utf8');
    process.stdin.on('data', (c) => { buf += c; });
    process.stdin.on('end', done);
    process.stdin.on('error', done);
    const t = setTimeout(done, 3000);
    if (t.unref) t.unref();
  });
}

// 参数来源优先级：命令行 JSON > stdin JSON > config.json
async function getArgs() {
  const raw = process.argv[2];
  let inline = {};
  if (raw) {
    try { inline = JSON.parse(raw); } catch (e) { throw new Error('第 1 个参数不是合法 JSON：' + e.message); }
  } else {
    const s = await readStdin();
    if (s) {
      try { inline = JSON.parse(s); } catch (e) { throw new Error('stdin 不是合法 JSON：' + e.message); }
    }
  }
  const cfg = loadConfig();
  const merged = Object.assign({}, cfg, inline);
  merged.imgbed = Object.assign({}, cfg.imgbed || {}, inline.imgbed || {});
  return merged;
}

function needFetch() {
  if (typeof fetch !== 'function') {
    throw new Error('需要 Node.js 18 或更高版本（内置 fetch/FormData/Blob）。当前 ' + process.version + '，请升级 Node。');
  }
  return fetch;
}

function emit(obj) {
  process.stdout.write(JSON.stringify(obj, null, 2) + '\n');
}

// 统一入口：成功走 emit，异常也转成 JSON 输出，退出码非 0
function run(fn) {
  Promise.resolve()
    .then(fn)
    .then((r) => { emit(r === undefined ? { ok: true } : r); })
    .catch((e) => { emit({ ok: false, error: String((e && e.message) || e) }); process.exitCode = 1; });
}

const b64ToText = (s) => Buffer.from(String(s).replace(/\s/g, ''), 'base64').toString('utf8');
const textToB64 = (s) => Buffer.from(String(s), 'utf8').toString('base64');

// 中文/空格路径：逐段编码，别整串 encodeURI（会漏掉 # 等）
const encPath = (p) => String(p).split('/').map(encodeURIComponent).join('/');

module.exports = { SKILL_ROOT, loadConfig, getArgs, needFetch, emit, run, b64ToText, textToB64, encPath };