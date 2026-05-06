---
name: okxdata
description: OKX加密货币API | python-okx异步库 | 支持OKX交易所全部功能
version: 1.0.0
author: python-okx / OKX
tags:
  - cryptocurrency
  - okx
  - okex
  - exchange
  - crypto-api
supported_markets:
  - OKX交易所
  - 加密货币
---

# OKX Data - OKX交易所加密货币数据专家

python-okx库，异步架构，支持OKX交易所全部API功能。

## 核心定位

**OKX Data** 是一个专注于OKX交易所的Python库，提供：

1. **异步架构**：基于aiohttp，高性能异步请求
2. **全量API覆盖**：OKX V5 API全部接口
3. **18个业务模块**：Market、Account、Trade等
4. **自动重试**：三级错误处理机制
5. **Python原生**：异步/同步双模式支持

## 核心优势

| 特性 | 说明 |
|------|------|
| **异步架构** | 基于aiohttp，高吞吐量 |
| **全量覆盖** | OKX V5 API 100+接口 |
| **Python原生** | 纯Python实现 |
| **自动重试** | 三级错误处理 |
| **类型注解** | 完整类型提示 |
| **文档完善** | 18个业务模块详解 |

## python-okx安装

### 环境要求

```bash
pip install python-okx
```

或使用git安装：

```bash
pip install git+https://github.com/okx/python-okx.git
```

### 依赖

- Python 3.7+
- aiohttp
- asyncio
- requests

### 验证安装

```python
import okx
print(okx.__version__)
```

## 快速开始

### 基础使用流程

```python
from okx.MarketData import MarketData

# 创建市场数据客户端
client = MarketData(flag="0")  # 0=模拟盘，1=实盘

# 获取行情数据
btc_data = client.get_ticker(instId="BTC-USDT-SWAP")
print(btc_data)
```

### 异步使用

```python
import asyncio
from okx.MarketData import MarketData

async def get_price():
    client = MarketData(flag="0")
    btc_price = await client.get_ticker(instId="BTC-USDT-SWAP")
    return btc_price

result = asyncio.run(get_price())
print(result)
```

## 数据覆盖

### 1. 市场数据模块

| 数据类型 | 方法 | 说明 |
|---------|------|------|
| **实时行情** | get_ticker | 当前价格、24h涨跌 |
| **K线数据** | get_candles | 历史K线 |
| **深度数据** | get_bills | 买卖盘口 |
| **成交数据** | get_trades | 历史成交 |
| **最新标记价格** | get_mark_price | 标记价格 |
| **最新资金费率** | get_funding_rate | 资金费率 |

### 2. 账户模块

| 数据类型 | 方法 | 说明 |
|---------|------|------|
| **账户信息** | get_account_info | 账户余额 |
| **持仓信息** | get_positions | 当前持仓 |
| **账单明细** | get_bills | 账户流水 |

### 3. 交易模块

| 数据类型 | 方法 | 说明 |
|---------|------|------|
| **下单** | place_order | 市价/限价单 |
| **撤单** | cancel_algo_orders | 撤销订单 |
| **修改订单** | amend_order | 修改订单 |

## API参考

### 1. 市场数据 - 实时行情

```python
from okx.MarketData import MarketData

client = MarketData(flag="0")

# 获取BTC-USDT实时行情
result = client.get_ticker(instId="BTC-USDT-SWAP")
print(result)
```

返回数据：
```json
{
  "code": "0",
  "msg": "",
  "data": [
    {
      "instId": "BTC-USDT-SWAP",
      "last": "50000.00",
      "lastSz": "0.1",
      "askPx": "50000.00",
      "bidPx": "49999.00",
      "open24h": "49000.00",
      "high24h": "51000.00",
      "low24h": "48500.00",
      "vol24h": "10000.00",
      "volCcy24h": "500000000.00"
    }
  ]
}
```

### 2. 市场数据 - K线数据

```python
from okx.MarketData import MarketData

client = MarketData(flag="0")

# 获取BTC-USDT历史K线
result = client.get_candles(instId="BTC-USDT-SWAP", bar="1H", limit=100)
print(result)
```

参数说明：
- **instId**: 合约ID，如"BTC-USDT-SWAP"
- **bar**: K线周期，"1m", "5m", "1H", "4H", "1D"等
- **limit**: 条数，最大300

### 3. 市场数据 - 深度数据

```python
from okx.MarketData import MarketData

client = MarketData(flag="0")

# 获取深度数据
result = client.get_bills(instId="BTC-USDT-SWAP", sz=10)
print(result)
```

### 4. 市场数据 - 成交数据

```python
from okx.MarketData import MarketData

client = MarketData(flag="0")

# 获取最近成交
result = client.get_trades(instId="BTC-USDT-SWAP", limit=50)
print(result)
```

### 5. 账户 - 账户信息

