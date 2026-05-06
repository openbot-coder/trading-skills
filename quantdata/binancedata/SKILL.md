---
name: binancedata
description: Binance币安API | 加密货币实时行情 | 支持600+交易对
version: 1.0.0
author: Binance
tags:
  - cryptocurrency
  - binance
  - exchange
  - crypto-api
supported_markets:
  - Binance加密货币交易所
  - USDT合约
  - 币本位合约
---

# Binance Data - 币安交易所加密货币数据专家

Binance官方API，支持600+加密货币交易对。

## 核心定位

**Binance Data** 是一个专注于币安交易所的数据源，提供：

1. **海量交易对**：600+加密货币交易对
2. **REST API**：简单易用的HTTP接口
3. **WebSocket**：实时数据推送
4. **官方SDK**：Python-binance库支持
5. **交易功能**：下单、撤单、账户

## 核心优势

| 特性 | 说明 |
|------|------|
| **交易对丰富** | 600+交易对 |
| **实时行情** | 毫秒级实时数据 |
| **WebSocket** | 实时数据推送 |
| **官方SDK** | python-binance库支持 |
| **无需注册** | 公开数据接口免费 |
| **REST API** | 简单易用 |

## 安装

### python-binance库

```bash
pip install python-binance
```

### 验证安装

```python
from binance.client import Client
client = Client()
print(client.get_exchange_info())
```

## 快速开始

### 基础使用流程

```python
from binance.client import Client

# 创建客户端
client = Client()

# 获取BTC价格
btc_price = client.get_symbol_ticker(symbol="BTCUSDT")
print(btc_price)
```

### 基本查询示例

#### 1. 获取实时价格

```python
from binance.client import Client

client = Client()

# 获取BTC/USDT价格
btc_price = client.get_symbol_ticker(symbol="BTCUSDT")
print(f"BTC价格: {btc_price['price']}")

# 获取多个价格
prices = client.get_all_tickers()
for ticker in prices[:5]:
    print(f"{ticker['symbol']}: {ticker['price']}")
```

#### 2. 获取K线数据

```python
from binance.client import Client
import pandas as pd

client = Client()

# 获取BTC历史K线
klines = client.get_klines(symbol="BTCUSDT", interval="1h", limit=100)
print(klines)
```

#### 3. 获取订单簿深度

```python
from binance.client import Client

client = Client()

# 获取订单簿
depth = client.get_order_book(symbol="BTCUSDT", limit=10)
print("买家出价:")
print(depth['bids'])
print("\n卖家要价:")
print(depth['asks'])
```

#### 4. 获取成交记录

```python
from binance.client import Client

client = Client()

# 获取最近成交
trades = client.get_recent_trades(symbol="BTCUSDT")
print(trades[:5])
```

## 交易对代码

### 常用交易对

| 交易对 | 代码 | 说明 |
|--------|------|------|
| BTC/USDT | BTCUSDT | 比特币 |
| ETH/USDT | ETHUSDT | 以太坊 |
| BNB/USDT | BNBUSDT | 币安币 |
| SOL/USDT | SOLUSDT | Solana |
| XRP/USDT | XRPUSDT | Ripple |
| ADA/USDT | ADAUSDT | Cardano |
| DOGE/USDT | DOGEUSDT | Dogecoin |
| DOT/USDT | DOTUSDT | Polkadot |
| LINK/USDT | LINKUSDT | Chainlink |
| LTC/USDT | LTCUSDT | Litecoin |

### 合约交易对

| 交易对 | 代码 | 说明 |
|--------|------|------|
| BTC/USDT永续 | BTCUSDT_PERP | 比特币永续合约 |
| ETH/USDT永续 | ETHUSDT_PERP | 以太坊永续合约 |
| SOL/USDT永续 | SOLUSDT_PERP | Solana永续合约 |

## API参考

### 1. 市场数据接口

#### 获取价格

```python
from binance.client import Client

client = Client()

# 单个交易对价格
price = client.get_symbol_ticker(symbol="BTCUSDT")

# 所有交易对价格
all_prices = client.get_all_symbol_ticker()

# 24h价格变动
ticker = client.get_ticker(symbol="BTCUSDT")
```

#### K线数据

```python
# 日K线
klines = client.get_klines(symbol="BTCUSDT", interval="1d", limit=30)

# 1小时K线
hourly_klines = client.get_klines(symbol="BTCUSDT", interval="1h", limit=100)

# 15分钟K线
minute_klines = client.get_klines(symbol="BTCUSDT", interval="15m", limit=200)
```

参数：
- **symbol**: 交易对符号（大写）
- **interval**: K线周期
- **limit**: 返回条数（最大1000）

#### K线周期

| 周期 | 代码 |
|------|------|
| 1分钟 | 1m |
| 5分钟 | 5m |
| 15分钟 | 15m |
| 30分钟 | 30m |
| 1小时 | 1h |
| 4小时 | 4h |
| 1天 | 1d |
| 1周 | 1w |
| 1个月 | 1M |

### 2. 订单簿数据

