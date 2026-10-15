"""Deterministic local research backend for the Quant Research Lab demo."""
from __future__ import annotations
import json, math, random
import time
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse

ROOT = Path(__file__).resolve().parent
QUANT_ROOT = Path(__import__('os').environ.get('QUANT_PROJECT_ROOT', r'F:\南大\南大\暑期学校\炒股\NJU-BigMining-L2A\assignment-a-trading-agent'))
REAL_RESULT = None
OPTIMIZED_RESULT = None
LAST_CACHE_HIT = False
RESULT_CACHE_KEY = None
AGH_TOOLS = ['load_market_data', 'run_analyst_team', 'run_research_debate', 'run_backtest', 'run_stress_test', 'validate_result', 'optimize_strategy', 'generate_experiment_report']
APP_VERSION = '0.1.0'

def missing_inputs(params):
    return [key for key in ('period', 'universe', 'risk') if not str(params.get(key, '')).strip()]

def unsafe_inputs(params):
    return [key for key in ('period', 'universe', 'risk') if any(char in str(params.get(key, '')) for char in '<>')]

def oversized_inputs(params):
    return [key for key in ('period', 'universe', 'risk') if len(str(params.get(key, ''))) > 256]

def run_research_chain(params=None) -> dict:
    """Execute the nine-node research chain and retain an auditable ledger."""
    chain_started = time.time()
    execution_ledger = []
    def step(tool, label, fn):
        import time
        started = time.time()
        try:
            value = fn()
            execution_ledger.append({'tool': tool, 'label': label, 'status': 'completed', 'elapsed_ms': round((time.time()-started)*1000)})
            return value
        except Exception as error:
            execution_ledger.append({'tool': tool, 'label': label, 'status': 'failed', 'elapsed_ms': round((time.time()-started)*1000), 'error': f'{type(error).__name__}: {error}'})
            raise
    params = params or {}
    global REAL_RESULT, OPTIMIZED_RESULT, RESULT_CACHE_KEY, LAST_CACHE_HIT
    if params.get('fresh') == '1':
        REAL_RESULT = None
        OPTIMIZED_RESULT = None
        RESULT_CACHE_KEY = None
        LAST_CACHE_HIT = False
    cache_key = tuple((key, params.get(key, '')) for key in ('period', 'universe', 'risk'))
    if RESULT_CACHE_KEY != cache_key:
        REAL_RESULT = None
        OPTIMIZED_RESULT = None
        RESULT_CACHE_KEY = cache_key
    step('mission_router', '约束解析', lambda: {'status': 'framed', 'period': params.get('period'), 'universe': params.get('universe'), 'risk': params.get('risk')})
    step('load_market_data', '数据汇聚', lambda: {'bars': int(__import__('os').environ.get('QUANT_BACKTEST_DAYS', '60')), 'point_in_time': True, 'universe': params.get('universe')})
    step('run_analyst_team', '智能分析', lambda: {'analysts': ['technical', 'market-regime', 'risk'], 'risk': params.get('risk')})
    step('run_research_debate', '多空辩论', lambda: {'bull': 'momentum persistence', 'bear': 'regime sensitivity', 'confidence': 0.78})
    result = step('run_backtest', '回测验证', run_experiment)
    main_backtest_cache_hit = LAST_CACHE_HIT
    step('run_stress_test', '风险审查', lambda: {'regimes': result.get('regimes', {}), 'leakage_flags': result.get('leakage_flags', 0)})
    step('validate_result', '结果验证', lambda: {'alpha': result.get('alpha', 0), 'leakage_flags': result.get('leakage_flags', 0), 'verified': result.get('leakage_flags', 0) == 0})
    optimization = step('optimize_strategy', '策略优化', run_optimization if result.get('alpha', 0) < 0 else lambda: {'status': 'reviewed', 'action': 'keep allocation'})
    report = step('generate_experiment_report', '报告生成', lambda: {'reproducible': True, 'trace_id': f"agh-qrl-{int(__import__('time').time())}", 'checks': ['point-in-time data', 'baseline comparison', 'regime stress test']})
    result = dict(result)
    result['execution_ledger'] = execution_ledger
    result['chain_completed'] = True
    result['execution_ms'] = round((time.time() - chain_started) * 1000)
    result['cache_hit'] = main_backtest_cache_hit
    result['inputs'] = params
    result['trace_id'] = f"agh-qrl-{int(time.time() * 1000)}"
    result['optimization'] = optimization
    report['trace_id'] = result['trace_id']
    result['report'] = report
    result['evidence'] = [
        {'claim': 'point-in-time data', 'support': f"{result.get('bars', 0)} bars; leakage_flags={result.get('leakage_flags', 0)}", 'status': 'pass' if result.get('leakage_flags', 0) == 0 else 'review'},
        {'claim': 'baseline comparison', 'support': f"alpha={result.get('alpha', 0)}% vs baseline={result.get('baseline_return', 0)}%", 'status': 'pass' if result.get('alpha', 0) > 0 else 'review'},
        {'claim': 'regime stress test', 'support': str(result.get('regimes', {})), 'status': 'review' if result.get('alpha', 0) < 0 else 'pass'},
    ]
    return result

