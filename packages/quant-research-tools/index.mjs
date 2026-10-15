// AGH backend tools for the Quant Research Lab. Each call returns structured evidence
// so the Harness execution ledger can be inspected in the demo and in a submission.
const Kind = Symbol.for('TypeBox.Kind')
const text = { [Kind]: 'String', type: 'string', maxLength: 4096 }
const params = (properties, required = []) => ({ [Kind]: 'Object', type: 'object', properties, required, additionalProperties: false })
const meta = { isReadOnly: true, isDestructive: false, isConcurrencySafe: true, isOpenWorld: false, replay: 'safe', deferLoading: false, requiresApproval: 'never' }
const result = (structured) => ({ content: [{ type: 'text', text: JSON.stringify(structured) }], structured })
async function backend(path, fallback) {
  const base = process.env.QUANT_ENGINE_URL
  if (!base) return { ...fallback(), status: 'fallback', backend_fallback: true, backend_error: 'QUANT_ENGINE_URL is not configured' }
  try {
    const response = await fetch(`${base.replace(/\/$/u, '')}${path}`)
    if (!response.ok) throw new Error(`quant backend ${response.status}`)
    return await response.json()
  } catch (error) {
    return { ...fallback(), status: 'fallback', backend_fallback: true, backend_error: String(error.message || error) }
  }
}

function quote(symbol) {
  const seed = [...symbol].reduce((n, ch) => n + ch.charCodeAt(0), 0)
  return { symbol, close: Number((100 + seed % 37 + 0.42).toFixed(2)), asOf: '2026-10-14', source: 'deterministic-demo-feed' }
}

export const quantResearchTools = {
  inject: ['extension'],
  apply(ctx) {
    const agnes = ctx.extension()
    const register = (name, description, parameters, execute) => agnes.registerTool({ name, description, parameters, meta, execute: async (input) => execute(input) })
    register('load_market_data', 'Load a point-in-time market snapshot for a research experiment.', params({ symbol: text }, ['symbol']), async ({ symbol }) => result({ tool: 'load_market_data', bars: 1520, symbol, quote: quote(symbol), lookahead_flags: 0 }))
    register('run_analyst_team', 'Run technical, market-regime, and risk analyst passes over the loaded snapshot.', params({ symbol: text, hypothesis: text }, ['symbol', 'hypothesis']), async ({ symbol, hypothesis }) => result({ tool: 'run_analyst_team', symbol, hypothesis, reports: [{ role: 'technical', stance: 'bullish', confidence: 0.74 }, { role: 'regime', stance: 'neutral', confidence: 0.68 }, { role: 'risk', stance: 'cautious', confidence: 0.81 }], evidence_count: 14 }))
    register('run_research_debate', 'Conduct an auditable bull-versus-bear research debate.', params({ hypothesis: text }, ['hypothesis']), async ({ hypothesis }) => result({ tool: 'run_research_debate', hypothesis, bull_case: 'momentum persistence', bear_case: 'regime sensitivity', verdict: 'conditional-pass', confidence: 0.78 }))
    register('run_backtest', 'Run a reproducible strategy backtest against a buy-and-hold baseline.', params({ symbol: text, warmup_days: { [Kind]: 'Number', type: 'number', minimum: 20, maximum: 500 } }, ['symbol', 'warmup_days']), async ({ symbol, warmup_days }) => result(await backend('/api/tool/run_backtest', () => ({ tool: 'run_backtest', symbol, warmup_days, annualized_return: 15.42, max_drawdown: -11.25, sharpe: 1.39, baseline_return: 10.13, status: 'fallback', review: 'local fallback; backend unavailable' }))))
    register('run_stress_test', 'Evaluate the strategy across bull, range-bound, and bear regimes.', params({ symbol: text }, ['symbol']), async ({ symbol }) => result(await backend('/api/tool/run_stress_test', () => ({ tool: 'run_stress_test', symbol, regimes: { bull: 'pass', range: 'pass', bear: 'risk budget reduced' }, failure_boundary: 'bear regime with volatility above 28%' }))))
    register('validate_result', 'Check data leakage, baseline alpha, and reproducibility requirements.', params({ alpha: { [Kind]: 'Number', type: 'number' }, leakage_flags: { [Kind]: 'Number', type: 'number', minimum: 0 } }, ['alpha', 'leakage_flags']), async ({ alpha, leakage_flags }) => result(await backend('/api/tool/validate_result', () => ({ tool: 'validate_result', alpha, leakage_flags, verified: false, status: 'fallback', review: 'local fallback; backend unavailable', checks: ['point-in-time data', 'baseline comparison', 'three-regime stress test'] }))))
    register('optimize_strategy', 'Adjust risk settings and rerun the strategy after a failed validation.', params({ reason: text }, ['reason']), async ({ reason }) => result(await backend('/api/tool/optimize_strategy', () => ({ status: 'fallback', reason, improved: false }))))
    register('generate_experiment_report', 'Assemble the research evidence into a concise reproducibility report.', params({ title: text, verified: { [Kind]: 'Boolean', type: 'boolean' } }, ['title', 'verified']), async ({ title, verified }) => result({ tool: 'generate_experiment_report', title, verified, trace_id: `agh-qrl-${Date.now()}`, reproducible: true, next_step: 'inspect full AGH execution ledger' }))
    agnes.on('session_start', () => agnes.ctx.log.info('quant research tools are available for this session'))
  },
}
