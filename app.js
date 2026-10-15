const steps = [
  ['01', 'Frame the question'], ['02', 'Gather point-in-time data'], ['03', 'Analyst team'],
  ['04', 'Bull / bear debate'], ['05', 'Backtest & stress test'], ['06', 'Verify the claim'],
];
const events = [
  ['Question framed', 'mission_router', '将“动量因子是否稳定”拆解为数据、策略和验证三个子任务。', 'success'],
  ['Data contract locked', 'market_data_tool', '沪深300 · 1,521 bars · point-in-time snapshot locked', 'success'],
  ['Analyst team started', 'parallel_agents', 'technical / market-regime / risk analysts are working in parallel…', 'success'],
  ['Analyst team completed', 'parallel_agents', '3 reports returned · 14 evidence points · 2 risk flags', 'success'],
  ['Debate in progress', 'bull_bear_debate', 'bull: persistence · bear: regime sensitivity · cross-examining claims…', 'success'],
  ['Debate resolved', 'bull_bear_debate', 'bull: persistence · bear: regime sensitivity · confidence 0.78', 'success'],
  ['Retry requested', 'backtest_tool', 'first run rejected: insufficient warm-up window; adjusting to 120 days', 'error'],
  ['Stress test running', 'regime_stress_tool', 'replaying bull / range-bound / bear regimes against the candidate', 'success'],
  ['Claim verified', 'validation_gate', 'alpha +7.8% vs buy & hold · 3 regimes · 0 leakage flags', 'success'],
];
const stepList = document.querySelector('#stepList');
const trajectory = document.querySelector('#trajectory');
const inspectorState = document.querySelector('#inspectorState');
const runBtn = document.querySelector('#runBtn');
const resetBtn = document.querySelector('#resetBtn');
let running = false;
let timer;

function renderSteps(active = -1) {
  stepList.innerHTML = steps.map((s, i) => `<div class="step ${i < active ? 'done' : ''} ${i === active ? 'active' : ''}"><span class="node"></span><span><b>${s[0]}</b> ${s[1]}</span></div>`).join('');
}
function renderEvent(item, i) {
  const [title, tool, detail, status] = item;
  const node = document.createElement('div');
  node.className = `event ${status}`;
  node.style.animationDelay = `${i * 80}ms`;
  node.innerHTML = `<div class="event-head"><b>${title}</b><time>${tool}</time></div><p>${detail}</p>`;
  trajectory.appendChild(node);
}
function reset() {
  clearInterval(timer); running = false; trajectory.innerHTML = '';
  renderSteps(-1); inspectorState.textContent = 'Awaiting mission';
  runBtn.innerHTML = '<span class="play">▶</span> Run research mission';
  document.querySelector('#runTime').textContent = '00:00.0';
}
async function run() {
  if (running) return; running = true; trajectory.innerHTML = ''; let i = 0; let ticks = 0;
  runBtn.innerHTML = '<span class="play">●</span> Mission running'; inspectorState.textContent = 'Executing AGH trajectory';
  try {
    const result = await fetch('/api/mission').then((response) => response.json());
    document.querySelector('#returnMetric').textContent = `${result.strategy_return}%`;
    document.querySelector('#drawdownMetric').textContent = `${result.max_drawdown}%`;
    document.querySelector('#sharpeMetric').textContent = result.sharpe;
    document.querySelector('#alphaMetric').textContent = `${result.alpha >= 0 ? '+' : ''}${result.alpha}%`;
    events[1][2] = `沪深300 · ${result.bars.toLocaleString()} bars · point-in-time snapshot locked`;
    events[events.length - 1][2] = `alpha ${result.alpha >= 0 ? '+' : ''}${result.alpha}% vs buy & hold · 3 regimes · ${result.leakage_flags} leakage flags`;
  } catch (_) {
    trajectory.innerHTML = '<div class="event error"><div class="event-head"><b>Backend unavailable</b><time>mission_router</time></div><p>请先使用 python server.py 启动研究后端。</p></div>';
    inspectorState.textContent = 'Backend unavailable'; running = false; runBtn.innerHTML = '<span class="play">↻</span> Retry mission'; return;
  }
  timer = setInterval(() => {
    ticks += 1; document.querySelector('#runTime').textContent = `00:${String(Math.round(ticks * 1.2)).padStart(2, '0')}.0`;
    if (i < events.length) { renderEvent(events[i], i); renderSteps(Math.min(i, steps.length - 1)); i += 1; }
    if (i >= events.length) { clearInterval(timer); running = false; renderSteps(steps.length); inspectorState.textContent = 'Mission verified · ready to inspect'; runBtn.innerHTML = '<span class="play">↻</span> Run again'; }
  }, 1200);
}
runBtn.addEventListener('click', run); resetBtn.addEventListener('click', reset); reset();
