const families = [
  {
    id: 'neutral',
    label: 'Neutral Core',
    base: {
      layout: 'dashboard',
      density: 'medium',
      radius: '8px',
      shadow: 'soft',
      surface: 'var(--surface)',
      canvas: 'var(--canvas)',
      font: 'var(--font-ui)',
      use: '稳定后台',
      avoid: '炫技装饰',
      tags: 'internal · data · tools'
    },
    variants: [
      { name: 'Graphite', source: 'Current Universal UI', primary: '--chart-1', secondary: '--chart-2', tertiary: '--accent' },
      { name: 'Slate', source: 'UI UX Pro Max · Clean Minimal', primary: '--chart-5', secondary: '--chart-1', tertiary: '--accent' },
      { name: 'Stone', source: 'Hallmark · Studio', primary: '--chart-3', secondary: '--chart-4', tertiary: '--accent' },
      { name: 'Mist', source: 'taste-skill · Soft Minimal', primary: '--accent', secondary: '--chart-6', tertiary: '--chart-1' },
      { name: 'Paper', source: 'Hallmark · Paper', primary: '--chart-8', secondary: '--chart-1', tertiary: '--accent' },
      { name: 'Ink', source: 'frontend-design · Swiss', primary: '--text', secondary: '--accent', tertiary: '--chart-1' },
      { name: 'Frost', source: 'UI UX Pro Max · Glass', primary: '--chart-7', secondary: '--chart-2', tertiary: '--accent' }
    ]
  },
  {
    id: 'quiet',
    label: 'Quiet Workspace',
    base: {
      layout: 'notes',
      density: 'comfortable',
      radius: '12px',
      shadow: 'flat',
      surface: 'var(--surface-subtle)',
      canvas: 'var(--canvas)',
      font: 'Georgia, "Times New Roman", serif',
      use: '长文与知识库',
      avoid: '高噪声状态墙',
      tags: 'notes · docs · research'
    },
    variants: [
      { name: 'Paper', source: 'Hallmark · Paper', primary: '--accent', secondary: '--chart-4', tertiary: '--chart-5' },
      { name: 'Studio', source: 'Hallmark · Studio', primary: '--chart-1', secondary: '--accent', tertiary: '--chart-6' },
      { name: 'Atelier', source: 'Hallmark · Atelier', primary: '--chart-8', secondary: '--accent', tertiary: '--chart-3' },
      { name: 'Ribbon', source: 'Hallmark · Ribbon', primary: '--chart-4', secondary: '--accent', tertiary: '--chart-1' },
      { name: 'Furrow', source: 'Hallmark · Furrow', primary: '--chart-2', secondary: '--accent', tertiary: '--chart-5' },
      { name: 'Dose', source: 'Hallmark · Dose', primary: '--chart-6', secondary: '--accent', tertiary: '--chart-2' },
      { name: 'Hedgerow', source: 'Hallmark · Hedgerow', primary: '--chart-3', secondary: '--accent', tertiary: '--chart-7' }
    ]
  },
  {
    id: 'technical',
    label: 'Technical Console',
    base: {
      layout: 'command',
      density: 'compact',
      radius: '4px',
      shadow: 'flat',
      surface: 'var(--console-surface)',
      canvas: 'var(--console-canvas)',
      font: 'var(--font-mono)',
      use: 'Agent 与调试',
      avoid: '营销化排版',
      tags: 'agent · terminal · debug'
    },
    variants: [
      { name: 'Cobalt', source: 'Hallmark · Cobalt', primary: '--console-accent', secondary: '--console-info', tertiary: '--console-success' },
      { name: 'Dusk', source: 'Hallmark · Dusk', primary: '--console-accent', secondary: '--console-danger', tertiary: '--console-warning' },
      { name: 'Vantage', source: 'Hallmark · Vantage', primary: '--console-success', secondary: '--console-info', tertiary: '--console-accent' },
      { name: 'Refract', source: 'Hallmark · Refract', primary: '--console-info', secondary: '--console-accent', tertiary: '--console-warning' },
      { name: 'Terminal', source: 'taste-skill · Terminal', primary: '--console-text', secondary: '--console-accent', tertiary: '--console-success' },
      { name: 'Industrial', source: 'frontend-design · Industrial', primary: '--console-warning', secondary: '--console-text', tertiary: '--console-accent' },
      { name: 'Carbon', source: 'claude-artisan · Carbon', primary: '--console-text', secondary: '--console-accent', tertiary: '--console-info' }
    ]
  },
  {
    id: 'data',
    label: 'Precision Data',
    base: {
      layout: 'table',
      density: 'compact',
      radius: '2px',
      shadow: 'flat',
      surface: 'var(--surface)',
      canvas: 'var(--canvas)',
      font: 'var(--font-ui)',
      use: '财务与报表',
      avoid: '装饰性图表',
      tags: 'finance · analytics · reports'
    },
    variants: [
      { name: 'Ledger', source: 'Current Universal UI', primary: '--chart-2', secondary: '--chart-3', tertiary: '--accent' },
      { name: 'Grid', source: 'frontend-design · Swiss', primary: '--chart-1', secondary: '--chart-5', tertiary: '--accent' },
      { name: 'Report', source: 'UI UX Pro Max · Editorial', primary: '--accent', secondary: '--chart-4', tertiary: '--chart-2' },
      { name: 'Matrix', source: 'claude-artisan · Brutalist', primary: '--chart-6', secondary: '--chart-7', tertiary: '--chart-1' },
      { name: 'Ink', source: 'taste-skill · Ink', primary: '--text', secondary: '--accent', tertiary: '--chart-2' },
      { name: 'Ledger Dark', source: 'Current Universal UI', primary: '--chart-4', secondary: '--chart-2', tertiary: '--accent' },
      { name: 'Chart', source: 'UI UX Pro Max · Data', primary: '--chart-5', secondary: '--chart-3', tertiary: '--accent' }
    ]
  },
  {
    id: 'soft',
    label: 'Soft Product',
    base: {
      layout: 'onboarding',
      density: 'comfortable',
      radius: '14px',
      shadow: 'soft',
      surface: 'var(--surface-subtle)',
      canvas: 'var(--canvas)',
      font: 'var(--font-ui)',
      use: '轻工具与引导',
      avoid: '冷硬后台',
      tags: 'personal · tools · guides'
    },
    variants: [
      { name: 'Cream', source: 'UI UX Pro Max · Soft', primary: '--orange', secondary: '--accent', tertiary: '--chart-4' },
      { name: 'Cloud', source: 'UI UX Pro Max · Glass', primary: '--accent', secondary: '--chart-5', tertiary: '--chart-1' },
      { name: 'Mist', source: 'taste-skill · Soft Minimal', primary: '--chart-6', secondary: '--accent', tertiary: '--chart-3' },
      { name: 'Aurora', source: 'Hallmark · Ribbon', primary: '--chart-7', secondary: '--accent', tertiary: '--chart-2' },
      { name: 'Dawn', source: 'Hallmark · Dose', primary: '--chart-3', secondary: '--accent', tertiary: '--chart-5' },
      { name: 'Petal', source: 'Hallmark · Atelier', primary: '--violet', secondary: '--accent', tertiary: '--chart-6' },
      { name: 'Ribbon', source: 'Hallmark · Ribbon', primary: '--chart-4', secondary: '--accent', tertiary: '--chart-8' }
    ]
  },
  {
    id: 'editorial',
    label: 'Editorial Focus',
    base: {
      layout: 'article',
      density: 'comfortable',
      radius: '4px',
      shadow: 'flat',
      surface: 'var(--surface)',
      canvas: 'var(--canvas)',
      font: 'Georgia, "Times New Roman", serif',
      use: '内容与介绍页',
      avoid: '仪表盘化',
      tags: 'content · marketing · docs'
    },
    variants: [
      { name: 'Atelier', source: 'Hallmark · Atelier', primary: '--chart-8', secondary: '--accent', tertiary: '--chart-4' },
      { name: 'Studio', source: 'Hallmark · Studio', primary: '--chart-1', secondary: '--accent', tertiary: '--chart-5' },
      { name: 'Journal', source: 'Hallmark · Furrow', primary: '--chart-3', secondary: '--accent', tertiary: '--chart-7' },
      { name: 'Press', source: 'frontend-design · Editorial', primary: '--text', secondary: '--accent', tertiary: '--chart-1' },
      { name: 'Serif', source: 'taste-skill · Editorial', primary: '--accent', secondary: '--chart-4', tertiary: '--chart-2' },
      { name: 'Book', source: 'Hallmark · Hedgerow', primary: '--chart-6', secondary: '--accent', tertiary: '--chart-3' },
      { name: 'Ink', source: 'taste-skill · Ink', primary: '--text', secondary: '--chart-8', tertiary: '--accent' }
    ]
  },
  {
    id: 'compact',
    label: 'Compact Utility',
    base: {
      layout: 'widget',
      density: 'compact',
      radius: '6px',
      shadow: 'none',
      surface: 'var(--surface-subtle)',
      canvas: 'var(--canvas)',
      font: 'var(--font-ui)',
      use: '小工具与插件',
      avoid: '大面积留白',
      tags: 'tools · widgets · utilities'
    },
    variants: [
      { name: 'Dock', source: 'Current Universal UI', primary: '--accent', secondary: '--success', tertiary: '--info' },
      { name: 'Pocket', source: 'UI UX Pro Max · Minimal', primary: '--chart-1', secondary: '--accent', tertiary: '--success' },
      { name: 'Snap', source: 'taste-skill · Minimal', primary: '--chart-2', secondary: '--accent', tertiary: '--info' },
      { name: 'Tile', source: 'claude-artisan · Material', primary: '--chart-3', secondary: '--accent', tertiary: '--success' },
      { name: 'Mini', source: 'Hallmark · Studio', primary: '--chart-5', secondary: '--accent', tertiary: '--info' },
      { name: 'Card', source: 'Hallmark · Ribbon', primary: '--chart-6', secondary: '--accent', tertiary: '--success' },
      { name: 'Studio', source: 'Hallmark · Studio', primary: '--chart-7', secondary: '--accent', tertiary: '--info' }
    ]
  },
  {
    id: 'dark',
    label: 'Dark Command',
    base: {
      layout: 'command',
      density: 'compact',
      radius: '6px',
      shadow: 'soft',
      surface: 'var(--console-surface)',
      canvas: 'var(--console-canvas)',
      font: 'var(--font-mono)',
      use: '监控与运维',
      avoid: '霓虹堆砌',
      tags: 'monitoring · ops · agents'
    },
    variants: [
      { name: 'Night', source: 'Hallmark · Dusk', primary: '--console-accent', secondary: '--console-info', tertiary: '--console-success' },
      { name: 'Void', source: 'claude-artisan · Carbon', primary: '--console-text', secondary: '--console-accent', tertiary: '--console-danger' },
      { name: 'Eclipse', source: 'Hallmark · Dusk', primary: '--console-warning', secondary: '--console-accent', tertiary: '--console-info' },
      { name: 'Nebula', source: 'Hallmark · Refract', primary: '--console-success', secondary: '--console-accent', tertiary: '--console-info' },
      { name: 'Onyx', source: 'Hallmark · Vantage', primary: '--console-text', secondary: '--console-success', tertiary: '--console-accent' },
      { name: 'Carbon', source: 'claude-artisan · Carbon', primary: '--console-accent', secondary: '--console-warning', tertiary: '--console-info' },
      { name: 'Terminal', source: 'taste-skill · Terminal', primary: '--console-text', secondary: '--console-accent', tertiary: '--console-success' }
    ]
  }
];

