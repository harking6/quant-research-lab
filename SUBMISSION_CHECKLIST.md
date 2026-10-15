# Quant Research Lab 提交前检查

## 启动

```powershell
$env:QUANT_BACKTEST_DAYS = "60"
$env:QUANT_PROJECT_ROOT = "F:\南大\南大\暑期学校\炒股\NJU-BigMining-L2A\assignment-a-trading-agent"
python server.py
```

打开 `http://127.0.0.1:4173/`，输入交易周期、股票类型和风险偏好，点击“生成研究方案”。

## 演示验收点

- 9 个执行节点依次出现，并回填工具账本状态。
- 结果区域展示 Trace ID、缓存状态、证据板和整链耗时。
- `/api/report?...` 返回 `execution_ledger`、`execution_ms`、`cache_hit` 和统一 Trace ID。
- `/api/health` 的 `engine_available` 为 `true`，`/api/manifest` 返回 8 个 AGH 工具。
- 空参数、标签字符和超过 256 字符的约束应返回 HTTP 400；fallback 必须带有明确状态和错误原因。
- 研究链异常应返回结构化 JSON 错误，前端显示 `REVIEW`，不得伪造收益指标。

## 回归命令

```powershell
python smoke_test.py
python api_smoke_test.py
# 可选：验证其他服务地址
$env:QUANT_ENGINE_URL = "http://127.0.0.1:4173"
python api_smoke_test.py
cd ..\packages\quant-research-tools
npm test
$env:QUANT_ENGINE_URL = "http://127.0.0.1:4173"
npm test
```

若后端不可用，插件应明确返回 `status: fallback`、`backend_fallback: true` 和 `backend_error`，不得把 fallback 当成真实验证结果。