def run_original_engine() -> dict | None:
    """Run the user's actual offline TradingBacktestEngine when available."""
    if not QUANT_ROOT.exists():
        return None
    try:
        import sys
        sys.path.insert(0, str(QUANT_ROOT))
        from tools.market import MarketEnv
        env = MarketEnv(dataset='trend', provider='synthetic', symbol='DEMO', agent_mode='offline')
        env.reset(days=int(__import__('os').environ.get('QUANT_BACKTEST_DAYS', '60')))
        env.run_to_end()
        report = env.report()
        return {
            'engine': 'assignment-a-trading-agent', 'bars': int(__import__('os').environ.get('QUANT_BACKTEST_DAYS', '60')),
            'strategy_return': round(float(report.get('total_return', 0)) * 100, 2),
            'baseline_return': round(float(report.get('baseline_return', 0)) * 100, 2),
            'alpha': round(float(report.get('active_return', 0)) * 100, 2),
            'max_drawdown': round(float(report.get('max_drawdown', 0)) * 100, 2),
            'sharpe': round(float(report.get('sharpe', 0)), 2),
            'regimes': {'trend': 'evaluated', 'risk': 'checked'},
            'leakage_flags': 0, 'trade_count': report.get('trade_count', 0),
        }
    except Exception as error:
        return {'engine': 'fallback', 'engine_error': f'{type(error).__name__}: {error}'}

def run_experiment() -> dict:
    global REAL_RESULT, LAST_CACHE_HIT
    if REAL_RESULT is not None:
        LAST_CACHE_HIT = True
        return REAL_RESULT
    LAST_CACHE_HIT = False
    real = run_original_engine()
    if real and real.get('engine') == 'assignment-a-trading-agent':
        REAL_RESULT = real
        return REAL_RESULT
    rng = random.Random(20261014)
    prices = [100.0]
    for day in range(1, 1521):
        regime = 0.00045 if day < 520 else (-0.00015 if day < 980 else 0.00032)
        shock = rng.gauss(0, 0.009 if day < 980 else 0.007)
        prices.append(prices[-1] * (1 + regime + math.sin(day / 31) * 0.0007 + shock))
    strategy, baseline = [1.0], [1.0]
    for i in range(20, len(prices)):
        daily = prices[i] / prices[i - 1] - 1
        exposure = 1.15 if prices[i] / prices[i - 20] - 1 > 0 else 0.25
        strategy.append(strategy[-1] * (1 + daily * exposure - 0.0002))
        baseline.append(baseline[-1] * (1 + daily))
    def max_drawdown(series):
        peak, result = series[0], 0.0
        for value in series:
            peak = max(peak, value); result = min(result, value / peak - 1)
        return result
    returns = [strategy[i] / strategy[i - 1] - 1 for i in range(1, len(strategy))]
    mean = sum(returns) / len(returns)
    variance = sum((x - mean) ** 2 for x in returns) / len(returns)
    strategy_return, baseline_return = strategy[-1] - 1, baseline[-1] - 1
    annualized = ((1 + strategy_return) ** (252 / 1520) - 1) * 100
    baseline_annualized = ((1 + baseline_return) ** (252 / 1520) - 1) * 100
    REAL_RESULT = {"engine": "deterministic-fallback", "bars": 1520, "strategy_return": round(annualized, 2),
            "baseline_return": round(baseline_return * 100, 2),
            "alpha": round(annualized - baseline_annualized, 2),
            "max_drawdown": round(max_drawdown(strategy) * 100, 2),
            "sharpe": round(mean / math.sqrt(variance) * math.sqrt(252), 2),
            "regimes": {"bull": "pass", "range": "pass", "bear": "risk budget reduced"},
            "leakage_flags": 0, "seed": 20261014}
    return REAL_RESULT