const styles = families.flatMap(family => family.variants.map(variant => ({
  family: family.label,
  familyId: family.id,
  layout: family.base.layout,
  density: family.base.density,
  radius: family.base.radius,
  shadow: family.base.shadow,
  surface: family.base.surface,
  canvas: family.base.canvas,
  font: family.base.font,
  use: family.base.use,
  avoid: family.base.avoid,
  tags: family.base.tags,
  ...variant
})));

const layoutMarkup = {
  dashboard: `
    <div class="block hairline"></div>
    <div class="block primary"></div>
    <div class="block secondary"></div>
    <div class="block tertiary"></div>
    <div class="block hairline"></div>
  `,
  notes: `
    <div class="block hairline"></div>
    <div class="block primary"></div>
    <div class="block secondary"></div>
    <div class="block tertiary"></div>
  `,
  command: `
    <div class="block hairline"></div>
    <div class="block primary"></div>
    <div class="block secondary"></div>
    <div class="block tertiary"></div>
  `,
  table: `
    <div class="block hairline"></div>
    <div class="block primary"></div>
    <div class="block secondary"></div>
    <div class="block tertiary"></div>
    <div class="block hairline"></div>
  `,
  onboarding: `
    <div class="block primary"></div>
    <div class="block secondary"></div>
    <div class="block tertiary"></div>
  `,
  article: `
    <div class="block primary"></div>
    <div class="block secondary"></div>
    <div class="block tertiary"></div>
  `,
  widget: `
    <div class="block primary"></div>
    <div class="block secondary"></div>
  `
};

