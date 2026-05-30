---
name: quantdata
description: 量化数据源路由中心 | 支持股票/加密货币/期货/行情查询 | 自动路由到crawldata/westockdata/yfinance/baostock/futu/coingecko
version: 0.3.0
author: quantdata team
tags:
  - stock
  - crypto
  - finance
  - data
  - market
  - quant
  - trading
  - 股票
  - 行情
  - 加密货币
  - 期货
  - 金融
supported_markets:
  - A股（沪深/科创/北交所）
  - 港股
  - 美股
  - 加密货币
  - 全球市场
  - 国际期货
---

# QuantData - 量化数据源路由中心

一站式量化数据查询路由系统，自动识别数据请求并路由到最优的数据源子技能。

## 🚀 快速使用

### 触发关键词

| 数据类型 | 触发词 | 路由目标 |
|---------|-------|---------|
| **A股股票** | A股、平安银行、sh600000、sz000001 | crawldata / westockdata / baostockdata |
| **港股股票** | 港股、腾讯控股、hk00700 | westockdata / futuopendata / yfinancedata |
| **美股股票** | 美股、苹果、AAPL | yfinancedata / westockdata / futuopendata |
| **国际期货** | 黄金、原油、白银、hf_GC、hf_CL | crawldata / yfinancedata |
| **加密货币** | BTC、比特币、ETH、以太坊、加密货币 | coingeckodata / okxdata / binancedata / yfinancedata |
| **K线数据** | K线、kline、日线、周线、月线 | 根据市场自动路由 |
| **实时行情** | 行情、实时、quote、价格 | crawldata / westockdata / futuopendata |
| **财务报表** | 财报、财务报表、profit | baostockdata / yfinancedata |
| **资金流向** | 资金、资金流向 | westockdata |
| **龙虎榜** | 龙虎榜、lhb | westockdata |
| **期权数据** | 期权、option | yfinancedata / futuopendata |
| **宏观经济** | 宏观、CPI、PPI、PMI、GDP、利率、货币供应量 | macrodata ⭐ | baostockdata |
| **经济日历** | 经济日历、数据发布、事件 | macrodata（浏览器） | — |
| **政策动态** | 政策、央行、监管 | macrodata（浏览器） | — |

### 示例查询

```
✅ 查询 AAPL 股价
✅ 查询 腾讯控股 K线
✅ 查询 BTC 价格
✅ 查询 黄金 价格
✅ 查询 原油 价格
✅ 查询 平安银行 财报
✅ 查询 苹果公司 期权
✅ 查询 港股 实时行情
```

## 📦 子技能清单

### 已安装子技能

| 子技能 | 数据类型 | 市场覆盖 | 优势 |
|--------|---------|---------|------|
| **crawldata** | 腾讯财经爬虫 | A股/指数/国际期货 | 无限制、全字段解析、快速 |
| **westockdata** | 腾讯自选股 | A股/港股/美股 | 实时行情、技术指标 |
| **baostockdata** | 证券宝 | A股 | 1990年至今历史数据、无限制 |
| **yfinancedata** | Yahoo Finance | 美股/全球/加密 | 财务报表、期权、分析师预期 |
| **futuopendata** | 富途OpenAPI | 港股/美股/A股 | Level 2摆盘、逐笔成交 |
| **coingeckodata** | CoinGecko | 10,000+加密货币 | 免费无API Key |
| **okxdata** | OKX交易所 | 加密货币 | OKX全量API、模拟盘 |
| **binancedata** | 币安交易所 | 加密货币 | WebSocket推送 |
| **ccxtdata** | CCXT | 100+加密货币交易所 | 统一API，一站式行情 |
| **macrodata** | 宏观数据 | 中国/美国/全球 | 爬虫采集 + AKShare 兜底 + 浏览器 |
| **analystdata** | akshare | A股 | 分析师一致预期(盈利预测+评级分布) |
| **corpdata** | akshare | A股 | 增减持、定向增发 |

