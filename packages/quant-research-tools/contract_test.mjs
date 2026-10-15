import { quantResearchTools } from './index.mjs'

const registered = {}
const context = {
  extension: () => ({
    registerTool: ({ name, execute }) => { registered[name] = execute },
    on: () => {},
    ctx: { log: { info: () => {} } },
  }),
}

quantResearchTools.apply(context)
if (Object.keys(registered).length !== 8) throw new Error('expected 8 registered tools')

const result = await registered.run_backtest({ symbol: 'DEMO', warmup_days: 60 })
const payload = JSON.parse(result.content[0].text)
if (payload.tool !== 'run_backtest') throw new Error('tool identity missing')
const expectFallback = process.env.EXPECT_FALLBACK === '1' || !process.env.QUANT_ENGINE_URL
if (expectFallback !== Boolean(payload.backend_fallback)) throw new Error(`fallback expectation mismatch: expected=${expectFallback}`)
console.log(JSON.stringify({ tools: Object.keys(registered).length, tool: payload.tool, fallback: Boolean(payload.backend_fallback), engine: payload.engine || 'fallback' }))
