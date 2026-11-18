const pageTypes = [
  {
    id: 'agent',
    name: 'AI Agent 工作台',
    variants: [
      { scheme: 'stable', variant: '稳定三列', note: '会话、执行、详情边界清楚。' },
      { scheme: 'compact', variant: '紧凑双列', note: '窄屏优先保留消息与输入。' },
      { scheme: 'personal', variant: '命令台主导', note: '运行状态和轨迹更强。' }
    ],
    markup: `
      <div class="mock-rail"></div>
      <div class="mock-bar"></div>
      <div class="main"><div class="mock-block mock-primary"></div><div class="mock-block"></div><div class="mock-block mock-secondary"></div><div class="mock-block"></div></div>
      <div class="side"><div class="mock-block mock-tertiary"></div><div class="mock-block"></div><div class="mock-block mock-secondary"></div></div>
      <div class="composer"><div class="mock-block"></div><div class="mock-action"></div></div>
    `
  },
  {
    id: 'notes',
    name: '笔记知识库',
    variants: [
      { scheme: 'stable', variant: '阅读三栏', note: '正文稳定，属性不打扰。' },
      { scheme: 'compact', variant: '目录双栏', note: '适合高频整理和检索。' },
      { scheme: 'personal', variant: '深色书房', note: '适合夜间长文和专注。' }
    ],
    markup: `
      <div class="mock-rail"></div>
      <div class="mock-bar"></div>
      <div class="document"><div class="mock-block mock-primary"></div><div class="mock-line"></div><div class="mock-line"></div><div class="mock-line"></div><div class="mock-block mock-secondary"></div></div>
      <div class="properties"><div class="mock-block mock-tertiary"></div><div class="mock-block"></div><div class="mock-block"></div></div>
    `
  },
  {
    id: 'data',
    name: '数据后台',
    variants: [
      { scheme: 'stable', variant: '指标到明细', note: '先给结论，再给下钻。' },
      { scheme: 'compact', variant: '高密度分析', note: '同屏比较更多维度。' },
      { scheme: 'personal', variant: '深色观察', note: '趋势和异常更突出。' }
    ],
    markup: `
      <div class="mock-bar"></div>
      <div class="metrics"><div class="mock-block"></div><div class="mock-block mock-primary"></div><div class="mock-block"></div><div class="mock-block mock-secondary"></div></div>
      <div class="content"><div class="mock-block mock-primary"></div><div class="mock-block"></div></div>
      <div class="mock-block"></div>
    `
  },
  {
    id: 'monitor',
    name: '监控排障',
    variants: [
      { scheme: 'stable', variant: '筛选时间线', note: '先定位，再看状态说明。' },
      { scheme: 'compact', variant: '密度优先', note: '适合多服务快速扫视。' },
      { scheme: 'personal', variant: '夜航控制台', note: '异常色更醒目但不刺眼。' }
    ],
    markup: `
      <div class="mock-bar"></div>
      <div class="metrics"><div class="mock-block"></div><div class="mock-block"></div><div class="mock-block mock-primary"></div><div class="mock-block"></div></div>
      <div class="timeline"><span></span><span></span><span></span><span></span><span></span><span></span><span></span><span></span><span></span><span></span><span></span><span></span></div>
      <div class="mock-bar mock-secondary"></div>
    `
  },
  {
    id: 'config',
    name: '配置设置',
    variants: [
      { scheme: 'stable', variant: '分组设置行', note: '配置边界和保存路径清楚。' },
      { scheme: 'compact', variant: '紧凑列表', note: '适合服务多、字段短。' },
      { scheme: 'personal', variant: '控制面板', note: '运行状态更直观。' }
    ],
    markup: `
      <div class="mock-rail"></div>
      <div class="mock-bar"></div>
      <div class="rows"><div class="row"><div class="mock-block"></div><div class="mock-action"></div></div><div class="row"><div class="mock-block mock-primary"></div><div class="mock-block"></div></div><div class="row"><div class="mock-block"></div><div class="mock-block mock-secondary"></div></div></div>
    `
  },
  {
    id: 'records',
    name: '记录管理',
    variants: [
      { scheme: 'stable', variant: '筛选表格', note: '搜索、排序和操作完整。' },
      { scheme: 'compact', variant: '高密度表格', note: '同屏看到更多记录。' },
      { scheme: 'personal', variant: '深色数据台', note: '适合长时间查看数据。' }
    ],
    markup: `
      <div class="mock-bar"></div>
      <div class="metrics"><div class="mock-block"></div><div class="mock-block mock-primary"></div><div class="mock-block"></div><div class="mock-action"></div></div>
      <div class="table"><div class="table-row"><div class="mock-cell"></div><div class="mock-cell mock-primary"></div><div class="mock-cell"></div><div class="mock-cell mock-secondary"></div></div><div class="table-row"><div class="mock-cell"></div><div class="mock-cell"></div><div class="mock-cell mock-tertiary"></div><div class="mock-cell"></div></div><div class="table-row"><div class="mock-cell"></div><div class="mock-cell"></div><div class="mock-cell"></div><div class="mock-cell"></div></div></div>
      <div class="mock-bar"></div>
    `
  },
  {
    id: 'finance',
    name: '账务财务',
    variants: [
      { scheme: 'stable', variant: '摘要明细', note: '先看总额，再看状态。' },
      { scheme: 'compact', variant: '对账优先', note: '数字和状态更紧凑。' },
      { scheme: 'personal', variant: '财务控制台', note: '异常和逾期更醒目。' }
    ],
    markup: `
      <div class="mock-bar"></div>
      <div class="summary"><div class="mock-block mock-primary"></div><div class="mock-block"></div><div class="mock-block mock-secondary"></div></div>
      <div class="detail"><div class="mock-block"></div><div class="mock-block mock-tertiary"></div><div class="mock-block"></div></div>
    `
  },
  {
    id: 'utility',
    name: '小工具',
    variants: [
      { scheme: 'stable', variant: '输入结果', note: '首屏完成一次任务。' },
      { scheme: 'compact', variant: '快捷处理', note: '适合批量与高频操作。' },
      { scheme: 'personal', variant: '深色终端', note: '适合命令型小工具。' }
    ],
    markup: `
      <div class="mock-bar"></div>
      <div class="result"><div class="mock-block mock-primary"></div><div class="mock-block"></div><div class="mock-block mock-secondary"></div></div>
      <div class="metrics"><div class="mock-block"></div><div class="mock-action"></div></div>
    `
  },
  {
    id: 'content',
    name: '内容页面',
    variants: [
      { scheme: 'stable', variant: '阅读版式', note: '标题和正文层级稳定。' },
      { scheme: 'compact', variant: '信息紧凑', note: '适合说明文档和指南。' },
      { scheme: 'personal', variant: '编辑风格', note: '有个性但不喧宾夺主。' }
    ],
    markup: `
      <div class="mock-block mock-primary"></div>
      <div class="article"><div class="mock-block"></div><div class="mock-line"></div><div class="mock-line"></div><div class="mock-block mock-secondary"></div><div class="mock-line"></div></div>
      <div class="aside"><div class="mock-block"></div><div class="mock-block mock-tertiary"></div><div class="mock-block"></div></div>
    `
  },
  {
    id: 'search',
    name: '搜索结果',
    variants: [
      { scheme: 'stable', variant: '列表优先', note: '结果类型和摘要清楚。' },
      { scheme: 'compact', variant: '筛选并列', note: '适合多条件检索。' },
      { scheme: 'personal', variant: '深色检索', note: '夜间查找更舒服。' }
    ],
    markup: `
      <div class="mock-bar"></div>
      <div class="metrics"><div class="mock-block mock-primary"></div><div class="mock-block"></div><div class="mock-block"></div></div>
      <div class="results"><div class="result"><div class="mock-block"></div><div><div class="mock-line"></div><div class="mock-line"></div></div></div><div class="result"><div class="mock-block mock-secondary"></div><div><div class="mock-line"></div><div class="mock-line"></div></div></div></div>
    `
  },
  {
    id: 'empty',
    name: '空态引导',
    variants: [
      { scheme: 'stable', variant: '单点引导', note: '告诉用户下一步做什么。' },
      { scheme: 'compact', variant: '快捷入口', note: '适合熟悉用户。' },
      { scheme: 'personal', variant: '柔和首启', note: '降低第一次使用压力。' }
    ],
    markup: `
      <div class="mock-block mock-primary"></div>
      <div class="empty"><div class="mock-block mock-outline"></div><div class="mock-block"></div><div class="mock-action"></div></div>
      <div class="mock-bar"></div>
    `
  },
  {
    id: 'form',
    name: '表单流程',
    variants: [
      { scheme: 'stable', variant: '分步表单', note: '错误能落到字段。' },
      { scheme: 'compact', variant: '单屏配置', note: '适合短表单和高级用户。' },
      { scheme: 'personal', variant: '深色设置', note: '适合系统或开发配置。' }
    ],
    markup: `
      <div class="steps"><div class="mock-block mock-primary"></div><div class="mock-block"></div><div class="mock-block"></div></div>
      <div class="fields"><div><div class="mock-line"></div><div class="mock-block"></div></div><div><div class="mock-line"></div><div class="mock-block mock-secondary"></div></div><div><div class="mock-line"></div><div class="mock-block"></div></div></div>
      <div class="mock-action"></div>
    `
  }
];