```python
from okx.Account import Account
import okx.Account as Account

# 创建账户客户端
account = Account(api_key="your_key", api_secret="your_secret", passphrase="your_passphrase", flag="0")

# 获取账户信息
result = account.get_account_balance()
print(result)
```

### 6. 交易 - 下单

```python
from okx.Trade import Trade
import okx.Trade as Trade

trade = Trade(api_key="", api_secret="", passphrase="", flag="0")

# 市价开多
result = trade.place_order(
    instId="BTC-USDT-SWAP",
    tdMode="cross",
    side="buy",
    posSide="long",
    ordType="market",
    sz="0.01"
)
print(result)
```

## 交易参数

### 交易模式 (tdMode)

| 模式 | 说明 |
|------|------|
| **cross** | 全仓模式 |
| **isolated** | 逐仓模式 |
| **cash** | 现货模式 |

### 订单方向 (side)

| 方向 | 说明 |
|------|------|
| **buy** | 买入/做多 |
| **sell** | 卖出/做空 |

### 持仓方向 (posSide)

| 持仓 | 说明 |
|------|------|
| **long** | 多头持仓 |
| **short** | 空头持仓 |
| **net** | 净持仓 |

### 订单类型 (ordType)

| 类型 | 说明 |
|------|------|
| **market** | 市价单 |
| **limit** | 限价单 |
| **stop_loss** | 止损单 |
| **take_profit** | 止盈单 |

## 错误处理

### 错误代码

| 代码 | 说明 |
|------|------|
| 0 | 成功 |
| 10001 | 系统错误 |
| 10002 | 请求超时 |
| 10003 | 参数错误 |
| 10004 | 认证失败 |
| 10005 | 签名错误 |

### 自动重试机制

```python
from okx._utils import retry

@retry(max_attempts=3)
async def get_data_with_retry():
    client = MarketData(flag="0")
    return await client.get_ticker(instId="BTC-USDT-SWAP")
```

## 异步编程

### 批量获取多个币种数据

```python
import asyncio
from okx.MarketData import MarketData

async def get_multiple_tickers():
    client = MarketData(flag="0")
    
    tickers = ["BTC-USDT", "ETH-USDT", "SOL-USDT"]
    tasks = [
        client.get_ticker(instId=f"{ticker}-SWAP")
        for ticker in tickers
    ]
    
    results = await asyncio.gather(*tasks)
    return results

# 运行
tickers_data = asyncio.run(get_multiple_tickers())
print(tickers_data)
```

### 实时K线订阅

```python
import asyncio
from okx.Ws import Ws

async def on_message(message):
    print(message)

ws = Ws()
ws.subscribe(
    channel=["BTC-USDT-SWAP"],
    inst_type="SWAP",
    callback=on_message
)

# 启动WebSocket连接
asyncio.run(ws.start())
```

## 与其他数据源对比

| 特性 | OKX | CoinGecko | yfinance |
|------|------|-----------|----------|
| **交易所** | OKX | 全球 | 全球 |
| **数据类型** | 实时+历史 | 实时+历史 | 实时+历史 |
| **免费程度** | 合理限额 | 免费 | 免费 |
| **API接口** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐ |
| **实时性** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐ |
| **交易功能** | ⭐⭐⭐⭐⭐ | ❌ | ❌ |

## 使用场景

### 1. 实时行情监控

```python
import asyncio
from okx.MarketData import MarketData

async def monitor_prices():
    client = MarketData(flag="0")
    
    symbols = ["BTC-USDT", "ETH-USDT", "SOL-USDT"]
    
    while True:
        for symbol in symbols:
            data = await client.get_ticker(instId=f"{symbol}-SWAP")
            price = data['data'][0]['last']
            print(f"{symbol}: ${price}")
        
        await asyncio.sleep(10)  # 10秒刷新一次

# 运行
asyncio.run(monitor_prices())
```

### 2. 技术分析指标计算

```python
import pandas as pd
from okx.MarketData import MarketData

def calculate_ma(data, window=20):
    """计算移动平均线"""
    df = pd.DataFrame(data)
    df['MA'] = df['close'].rolling(window=window).mean()
    return df

async def main():
    client = MarketData(flag="0")
    candles = await client.get_candles(instId="BTC-USDT-SWAP", bar="1H", limit=100)
    df = calculate_ma(candles, window=20)
    print(df.tail())

asyncio.run(main())
```

## 官方资源

- **python-okx GitHub**: https://github.com/okx/python-okx
- **OKX API文档**: https://www.okx.com/docs-v5/zh/
- **OKX官网**: https://www.okx.com

## 免责声明

⚠️ **重要提示**：

- 加密货币交易有风险
- 请充分了解产品规则
- 模拟盘交易建议先熟悉功能
- 实盘交易需谨慎

## 更新日志

### v1.0.0 (2026-05-06)

- 初始版本
- 支持OKX交易所全部API
- 异步架构设计
- 18个业务模块
- 自动重试机制