const grid = document.getElementById('atlas-grid');
const buttons = [...document.querySelectorAll('.atlas-actions .control')];

function render(activeFamily = 'all') {
  grid.innerHTML = '';
  styles.filter(style => activeFamily === 'all' || style.familyId === activeFamily).forEach(style => {
    const article = document.createElement('article');
    article.className = 'style-card';
    article.dataset.family = style.familyId;
    article.innerHTML = `
      <div class="card-head">
        <p class="card-family">${style.family}</p>
        <h3 class="card-name">${style.name}</h3>
        <p class="card-source">${style.source}</p>
      </div>
      <div class="palette" aria-label="色彩示意">
        <span style="--dot: var(${style.primary})"></span>
        <span style="--dot: var(${style.secondary})"></span>
        <span style="--dot: var(${style.tertiary})"></span>
      </div>
      <div class="mini-layout layout-${style.layout}"
        style="--mini-canvas:${style.canvas};--mini-surface:${style.surface};--mini-primary:var(${style.primary});--mini-secondary:var(${style.secondary});--mini-tertiary:var(${style.tertiary});--mini-line:var(--line);--mini-text:var(--text);--mini-font:${style.font};--mini-shadow:${style.shadow === 'flat' ? 'none' : 'var(--shadow-sm)'}">
        ${layoutMarkup[style.layout]}
      </div>
      <div class="card-foot">
        <p><strong>适用</strong>${style.use}</p>
        <p><strong>避免</strong>${style.avoid}</p>
      </div>
    `;
    grid.appendChild(article);
  });
}

function updateStatus(activeFamily) {
  const count = styles.filter(style => activeFamily === 'all' || style.familyId === activeFamily).length;
  document.querySelector('[data-status]').textContent = `已展示 ${count} 个风格`;
}

buttons.forEach(button => {
  button.addEventListener('click', () => {
    buttons.forEach(other => other.setAttribute('aria-pressed', String(other === button)));
    render(button.dataset.family);
    updateStatus(button.dataset.family);
  });
});

render();
updateStatus();