const grid = document.getElementById('atlas-grid');
const buttons = [...document.querySelectorAll('.atlas-actions .control')];
const allSchemes = pageTypes.flatMap(type => type.variants.map(variant => ({ type, variant })));

function render(activeLayout = 'all') {
  grid.replaceChildren();
  allSchemes.filter(({ type }) => activeLayout === 'all' || type.id === activeLayout).forEach(({ type, variant }) => {
    const card = document.createElement('article');
    card.className = 'layout-card';
    card.dataset.layout = type.id;
    card.innerHTML = `
      <div class="layout-head">
        <p class="layout-kind">${type.name}</p>
        <h3 class="layout-name">${variant.variant}</h3>
        <p class="layout-note">${variant.note}</p>
      </div>
      <div class="page-mock page-${type.id} scheme-${variant.scheme}">${type.markup}</div>
      <div class="layout-foot"><strong>方案</strong><span>${variant.scheme === 'stable' ? '稳妥' : variant.scheme === 'compact' ? '紧凑' : '个性'}</span></div>
    `;
    grid.append(card);
  });
  const count = [...grid.children].length;
  document.querySelector('[data-status]').textContent = `已展示 ${count} 个页面布局方案`;
}

buttons.forEach(button => {
  button.addEventListener('click', () => {
    buttons.forEach(other => other.setAttribute('aria-pressed', String(other === button)));
    render(button.dataset.layout);
  });
});

render();