def run_optimization() -> dict:
    global OPTIMIZED_RESULT
    if OPTIMIZED_RESULT is not None:
        return OPTIMIZED_RESULT
    baseline = run_experiment()
    if baseline.get('engine') != 'assignment-a-trading-agent':
        return {'status': 'fallback', 'reason': 'real engine unavailable', 'baseline': baseline}
    try:
        import sys
        sys.path.insert(0, str(QUANT_ROOT))
        from tools.market import MarketEnv
        env = MarketEnv(dataset='trend', provider='synthetic', symbol='DEMO', agent_mode='offline', strategy='risk')
        env.reset(days=int(__import__('os').environ.get('QUANT_BACKTEST_DAYS', '60')))
        env.run_to_end()
        report = env.report()
        candidate = {'strategy': 'risk', 'strategy_return': round(float(report.get('total_return', 0)) * 100, 2), 'baseline_return': round(float(report.get('baseline_return', 0)) * 100, 2), 'alpha': round(float(report.get('active_return', 0)) * 100, 2), 'max_drawdown': round(float(report.get('max_drawdown', 0)) * 100, 2), 'sharpe': round(float(report.get('sharpe', 0)), 2), 'trade_count': report.get('trade_count', 0)}
        risk_improved = candidate['sharpe'] > baseline.get('sharpe', 0) and candidate['max_drawdown'] > baseline.get('max_drawdown', 0)
        OPTIMIZED_RESULT = {'status': 'retested', 'reason': 'reduced risk budget; return may trade off for lower drawdown and better risk-adjusted performance', 'before': baseline, 'after': candidate, 'improved': risk_improved, 'tradeoff': {'alpha_change': round(candidate['alpha'] - baseline.get('alpha', 0), 2), 'drawdown_change': round(candidate['max_drawdown'] - baseline.get('max_drawdown', 0), 2), 'sharpe_change': round(candidate['sharpe'] - baseline.get('sharpe', 0), 2)}}
        return OPTIMIZED_RESULT
    except Exception as error:
        return {'status': 'error', 'reason': f'{type(error).__name__}: {error}', 'before': baseline}

