#!/usr/bin/env node

const fs = require("fs");
const path = require("path");
const { applyVizMinWidth } = require("./lib/viz_min_width");

function fail(message) {
  console.error(message);
  process.exit(1);
}

const [, , shellArg, runDirArg, outputArg] = process.argv;

if (!shellArg || !runDirArg || !outputArg) {
  fail("Usage: node assemble_story.js <shell.html> <run-dir> <body-out.html>");
}

const shellFile = path.resolve(shellArg);
const runDir = path.resolve(runDirArg);
const outputFile = path.resolve(outputArg);
const figuresDir = path.join(runDir, "figures");

const shell = fs.readFileSync(shellFile, "utf8");
const used = new Set();
const missing = [];

const assembled = shell.replace(/<!--\s*FIGURE:([a-z0-9][a-z0-9-]*)\s*-->/g, (_, id) => {
  const figureFile = path.join(figuresDir, id, "figure.html");
  if (!fs.existsSync(figureFile)) {
    missing.push(id);
    return `<!-- MISSING FIGURE:${id} -->`;
  }
  used.add(id);
  return fs.readFileSync(figureFile, "utf8").trim();
});

if (missing.length) {
  fail(`Missing figure files: ${missing.join(", ")}`);
}

if (!used.size) {
  fail("No <!-- FIGURE:id --> placeholders found in the shell.");
}

const manifestFile = path.join(runDir, "manifest.json");
const declared = new Set();
if (fs.existsSync(manifestFile)) {
  const manifest = JSON.parse(fs.readFileSync(manifestFile, "utf8"));
  const items = Array.isArray(manifest) ? manifest : manifest.figures || [];
  for (const item of items) {
    if (item && item.id) declared.add(item.id);
  }
}

const extras = declared.size
  ? [...declared].filter((id) => !used.has(id))
  : [];

if (extras.length) {
  fail(`Manifest figures not placed in the shell: ${extras.join(", ")}`);
}

fs.mkdirSync(path.dirname(outputFile), { recursive: true });
fs.writeFileSync(outputFile, applyVizMinWidth(assembled), "utf8");
console.log(`Assembled ${used.size} figures into ${outputFile}`);
