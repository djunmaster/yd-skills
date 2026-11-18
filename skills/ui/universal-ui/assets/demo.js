const sample = document.querySelector('[data-template]');
const find = selector => sample.querySelector(selector);
const findAll = selector => Array.from(sample.querySelectorAll(selector));
const notify = text => { find('[data-status]').textContent = text; };
const format = new Intl.NumberFormat('zh-CN');
const money = value => `¥${format.format(value)}`;

const themeToggle = find('[data-theme-toggle]');
themeToggle.addEventListener('click', () => {
  const dark = document.documentElement.dataset.theme !== 'dark';
  document.documentElement.dataset.theme = dark ? 'dark' : 'light';
  themeToggle.textContent = dark ? '浅色预览' : '深色预览';
});

function renderPairs(container, entries) {
  container.replaceChildren(...entries.map(([label, value]) => {
    const pair = document.createElement('div');
    const term = document.createElement('dt');
    const description = document.createElement('dd');
    term.textContent = label;
    description.textContent = value;
    pair.append(term, description);
    return pair;
  }));
}

function initAnalytics() {
  const monthly = [
    { month: '6 月', revenue: 132800, mrr: 112400, sessions: 4120, orders: 160 },
    { month: '7 月', revenue: 145200, mrr: 118100, sessions: 4610, orders: 188 },
    { month: '8 月', revenue: 157900, mrr: 123600, sessions: 4920, orders: 205 },
    { month: '9 月', revenue: 154400, mrr: 127800, sessions: 5310, orders: 216 },
    { month: '10 月', revenue: 181600, mrr: 136000, sessions: 5760, orders: 254 },
    { month: '11 月', revenue: 203600, mrr: 143500, sessions: 6290, orders: 302 },
  ];
  const ranges = findAll('[data-range]');

  function update(count) {
    const series = monthly.slice(-count);
    const sum = field => series.reduce((total, period) => total + period[field], 0);
    const metrics = {
      revenue: money(sum('revenue')),
      mrr: money(series.at(-1).mrr),
      sessions: format.format(sum('sessions')),
      conversion: `${(sum('orders') / sum('sessions') * 100).toFixed(1)}%`,
    };
    for (const [metric, value] of Object.entries(metrics)) find(`[data-metric="${metric}"]`).textContent = value;
    const points = series.map((period, index) => `${500 * index / (series.length - 1)},${200 - 200 * period.revenue / 250000}`).join(' ');
    find('.trend').setAttribute('points', points);
    find('.area').setAttribute('points', `0,200 ${points} 500,200`);
    find('[data-axis]').replaceChildren(...series.map(period => {
      const label = document.createElement('span');
      label.textContent = period.month;
      return label;
    }));
    renderPairs(find('[data-chart-values]'), series.map(period => [period.month, money(period.revenue)]));
    ranges.forEach(button => button.setAttribute('aria-pressed', String(Number(button.dataset.range) === count)));
    notify(`${series[0].month}至 ${series.at(-1).month} · 共 ${count} 期 · 总收入 ${metrics.revenue}`);
  }

  ranges.forEach(button => button.addEventListener('click', () => update(Number(button.dataset.range))));
  update(6);
}

function initMonitoring() {
  const filter = find('[data-service]');
  const rows = findAll('[data-service-id]');
  const states = { '1': { tone: 'warning', text: '降级' }, '2': { tone: 'danger', text: '中断' } };
  rows.forEach(row => {
    Array.from(row.dataset.windows).forEach(state => {
      const cell = document.createElement('span');
      cell.className = 'window';
      if (states[state]) cell.dataset.tone = states[state].tone;
      row.querySelector('.windows').append(cell);
    });
  });

  function update() {
    const visible = [];
    rows.forEach(row => {
      row.hidden = filter.value !== 'all' && row.dataset.serviceId !== filter.value;
      if (!row.hidden) visible.push(row);
    });
    const events = visible.flatMap(row => Array.from(row.dataset.windows).flatMap((state, index) => states[state]
      ? [[row.querySelector('strong').textContent, `窗口 ${index + 1} · ${states[state].text}`]] : []));
    renderPairs(find('[data-incidents]'), events.length ? events : [['最近 30 个窗口', '无异常']]);
    notify(`${visible.length} 个服务 · ${events.length} 个异常窗口`);
  }

  filter.addEventListener('change', update);
  update();
}

