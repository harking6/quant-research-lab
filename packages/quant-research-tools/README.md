# Quant Research Tools

AGH backend plugin for the Quant Research Lab. It exposes the research loop as eight read-only, replay-safe tools:

`load_market_data` → `run_analyst_team` → `run_research_debate` → `run_backtest` → `run_stress_test` → `validate_result` → `optimize_strategy` → `generate_experiment_report`.

The current implementation is deterministic and self-contained so the plugin can be verified without market credentials. Set `QUANT_ENGINE_URL=http://127.0.0.1:4173` to make the backtest, stress-test, and validation tools call the local research backend; if it is unavailable, each tool returns a marked fallback result.

Run `node contract_test.mjs` with `QUANT_ENGINE_URL` for the live-backend contract, or add `EXPECT_FALLBACK=1` with an unavailable URL to verify the marked fallback path.