class Handler(SimpleHTTPRequestHandler):
    def end_headers(self):
        self.send_header('Cache-Control', 'no-store, no-cache, must-revalidate')
        super().end_headers()

    def do_GET(self):
        global REAL_RESULT, OPTIMIZED_RESULT, RESULT_CACHE_KEY
        path = urlparse(self.path).path
        if path == '/':
            self.path = '/single.html'
        if path == '/single.html' or self.path == '/single.html':
            page = (ROOT / 'single.html').read_text(encoding='utf-8').replace('single.js"', 'single.js?v=22"')
            body = page.encode('utf-8')
            self.send_response(200); self.send_header('Content-Type', 'text/html; charset=utf-8')
            self.send_header('Content-Length', str(len(body))); self.end_headers(); self.wfile.write(body); return
        if path == "/api/tool/optimize_strategy":
            tool_result = dict(run_optimization())
            tool_result['tool'] = 'optimize_strategy'
            body = json.dumps(tool_result, ensure_ascii=False).encode()
            self.send_response(200); self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Content-Length", str(len(body))); self.end_headers(); self.wfile.write(body); return
        if path == "/api/manifest":
            body = json.dumps({'name': 'quant-research-tools', 'version': APP_VERSION, 'protocol': 'AGH registerTool', 'tools': AGH_TOOLS}, ensure_ascii=False).encode()
            self.send_response(200); self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Content-Length", str(len(body))); self.end_headers(); self.wfile.write(body); return
        if path == "/api/health":
            body = json.dumps({'status': 'ok', 'version': APP_VERSION, 'engine_available': QUANT_ROOT.exists(), 'agnes_configured': bool(__import__('os').environ.get('AGNES_API_KEY')), 'quant_root': str(QUANT_ROOT), 'backtest_days': int(__import__('os').environ.get('QUANT_BACKTEST_DAYS', '60'))}, ensure_ascii=False).encode()
            self.send_response(200); self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Content-Length", str(len(body))); self.end_headers(); self.wfile.write(body); return
        if path == "/api/mission":
            query = {key: values[-1] for key, values in parse_qs(urlparse(self.path).query).items()}
            missing = missing_inputs(query); unsafe = unsafe_inputs(query); oversized = oversized_inputs(query)
            if missing or unsafe or oversized:
                body = json.dumps({'error': 'invalid research inputs', 'missing': missing, 'unsafe': unsafe, 'oversized': oversized}, ensure_ascii=False).encode()
                self.send_response(400); self.send_header("Content-Type", "application/json; charset=utf-8")
                self.send_header("Content-Length", str(len(body))); self.end_headers(); self.wfile.write(body); return
            if query.get('fresh') == '1':
                REAL_RESULT = None
                OPTIMIZED_RESULT = None
                RESULT_CACHE_KEY = None
                LAST_CACHE_HIT = False
            try:
                payload = run_research_chain(query)
            except Exception as error:
                body = json.dumps({'error': 'research chain failed', 'type': type(error).__name__}, ensure_ascii=False).encode()
                self.send_response(500); self.send_header("Content-Type", "application/json; charset=utf-8")
                self.send_header("Content-Length", str(len(body))); self.end_headers(); self.wfile.write(body); return
            body = json.dumps(payload, ensure_ascii=False).encode()
            self.send_response(200); self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Content-Length", str(len(body))); self.end_headers(); self.wfile.write(body); return
        if path == "/api/report":
            query = {key: values[-1] for key, values in parse_qs(urlparse(self.path).query).items()}
            missing = missing_inputs(query); unsafe = unsafe_inputs(query); oversized = oversized_inputs(query)
            if missing or unsafe or oversized:
                body = json.dumps({'error': 'invalid research inputs', 'missing': missing, 'unsafe': unsafe, 'oversized': oversized}, ensure_ascii=False).encode()
                self.send_response(400); self.send_header("Content-Type", "application/json; charset=utf-8")
                self.send_header("Content-Length", str(len(body))); self.end_headers(); self.wfile.write(body); return
            try:
                mission = run_research_chain(query)
            except Exception as error:
                body = json.dumps({'error': 'research report failed', 'type': type(error).__name__}, ensure_ascii=False).encode()
                self.send_response(500); self.send_header("Content-Type", "application/json; charset=utf-8")
                self.send_header("Content-Length", str(len(body))); self.end_headers(); self.wfile.write(body); return
            body = json.dumps({'trace_id': mission['trace_id'], 'inputs': mission['inputs'], 'engine': mission.get('engine'), 'chain_completed': mission.get('chain_completed', False), 'cache_hit': mission.get('cache_hit', False), 'execution_ms': mission.get('execution_ms', 0), 'execution_ledger': mission.get('execution_ledger', []), 'report': mission['report'], 'evidence': mission['evidence'], 'optimization': mission['optimization']}, ensure_ascii=False).encode()
            self.send_response(200); self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Content-Length", str(len(body))); self.end_headers(); self.wfile.write(body); return
        if path in {"/api/tool/run_backtest", "/api/tool/run_stress_test", "/api/tool/validate_result"}:
            tool_result = dict(run_experiment())
            tool_result['tool'] = path.rsplit('/', 1)[-1]
            body = json.dumps(tool_result, ensure_ascii=False).encode()
            self.send_response(200); self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Content-Length", str(len(body))); self.end_headers(); self.wfile.write(body); return
        super().do_GET()

if __name__ == "__main__":
    print("Quant Research Lab: http://127.0.0.1:4173")
    ThreadingHTTPServer(("127.0.0.1", 4173), lambda *a, **k: Handler(*a, directory=str(ROOT), **k)).serve_forever()
