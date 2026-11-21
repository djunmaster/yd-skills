#!/usr/bin/env node

const fs = require("fs");
const path = require("path");
const { applyVizMinWidth } = require("./lib/viz_min_width");

const skillDir = path.resolve(__dirname, "..");
const assets = path.join(skillDir, "assets");

function read(file) {
  return fs.readFileSync(file, "utf8");
}

function build(bodyFile, outputFile, title, theme) {
  const body = applyVizMinWidth(read(bodyFile)).replace(/<figure\b(?:[^>"']|"[^"]*"|'[^']*')*>/g, (openingTag) => {
    const visualId = openingTag.match(/\sdata-visual-id="([a-z0-9-]+)"/);
    if (!visualId || /\sid\s*=/.test(openingTag)) return openingTag;
    return openingTag.replace(/>$/, ` id="${visualId[1]}">`);
  });
  const cssFiles = theme === "dark"
    ? ["dark-story.css"]
    : ["qq-style.css", "qq-extra.css", "qq-responsive.css"];
  const css = cssFiles
    .map((file) => `<style>\n${read(path.join(assets, file))}\n</style>`)
    .join("\n");

  const html = `<!doctype html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>${title}</title>
<link rel="icon" href="data:,">
${css}
</head>
<body>
${body}
</body>
</html>
`;

  fs.mkdirSync(path.dirname(outputFile), { recursive: true });
  fs.writeFileSync(outputFile, html, "utf8");
  const size = Buffer.byteLength(html, "utf8");
  console.log(`Built ${outputFile} (${size} bytes)`);
}

const [, , bodyArg, outputArg, titleArg, themeArg] = process.argv;

if (!bodyArg || !outputArg) {
  console.error("Usage: node build_recap.js <body.html> <output.html> [title] [light|dark]");
  process.exit(1);
}

build(
  path.resolve(bodyArg),
  path.resolve(outputArg),
  titleArg || "大模型微调与数据建设方法论",
  (themeArg || "light").toLowerCase()
);
