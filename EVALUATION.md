# 自评审记录

| 维度 | 当前证据 | 结论 |
| --- | --- | --- |
| 真实性 | 正式 60 日 `TradingBacktestEngine`；`run_backtest` 有实际耗时 | 通过 |
| 工具接入 | manifest 8 工具；插件源码 8 个 `registerTool`；9 节点账本 | 通过 |
| 可追溯 | Trace ID、逐节点耗时、tool/status、evidence board | 通过 |
| 可复现 | 固定 seed、输入缓存隔离、smoke test、报告 checks | 通过 |
| 容错 | fallback 引擎、REVIEW 状态、失败原因、健康检查 | 通过 |
| 展示 | 单页输入、动态自定义股票池、九节点流程、优化前后证据 | 通过 |

## 已知边界

- 未配置 `AGNES_API_KEY` 时使用本地真实离线引擎；`/api/health` 会明确标记 `agnes_configured=false`。
- 市场数据当前使用离线/确定性数据源，适合比赛复现，不代表实时投资建议。
- 缓存按交易周期、股票类型和风险偏好隔离；点击强制重跑可重新计算。

## 回归命令

```powershell
python smoke_test.py
```
