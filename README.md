# Quant Research Lab

提交演示前请先看 [SUBMISSION_CHECKLIST.md](SUBMISSION_CHECKLIST.md)。

面向 Agnes Harness 黑客松的量化研究智能体演示切片。

这个示例把 TradingAgents 的分析师、研究辩论、交易员、风控与组合经理流程，映射成 AGH 可以编排和留痕的研究任务：

```text
研究问题 → 市场数据 → 多智能体分析 → 多空辩论 → 策略回测 → 压力测试 → 基线验证 → 实验报告
```

当前目录提供一个无需 API Key 的可交互演示界面。`GET /api/mission` 会优先调用原量化项目的离线 `MarketEnv/TradingBacktestEngine`；原项目不可用时才使用固定随机种子的本地降级回测。

默认真实回测窗口为 60 个交易日，完成后会在当前服务进程内按“交易周期 + 股票类型 + 风险偏好”缓存结果；更换任一输入都会触发新任务，可用 `QUANT_BACKTEST_DAYS` 调整窗口。

`agnes_client.py` 提供真实 Agnes API 的可选适配层：Key 只从运行时环境变量 `AGNES_API_KEY` 读取，默认使用 `agnes-2.5-flash` 和官方 OpenAI-compatible endpoint。没有 Key 时，演示仍可使用本地确定性回测模式。

## 运行

在本目录启动研究后端：

```powershell
python server.py
```

配置真实模型时：

```powershell
pip install openai
$env:AGNES_API_KEY = "<本地Key>"
python -c "from agnes_client import ask; print(ask('请用一句话说明你的研究职责。'))"
```

打开 <http://127.0.0.1:4173/>。

快速回归检查：

```powershell
python smoke_test.py
python api_smoke_test.py
```

`GET /api/health` 返回服务版本、服务状态、本地引擎可用性、`agnes_configured`（是否设置 `AGNES_API_KEY`）和回测窗口；`GET /api/manifest` 返回当前注册的 8 个 AGH 工具。一次 mission 会产生 9 个账本节点，其中 `mission_router` 是编排节点，另外 8 个对应注册工具。

`GET /api/report` 返回结构化报告、Trace ID、`cache_hit`、9 节点 `execution_ledger`、整链 `execution_ms`、evidence board 和优化前后结果，适合提交材料或二次集成。

`/api/mission` 和 `/api/report` 缺少 `period`、`universe` 或 `risk`，约束包含标签字符，或单字段超过 256 个字符时返回 HTTP 400，并列出 `missing`/`unsafe`/`oversized` 字段；服务不会用空约束生成默认研究。

如果后端或网络调用失败，页面会显示 `REVIEW` 和错误原因，不会使用默认收益指标伪装成成功回测。

任务结果还包含 `evidence` 数组；每条证据都有 `claim`、`support` 和 `status`，页面会将其渲染为可质询的 evidence board。

## 与 AGH 的接入边界

当前后端插件实现以下工具，并让 AGH 记录每次调用：

- `load_market_data`
- `run_analyst_team`
- `run_research_debate`
- `run_backtest`
- `run_stress_test`
- `validate_result`
- `optimize_strategy`
- `generate_experiment_report`

原量化项目位于 `F:/南大/南大/暑期学校/炒股/NJU-BigMining-L2A/assignment-a-trading-agent`，可将其行情、回测和风控模块作为这些工具的实现来源。