详细的路由规则和数据源对比，请查阅 [ROUNTING.md](file:///d:/src/trading-skills/quantdata/ROUNTING.md)

## 🎯 路由规则

### 1. 按市场类型路由

| 市场类型 | 识别特征 | 优先数据源 | 备选数据源 |
|---------|---------|-----------|-----------|
| **A股** | `sh`/`sz`前缀、6位数字 | crawldata | westockdata / baostockdata / futuopendata |
| **港股** | `hk`前缀、5位数字 | westockdata | futuopendata / yfinancedata |
| **美股** | 纯字母、NYSE/NASDAQ | yfinancedata | westockdata / futuopendata |
| **国际期货** | `hf_`前缀、黄金/原油/白银 | crawldata | yfinancedata |
| **加密货币** | BTC/ETH/币安/OKX | coingeckodata / ccxtdata | okxdata / binancedata / yfinancedata |

### 2. 按数据类型路由

| 数据类型 | 识别关键词 | 优先数据源 |
|---------|----------|-----------|
| **实时行情** | `行情`、`quote`、`实时`、`价格` | crawldata / westockdata / futuopendata |
| **K线数据** | `K线`、`kline`、`日线`、`分钟` | 按市场路由 |
| **财务报表** | `财报`、`财务`、`finance`、`利润表` | baostockdata / yfinancedata |
| **资金流向** | `资金`、`流向`、`fund` | westockdata |
| **技术指标** | `指标`、`MACD`、`RSI`、`KDJ` | westockdata |
| **期权数据** | `期权`、`option`、`call`、`put` | yfinancedata / futuopendata |
| **宏观经济** | `宏观`、`利率`、`货币供应量`、`存款准备金` | baostockdata |
| **分析师预期** | `研报`、`分析师`、`一致预期`、`forecast`、`评级` | analystdata |
| **公司事件** | `增减持`、`定增`、`增发`、`股东`、`share_change` | corpdata |
| **加密货币** | `BTC`、`ETH`、`比特币`、`以太坊` | ccxtdata / coingeckodata |

## 🔄 自动重试机制

QuantData 内置智能重试机制，确保数据获取可靠性：

- **最大重试次数**：3次
- **重试间隔**：1秒 → 2秒 → 4秒（指数退避）
- **超时时间**：30秒
- **自动降级**：主数据源失败时自动切换备选数据源

**触发条件**：网络失败、超时、服务端错误（5xx）、限流（429）

## 📖 使用指南

### 基本查询

```
输入：查一下 AAPL 股价
输出：自动路由到 yfinancedata 查询

输入：腾讯控股 K线
输出：自动路由到 westockdata / futuopendata

输入：BTC 价格
输出：自动路由到 coingeckodata
```

### 批量查询

```
输入：查询 平安银行、招商银行、浦发银行 K线
输出：自动路由到 baostockdata 批量查询
```

### 跨市场查询

```
输入：对比 腾讯控股(港股) 和 苹果(美股) 的数据
输出：分别路由到 westockdata 和 yfinancedata
```

## 💡 数据选择建议

| 需求场景 | 推荐数据源 | 原因 |
|---------|----------|------|
| **A股实时行情** | crawldata | 快速无限制、全字段 |
| **A股历史回测** | baostockdata | 1990年至今、无限制 |
| **国际期货** | crawldata | 黄金/原油/白银实时价格 |
| **港股实时** | futuopendata / westockdata | Level 2、逐笔 |
| **美股数据** | yfinancedata | 最完整、期权/分析师预期 |
| **加密货币** | ccxtdata | 100+交易所统一行情 |
| **财务报表** | baostockdata / yfinancedata | 数据完整 |
| **技术指标** | westockdata | 直接提供 |

详细的路由规则和数据源对比，请查阅 [ROUNTING.md](file:///d:/src/trading-skills/quantdata/ROUNTING.md)

## ⚙️ 配置

### 环境要求

- Python 3.6+
- requests 库
- 至少一个可用的数据源子技能

### 扩展新数据源

1. 在 `quantdata/` 创建新技能目录
2. 编写符合规范的 SKILL.md
3. 在 `ROUNTING.md` 注册路由规则
4. 在本文档更新子技能清单

## 📝 版本历史

### v0.5.0 (2026-05-21)
- 新增：analystdata A股分析师一致预期（盈利预测 + 评级分布）
- 新增：corpdata A股公司事件（增减持 + 定向增发）
- 新增：macrodata 融资融券余额、恐贪指数
- 新增：macrodata VIX/DXY 超时配置（--timeout 参数）
- 更新：Vibe-Trading Skill 完整数据路由映射表

### v0.4.0 (2026-05-21)
- 新增：ccxtdata CCXT统一加密货币数据源
- 新增：支持100+加密货币交易所行情
- 更新：加密货币路由优先级 ccxtdata > coingeckodata
- 优化：加密货币路由规则，支持资金费率/深度数据

### v0.3.0 (2026-05-07)
- 新增：crawldata 腾讯财经爬虫数据源
- 新增：支持国际期货（黄金/原油/白银等）
- 优化：A股实时行情优先使用 crawldata
- 优化：完整字段解析（买卖五档、成交量、成交额等）

### v0.2.0 (2026-05-06)
- 新增：coingeckodata/okxdata/binancedata 加密货币数据源
- 优化：更清晰的触发关键词和路由规则
- 优化：增加快速使用示例

### v0.1.0
- 初始版本，支持 westockdata/baostockdata/yfinancedata/futuopendata

## ⚠️ 免责声明

- 数据仅供参考，不构成投资建议
- 投资有风险，决策需谨慎
- 请以交易所官方数据为准

## 💬 自然语言查询示例

QuantData 支持多种自然语言查询方式：

| 查询方式 | 示例 | 路由目标 |
|---------|------|---------|
| **代码查询** | `sh600000`、`hk00700`、`AAPL`、`BTC` | 按代码前缀自动识别市场 |
| **名称查询** | `茅台`、`腾讯`、`苹果`、`比特币` | 模糊匹配后路由 |
| **资产类型** | `黄金`、`原油`、`白银`、`小麦` | crawldata / yfinancedata |
| **数据指标** | `涨跌幅`、`成交量`、`市值`、`市盈率` | 自动附加到查询 |
| **时间范围** | `最近一年`、`2023年`、`近一个月` | 自动转换为日期参数 |
| **组合查询** | `腾讯控股 股价 + K线 + 成交量` | 批量路由到对应数据源 |

### 常用自然语言模式

```
✅ "帮我查下" + 股票代码/名称 → 实时行情
✅ "最近走势" + 股票代码 → K线数据
✅ "历史数据" + 股票代码 + 时间范围 → 历史K线
✅ "财报" + 公司名称 → 财务报表
✅ "资金流向" + 股票代码 → westockdata
```
## 🔧 常见问题排查

| 问题 | 原因 | 解决方案 |
|-----|------|---------|
| **路由失败** | 股票代码/名称无法识别 | 尝试使用完整代码（如 sh600000）或明确市场（如 A股茅台） |
| **数据为空** | 代码已下市或停牌 | 检查代码有效性，或切换到备选数据源 |
| **超时错误** | 数据源响应慢 | 等待后重试，系统会自动降级到备选源 |
| **字段缺失** | 数据源不支持该字段 | 尝试切换到其他数据源（如 westockdata → baostockdata） |
| **加密货币查不到** | 交易对格式错误 | 使用标准格式如 `BTC/USDT`，避免空格和特殊字符 |

**提示**：遇到数据问题时，优先尝试 `westockdata` 作为备选方案，它对A股/港股/美股的覆盖最全面。