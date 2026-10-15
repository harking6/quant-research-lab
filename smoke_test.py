"""Fast, credential-free regression test for the local research chain."""
import os
from pathlib import Path

os.environ['QUANT_PROJECT_ROOT'] = r'C:\path\that\does\not\exist'

import server


def main() -> None:
    result = server.run_research_chain({
        'period': 'smoke',
        'universe': 'smoke-universe',
        'risk': 'balanced',
    })
    tools = [entry['tool'] for entry in result['execution_ledger']]
    expected = [
        'mission_router', 'load_market_data', 'run_analyst_team',
        'run_research_debate', 'run_backtest', 'run_stress_test',
        'validate_result', 'optimize_strategy', 'generate_experiment_report',
    ]
    assert result['chain_completed'] is True
    assert result['execution_ms'] >= 0
    assert result['engine'] == 'deterministic-fallback'
    assert tools == expected, tools
    assert result['report']['reproducible'] is True
    assert len(result['report']['checks']) == 3
    assert len(result['evidence']) == 3
    assert all({'claim', 'support', 'status'} <= set(item) for item in result['evidence'])
    plugin_source = (Path(__file__).resolve().parents[1] / 'packages' / 'quant-research-tools' / 'index.mjs').read_text(encoding='utf-8')
    assert len(server.AGH_TOOLS) == 8
    assert all(f"register('{tool}'" in plugin_source for tool in server.AGH_TOOLS)
    assert result['trace_id'].startswith('agh-qrl-')
    assert result['report']['trace_id'] == result['trace_id']
    cached = server.run_research_chain({'period': 'smoke', 'universe': 'smoke-universe', 'risk': 'balanced'})
    assert cached['cache_hit'] is True
    refreshed = server.run_research_chain({'period': 'smoke', 'universe': 'smoke-universe', 'risk': 'balanced', 'fresh': '1'})
    assert refreshed['cache_hit'] is False
    print('smoke test passed: 9-node fallback chain, report, trace, optimization')


if __name__ == '__main__':
    main()
