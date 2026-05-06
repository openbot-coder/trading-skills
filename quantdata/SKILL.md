---
name: quantdata
description: 量化数据源路由中心 | 支持股票/加密货币/行情查询 | 自动路由到westockdata/yfinance/baostock/futu/coingecko
version: 0.2.0
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
  - 金融
supported_markets:
  - A股（沪深/科创/北交所）
  - 港股
  - 美股
  - 加密货币
  - 全球市场
---

# QuantData - 量化数据源路由中心

一站式量化数据查询路由系统，自动识别数据请求并路由到最优的数据源子技能。

## 🚀 快速使用

### 触发关键词

| 数据类型 | 触发词 | 路由目标 |
|---------|-------|---------|
| **A股股票** | A股、平安银行、sh600000、sz000001 | westockdata / baostockdata |
| **港股股票** | 港股、腾讯控股、hk00700 | westockdata / futuopendata / yfinancedata |
| **美股股票** | 美股、苹果、AAPL | yfinancedata / westockdata / futuopendata |
| **加密货币** | BTC、比特币、ETH、以太坊、加密货币 | coingeckodata / okxdata / binancedata / yfinancedata |
| **K线数据** | K线、kline、日线、周线、月线 | 根据市场自动路由 |
| **实时行情** | 行情、实时、quote、价格 | westockdata / futuopendata |
| **财务报表** | 财报、财务报表、profit | baostockdata / yfinancedata |
| **资金流向** | 资金、资金流向 | westockdata |
| **龙虎榜** | 龙虎榜、lhb | westockdata |
| **期权数据** | 期权、option | yfinancedata / futuopendata |
| **宏观经济** | 宏观、利率、货币供应量 | baostockdata |

### 示例查询

```
✅ 查询 AAPL 股价
✅ 查询 腾讯控股 K线
✅ 查询 BTC 价格
✅ 查询 平安银行 财报
✅ 查询 苹果公司 期权
✅ 查询 港股 实时行情
```

## 📦 子技能清单

### 已安装子技能

| 子技能 | 数据类型 | 市场覆盖 | 优势 |
|--------|---------|---------|------|
| **westockdata** | 腾讯自选股 | A股/港股/美股 | 实时行情、技术指标 |
| **baostockdata** | 证券宝 | A股 | 1990年至今历史数据、无限制 |
| **yfinancedata** | Yahoo Finance | 美股/全球/加密 | 财务报表、期权、分析师预期 |
| **futuopendata** | 富途OpenAPI | 港股/美股/A股 | Level 2摆盘、逐笔成交 |
| **coingeckodata** | CoinGecko | 10,000+加密货币 | 免费无API Key |
| **okxdata** | OKX交易所 | 加密货币 | OKX全量API、模拟盘 |
| **binancedata** | 币安交易所 | 加密货币 | WebSocket推送 |

详细的路由规则和数据源对比，请查阅 [ROUNTING.md](file:///d:/src/trading-skills/quantdata/ROUNTING.md)

## 🎯 路由规则

### 1. 按市场类型路由

| 市场类型 | 识别特征 | 优先数据源 | 备选数据源 |
|---------|---------|-----------|-----------|
| **A股** | `sh`/`sz`前缀、6位数字 | westockdata | baostockdata / futuopendata |
| **港股** | `hk`前缀、5位数字 | westockdata | futuopendata / yfinancedata |
| **美股** | 纯字母、NYSE/NASDAQ | yfinancedata | westockdata / futuopendata |
| **加密货币** | BTC/ETH/币安/OKX | coingeckodata | okxdata / binancedata / yfinancedata |

### 2. 按数据类型路由

| 数据类型 | 识别关键词 | 优先数据源 |
|---------|----------|-----------|
| **实时行情** | `行情`、`quote`、`实时`、`价格` | westockdata / futuopendata |
| **K线数据** | `K线`、`kline`、`日线`、`分钟` | 按市场路由 |
| **财务报表** | `财报`、`财务`、`finance`、`利润表` | baostockdata / yfinancedata |
| **资金流向** | `资金`、`流向`、`fund` | westockdata |
| **技术指标** | `指标`、`MACD`、`RSI`、`KDJ` | westockdata |
| **期权数据** | `期权`、`option`、`call`、`put` | yfinancedata / futuopendata |
| **宏观经济** | `宏观`、`利率`、`货币供应量`、`存款准备金` | baostockdata |
| **加密货币** | `BTC`、`ETH`、`比特币`、`以太坊` | coingeckodata |

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
| **A股实时行情** | westockdata | 快速无限制 |
| **A股历史回测** | baostockdata | 1990年至今、无限制 |
| **港股实时** | futuopendata / westockdata | Level 2、逐笔 |
| **美股数据** | yfinancedata | 最完整、期权/分析师预期 |
| **加密货币** | coingeckodata | 免费无API Key |
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