```python
from binance.client import Client

client = Client()

# 获取订单簿
order_book = client.get_order_book(symbol="BTCUSDT", limit=10)

print("买一价:")
print(order_book['bids'][0])

print("\n卖一价:")
print(order_book['asks'][0])
```

### 3. 成交记录

```python
from binance.client import Client

client = Client()

# 最近成交
trades = client.get_recent_trades(symbol="BTCUSDT", limit=50)

for trade in trades[:5]:
    print(f"价格: {trade['price'], 数量: {trade['qty']}, 时间: {trade['time']}")
```

### 4. 24h统计

```python
from binance.client import Client

client = Client()

# 24h统计数据
stats = client.get_ticker(symbol="BTCUSDT")
print(f"24h最高: {stats['highPrice']}")
print(f"24h最低: {stats['lowPrice']}")
print(f"24h成交量: {stats['volume']}")
print(f"24h涨跌: {stats['priceChange']}%")
```

### 5. 账户信息（需要API Key）

```python
from binance.client import Client

# 需要API Key
api_key = "your_api_key"
api_secret = "your_api_secret"
client = Client(api_key, api_secret)

# 账户余额
account = client.get_account()
print(account['balances'])
```

### 6. 下单（需要API Key）

```python
from binance.client import Client

client = Client(api_key, api_secret)

# 市价买单
order = client.order_market_buy(symbol="BTCUSDT", quantity=0.001)

# 限价单
order = client.order_limit_buy(
    symbol="BTCUSDT",
    quantity=0.001,
    price="50000"
)
```

## WebSocket实时数据

### 安装websocket-client

```bash
pip install websocket-client
```

### 实时价格订阅

```python
from binance.websockets import BinanceSocketManager

client = Client()
bm = BinanceSocketManager(client)
bm.start_trade_socket('BTCUSDT', process_message)
bm.start()
```

## 限流说明

### 公开接口限流

| 接口 | 限流 |
|------|------|
| 市场数据 | 1200次/分钟 |
| 账户数据 | 10次/秒 |
| 下单 | 10次/秒 |

### 最佳实践

```python
import time
from binance.client import Client

client = Client()

def rate_limited_get_price(symbols):
    """限流处理的价格获取"""
    results = []
    for i, symbol in enumerate(symbols):
        try:
            price = client.get_symbol_ticker(symbol=symbol)
            results.append(price)
            
            # 每秒最多10个请求
            if (i + 1) % 10 == 0:
                time.sleep(1)
        except Exception as e:
            print(f"Error for {symbol}: {e}")
    return results
```

## 与其他数据源对比

| 特性 | Binance | CoinGecko | OKX |
|------|----------|------------|------|
| **交易所** | 币安 | 全球聚合 | OKX |
| **交易对** | 600+ | 10,000+ | 全市场 |
| **实时性** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| **免费程度** | 公开接口免费 | 免费 | 合理限额 |
| **SDK支持** | ⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| **WebSocket** | ✅ | ❌ | ✅ |

## 使用场景

### 1. 实时行情监控

```python
from binance.client import Client

client = Client()

symbols = ["BTCUSDT", "ETHUSDT", "BNBUSDT", "SOLUSDT"]

print("=== 实时价格监控 ===")
for symbol in symbols:
    ticker = client.get_symbol_ticker(symbol=symbol)
    price = float(ticker['price'])
    print(f"{symbol:10} ${price:>15.2f}")
```

### 2. 技术指标计算

```python
import pandas as pd
from binance.client import Client

client = Client()

# 获取K线数据
klines = client.get_klines(symbol="BTCUSDT", interval="1h", limit=200)

df = pd.DataFrame(klines)
df.columns = ['timestamp', 'open', 'high', 'low', 'close', 'volume', 'close_time', 'quote_volume', 'trades', 'tb_base_volume', 'taker_buy_base', 'ignore']

df['close'] = df['close'].astype(float)

# 计算MA
df['MA20'] = df['close'].rolling(20).mean()
df['MA50'] = df['close'].rolling(50).mean()

print(df[['timestamp', 'close', 'MA20', 'MA50']].tail(10))
```

### 3. 订单簿分析

```python
from binance.client import Client

client = Client()

depth = client.get_order_book(symbol="BTCUSDT", limit=20)

bid_volume = sum([float(b[1]) for b in depth['bids']])
ask_volume = sum([float(a[1]) for a in depth['asks']])

print(f"买盘总量: {bid_volume} BTC")
print(f"卖盘总量: {ask_volume} BTC")
print(f"买卖比: {bid_volume/ask_volume:.2f}")
```

## 官方资源

- **Binance官网**: https://www.binance.com
- **API文档**: https://binance-docs.readthedocs.io
- **python-binance**: https://github.com/binance/binance-connector-python

## 免责声明

⚠️ **重要提示**：

- 加密货币交易有风险
- 请充分了解产品规则
- API Key请妥善保管
- 模拟盘建议先熟悉功能

## 更新日志

### v1.0.0 (2026-05-06)

- 初始版本
- 支持600+交易对
- REST API完整覆盖
- WebSocket实时数据
- 官方python-binance SDK
- 交易功能支持