function initGateway() {
  findAll('[data-provider]').forEach(row => {
    const toggle = row.querySelector('input');
    const badge = row.querySelector('.badge');
    toggle.addEventListener('change', () => {
      const enabled = toggle.checked;
      badge.dataset.tone = enabled ? row.dataset.health : 'neutral';
      badge.textContent = enabled ? row.dataset.health === 'success' ? '可用' : '延迟偏高' : '未启用';
      row.querySelector('[data-latency-label]').textContent = enabled ? `${row.dataset.latency} ms` : '—';
      notify(`${row.querySelector('strong').textContent} 已${enabled ? '启用' : '停用'}，仅更新本地示例。`);
    });
  });
  notify('启停操作只影响当前示例。');
}

function initCrm() {
  const search = find('[data-search]');
  const owner = find('[data-owner]');
  const reset = find('[data-reset]');
  const sort = find('[data-sort]');
  const retry = find('[data-retry]');
  const records = find('[data-records]');
  const rows = findAll('tbody tr');
  const statePanel = find('[data-state-panel]');
  const stateTitle = find('[data-state-title]');
  const stateDetail = find('[data-state-detail]');
  const states = {
    loading: ['正在加载客户…', '这是加载状态预览，可继续查看示例记录。', '完成加载'],
    empty: ['还没有客户', '新增客户后，记录会显示在这里。'],
    error: ['客户列表加载失败', '筛选条件仍会保留，请重新加载。', '重试'],
    noMatch: ['没有匹配的客户', '可调整搜索词或清除筛选。'],
  };
  const requestedState = new URLSearchParams(location.search).get('state');
  let state = ['loading', 'empty', 'error'].includes(requestedState) ? requestedState : 'ready';
  let ascending = false;

  function update() {
    const query = search.value.trim().toLocaleLowerCase();
    const displayable = rows.filter(row => row.textContent.toLocaleLowerCase().includes(query) && (owner.value === 'all' || row.cells[2].textContent === owner.value));
    rows.forEach(row => { row.hidden = !displayable.includes(row); });
    reset.disabled = search.value === '' && owner.value === 'all';
    const shownState = state === 'ready' && displayable.length === 0 ? 'noMatch' : state;
    const ready = shownState === 'ready';
    const [title, description, action] = states[shownState] ?? [];
    records.hidden = !ready;
    statePanel.hidden = ready;
    statePanel.setAttribute('aria-busy', String(shownState === 'loading'));
    stateTitle.textContent = title ?? '';
    stateTitle.classList.toggle('error', shownState === 'error');
    stateDetail.textContent = description ?? '';
    retry.hidden = !action;
    if (action) retry.textContent = action;
    notify(ready ? `显示 ${displayable.length} 条 · 共 ${rows.length} 条记录` : title);
  }

  search.addEventListener('input', update);
  owner.addEventListener('change', update);
  reset.addEventListener('click', () => { search.value = ''; owner.value = 'all'; update(); search.focus(); });
  retry.addEventListener('click', () => { state = 'ready'; update(); search.focus(); });
  sort.addEventListener('click', () => {
    ascending = !ascending;
    const direction = ascending ? 1 : -1;
    const sorted = [...rows].sort((first, second) => direction * (Number(first.dataset.amount) - Number(second.dataset.amount)));
    find('tbody').append(...sorted);
    sort.parentElement.setAttribute('aria-sort', ascending ? 'ascending' : 'descending');
    sort.querySelector('span').textContent = ascending ? '↑' : '↓';
    notify(`月度收入 ${ascending ? '从低到高' : '从高到低'}`);
  });
  update();
}

function initSaas() {
  const collect = find('[data-collect]');
  collect.addEventListener('click', () => {
    if (collect.getAttribute('aria-disabled') === 'true') return;
    collect.textContent = '已标记';
    collect.setAttribute('aria-disabled', 'true');
    find('[data-overdue]').textContent = '待催收';
    notify('青岚零售账单已在本地标记为待催收，未发送通知。');
  });
}

const templates = { analytics: initAnalytics, monitoring: initMonitoring, gateway: initGateway, crm: initCrm, saas: initSaas };
templates[sample.dataset.template]();
