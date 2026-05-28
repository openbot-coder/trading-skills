---
name: ccxtdata
description: CCXT统一加密货币数据接口 | 100+交易所 | 支持实时行情/K线/深度/资金费率/成交记录
version: 1.0.0
author: CCXT / Igor Kroitor
tags:
  - cryptocurrency
  - ccxt
  - exchange
  - crypto-api
  - unified-api
supported_markets:
  - 100+加密货币交易所（Binance/OKX/Bybit/Coinbase/Kraken等）
  - 现货/永续合约/交割合约/期权
disable-model-invocation: true
---

# CCXT Data - 统一加密货币数据接口

基于 [CCXT](https://github.com/ccxt/ccxt) 库，一套代码访问 100+ 加密货币交易所。

## 核心定位

**CCXT Data** 是加密货币数据路由的首选数据源，提供：

1. **统一接口**：100+ 交易所用同一套 API
2. **免认证查询**：行情/K线/深度/成交无需 API Key
3. **全品种覆盖**：现货、永续合约、交割合约、期权
4. **异步支持**：`ccxt.async_support` 高并发采集

## 支持的交易所（常用）

| 交易所 | ID | 说明 |
|--------|-----|------|
| Binance | `binance` | 全球最大，600+ 交易对 |
| OKX | `okx` | 国际版，全品种 |
| Bybit | `bybit` | 永续合约为主 |
| Coinbase | `coinbase` | 美国合规 |
| Kraken | `kraken` | 欧洲老牌 |
| Bitget | `bitget` | 跟单交易 |
| Gate.io | `gate` | 山寨币丰富 |
| HTX (火币) | `htx` | 原火币 |
| KuCoin | `kucoin` | 山寨币平台 |
| Bitfinex | `bitfinex` | 专业交易 |

完整列表：`python3 -c "import ccxt; print(len(ccxt.exchanges))"` → 100+

## 命令用法

所有命令格式：`python3 {base}/scripts/ccxt_data.py <command> [options]`

### ticker — 实时行情

```bash
python3 {base}/scripts/ccxt_data.py ticker BTC/USDT
python3 {base}/scripts/ccxt_data.py ticker ETH/USDT --exchange okx
python3 {base}/scripts/ccxt_data.py ticker BTC/USDT:USDT --exchange binance  # 永续合约
```

输出：最新价、24h涨跌、24h高低、24h成交量

### kline — K线数据

```bash
python3 {base}/scripts/ccxt_data.py kline BTC/USDT --timeframe 1h --limit 100
python3 {base}/scripts/ccxt_data.py kline ETH/USDT --exchange okx --timeframe 1d --limit 30
```

timeframe 支持：`1m/5m/15m/30m/1h/4h/1d/1w/1M`

输出：CSV 格式，列 = timestamp, open, high, low, close, volume

### depth — 订单簿深度

```bash
python3 {base}/scripts/ccxt_data.py depth BTC/USDT --limit 10
python3 {base}/scripts/ccxt_data.py depth ETH/USDT --exchange okx --limit 20
```

输出：买/卖盘各 N 档价格+数量，买卖总量及比率

### funding — 资金费率

```bash
python3 {base}/scripts/ccxt_data.py funding BTC/USDT:USDT
python3 {base}/scripts/ccxt_data.py funding ETH/USDT:USDT --exchange bybit
```

输出：当前资金费率、下一个结算时间、预测费率

### trades — 最近成交

```bash
python3 {base}/scripts/ccxt_data.py trades BTC/USDT --limit 20
python3 {base}/scripts/ccxt_data.py trades ETH/USDT --exchange okx --limit 10
```

输出：时间、方向、价格、数量

### exchanges — 列出支持的交易所

```bash
python3 {base}/scripts/ccxt_data.py exchanges
```

输出：所有支持的交易所 ID 列表

### markets — 列出交易所市场

```bash
python3 {base}/scripts/ccxt_data.py markets
python3 {base}/scripts/ccxt_data.py markets --exchange okx
```

输出：交易对列表（symbol）、类型（spot/future/swap）

## 路由优先级

在 quantdata 路由体系中，ccxtdata 是加密货币的**首选数据源**：

| 场景 | 首选 | 备选 |
|------|------|------|
| 加密货币行情 | ccxtdata ⭐ | binancedata / okxdata |
| 加密货币K线 | ccxtdata ⭐ | binancedata / okxdata |
| 加密货币深度 | ccxtdata ⭐ | binancedata / okxdata |
| 资金费率 | ccxtdata ⭐ | binancedata / okxdata |
| 单交易所深度 | binancedata / okxdata | ccxtdata |
| 免费聚合行情 | coingeckodata | ccxtdata |

## 与单交易所数据源对比

| 特性 | CCXT | Binance | OKX | CoinGecko |
|------|------|---------|-----|-----------|
| **交易所数** | 100+ | 1 | 1 | 聚合 |
| **统一接口** | ✅ | ❌ | ❌ | ✅ |
| **永续合约** | ✅ | ✅ | ✅ | ❌ |
| **资金费率** | ✅ | ✅ | ✅ | ❌ |
| **深度数据** | ✅ | ✅ | ✅ | ❌ |
| **无需Key** | ✅(行情) | ✅ | ✅ | ✅ |
| **实时性** | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ |

## 依赖

- `ccxt` >= 4.0（`pip install ccxt`）
- `pandas`（K线输出用）

## 注意事项

- 公共行情接口无需 API Key，直接可用
- 部分交易所可能需要代理（网络问题）
- 永续合约 symbol 格式：`BTC/USDT:USDT`（币本位用 `BTC/USD:BTC`）
- 限流因交易所而异，一般 10-20 次/秒
