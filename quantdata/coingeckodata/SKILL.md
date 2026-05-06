---
name: coingeckodata
description: CoinGecko加密货币API | 免费开源的加密货币行情接口 | 支持10,000+加密货币
version: 1.0.0
author: CoinGecko
tags:
  - cryptocurrency
  - crypto
  - crypto-api
  - bitcoin
  - ethereum
supported_markets:
  - 全球加密货币市场
---

# CoinGecko Data - 全球加密货币市场数据专家

免费、开源的加密货币市场数据接口，支持10,000+加密货币。

## 核心定位

**CoinGecko Data** 是一个专注于加密货币市场的免费数据源，提供：

1. **海量加密货币**：支持10,000+加密货币数据
2. **完全免费**：无需API Key，免费使用
3. **REST API**：简单易用的HTTP接口
4. **实时行情**：实时价格、市值、交易量等
5. **历史数据**：K线、历史价格走势

## 核心优势

| 特性 | 说明 |
|------|------|
| **免费使用** | 无需API Key |
| **海量数据** | 10,000+加密货币 |
| **简单易用** | REST API，Python requests即可 |
| **全球市场** | 全球加密货币覆盖 |
| **实时数据** | 实时价格更新 |
| **社区活跃** | 持续更新，积极维护 |

## 数据覆盖

### 1. 主流加密货币

| 加密货币 | 代码 | 说明 |
|---------|------|------|
| **Bitcoin** | bitcoin | BTC |
| **Ethereum** | ethereum | ETH |
| **Binance Coin** | binancecoin | BNB |
| **Solana** | solana | SOL |
| **Cardano** | cardano | ADA |
| **Ripple** | ripple | XRP |
| **Dogecoin** | dogecoin | DOGE |
| **Polkadot** | polkadot | DOT |
| **Litecoin** | litecoin | LTC |
| **Chainlink** | chainlink | LINK |

### 2. DeFi代币

| 类别 | 示例 |
|------|------|
| **DEX** | Uniswap (uni), PancakeSwap (cake) |
| **借贷** | Aave (aave), Compound (comp) |
| **Layer2** | Polygon (matic), Arbitrum (arb) |
| **稳定币** | Tether (usdt), USD Coin (usdc), Dai (dai) |

## 环境要求

### 安装

```bash
pip install requests
```

### 依赖

- Python 3.6+
- requests
- pandas（可选，用于数据处理）

### 验证安装

```python
import requests
response = requests.get("https://api.coingecko.com/api/v3/ping")
print(response.json())
```

## 快速开始

### 基础使用流程

```python
import requests
import pandas as pd

# Step 1: 获取实时价格
url = "https://api.coingecko.com/api/v3/simple/price"
params = {
    'ids': 'bitcoin',
    'vs_currencies': 'usd',
    'include_24hr_change': 'true'
}

response = requests.get(url, params=params)
data = response.json()
print(data)
```

### 基本查询示例

#### 1. 获取单个加密货币价格

```python
import requests

# 获取BTC实时价格
url = "https://api.coingecko.com/api/v3/simple/price"
params = {
    'ids': 'bitcoin',
    'vs_currencies': 'usd,usdt,eur,jpy',
    'include_24hr_change': 'true',
    'include_market_cap': 'true'
}

response = requests.get(url, params=params)
btc_data = response.json()

print(f"BTC价格: ${btc_data['bitcoin']['usd']}")
print(f"24h涨跌: {btc_data['bitcoin']['usd_24h_change']}%")
```

#### 2. 获取多个加密货币价格

```python
import requests

url = "https://api.coingecko.com/api/v3/simple/price"
params = {
    'ids': 'bitcoin,ethereum,solana',
    'vs_currencies': 'usd',
    'include_24hr_change': 'true',
    'include_market_cap': 'true'
}

response = requests.get(url, params=params)
crypto_data = response.json()

for crypto, prices in crypto_data.items():
    print(f"{crypto}: ${prices['usd']} ({prices['usd_24h_change']}%)")
```

#### 3. 获取市值排行榜

```python
import requests

url = "https://api.coingecko.com/api/v3/coins/markets"
params = {
    'vs_currency': 'usd',
    'order': 'market_cap_desc',
    'per_page': 10,
    'page': 1,
    'sparkline': 'false'
}

response = requests.get(url, params=params)
top_coins = response.json()

for coin in top_coins:
    print(f"{coin['name']}: ${coin['current_price']} (市值: ${coin['market_cap']})")
```

#### 4. 获取历史K线数据

```python
import requests

# 获取BTC历史价格
coin_id = "bitcoin"
url = f"https://api.coingecko.com/api/v3/coins/{coin_id}/market_chart"
params = {
    'vs_currency': 'usd',
    'days': '30'
}

response = requests.get(url, params=params)
historical_data = response.json()

prices = historical_data['prices']
for price in prices[-5:]:  # 最近5个数据点
    print(f"时间戳: {price[0]}, 价格: ${price[1]}")
```

## 加密货币代码

### 常用加密货币代码

| 加密货币 | CoinGecko ID | 交易所代码 |
|---------|-------------|------------|
| Bitcoin | bitcoin | BTC, BTC-USDT |
| Ethereum | ethereum | ETH, ETH-USDT |
| Binance Coin | binancecoin | BNB, BNB-USDT |
| Solana | solana | SOL, SOL-USDT |
| Cardano | cardano | ADA, ADA-USDT |
| XRP | ripple | XRP, XRP-USDT |
| Dogecoin | dogecoin | DOGE, DOGE-USDT |
| Polkadot | polkadot | DOT, DOT-USDT |
| Chainlink | chainlink | LINK, LINK-USDT |
| Litecoin | litecoin | LTC, LTC-USDT |
| Polygon | matic-network | MATIC, MATIC-USDT |
| Avalanche | avalanche-2 | AVAX, AVAX-USDT |
| Shiba Inu | shiba-inu | SHIB, SHIB-USDT |
| Uniswap | uniswap | UNI, UNI-USDT |
| Aave | aave | AAVE, AAVE-USDT |

### 交易对格式

| 交易所 | 格式 | 示例 |
|--------|------|------|
| USDT交易对 | crypto-usdt | bitcoin, ethereum |
| BTC交易对 | crypto-btc | bitcoin-btc, ethereum-btc |
| ETH交易对 | crypto-eth | bitcoin-eth |

## API参考

### 1. 简单价格接口

#### /simple/price

获取加密货币当前价格。

```python
url = "https://api.coingecko.com/api/v3/simple/price"
params = {
    'ids': 'bitcoin,ethereum',
    'vs_currencies': 'usd,eur,jpy',
    'include_24hr_change': 'true',
    'include_market_cap': 'true',
    'include_24hr_vol': 'true'
}
```

### 2. 市场数据接口

#### /coins/markets

获取加密货币市场数据。

```python
url = "https://api.coingecko.com/api/v3/coins/markets"
params = {
    'vs_currency': 'usd',
    'order': 'market_cap_desc',
    'per_page': 20,
    'page': 1,
    'sparkline': 'false',
    'price_change_percentage': '24h,7d,30d'
}
```

### 3. 历史数据接口

#### /coins/{id}/market_chart

获取历史价格数据。

```python
coin_id = "bitcoin"
url = f"https://api.coingecko.com/api/v3/coins/{coin_id}/market_chart"
params = {
    'vs_currency': 'usd',
    'days': 30,
    'interval': 'daily'
}
```

### 4. 搜索接口

#### /search

搜索加密货币。

```python
url = "https://api.coingecko.com/api/v3/search"
params = {'query': 'bitcoin'}
response = requests.get(url, params=params)
results = response.json()
```

### 5. 全球数据接口

#### /global

获取加密货币市场全球数据。

```python
url = "https://api.coingecko.com/api/v3/global"
response = requests.get(url)
global_data = response.json()

market_data = global_data['data']
print(f"总市值: ${market_data['total_market_cap']['usd']}")
print(f"24h交易量: ${market_data['total_volume']['usd']}")
print(f"BTC市值占比: {market_data['market_cap_percentage']['btc']}%")
```

## 限流说明

### API限流

| 接口 | 限流 | 说明 |
|------|------|------|
| 公开接口 | 10-50次/分钟 | 无需API Key |
| 需要API Key接口 | 更高限额 | 注册后获得 |

### 最佳实践

```python
import time
import requests

def rate_limited_request(url, params, max_retries=3):
    """带限流处理的请求函数"""
    for attempt in range(max_retries):
        try:
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            if attempt < max_retries - 1:
                wait_time = 2 ** attempt
                time.sleep(wait_time)
            else:
                raise
    return None
```

## 与其他数据源对比

| 特性 | CoinGecko | yfinance | futuopendata |
|------|-----------|-----------|--------------|
| **加密货币** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | ❌ |
| **免费程度** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ |
| **数据量** | 10,000+ | 主流加密货币 | N/A |
| **实时性** | ⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| **历史数据** | ⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |

## 使用场景推荐

### 1. 加密货币市场概览

```python
import requests

# 获取全球市场数据
url = "https://api.coingecko.com/api/v3/global"
response = requests.get(url)
global_data = response.json()['data']

print("=== 全球加密货币市场概览 ===")
print(f"总市值: ${global_data['total_market_cap']['usd']:,.0f}")
print(f"24h交易量: ${global_data['total_volume']['usd']:,.0f}")
print(f"BTC占比: {global_data['market_cap_percentage']['btc']}%")
print(f"交易所数量: {global_data['active_cryptocurrencies']}")
```

### 2. 加密货币投资组合跟踪

```python
import requests

portfolio = ['bitcoin', 'ethereum', 'solana', 'cardano']
url = "https://api.coingecko.com/api/v3/simple/price"

params = {
    'ids': ','.join(portfolio),
    'vs_currencies': 'usd',
    'include_24hr_change': 'true',
    'include_market_cap': 'true'
}

response = requests.get(url, params=params)
portfolio_data = response.json()

total_value = 0
print("=== 投资组合概览 ===")
for coin in portfolio:
    price = portfolio_data[coin]['usd']
    change = portfolio_data[coin]['usd_24h_change']
    total_value += price
    print(f"{coin:15} ${price:>10.2f} ({change:+.2f}%)")
```

## 版本信息

- **当前版本**: 1.0.0
- **官方网站**: https://www.coingecko.com
- **API文档**: https://www.coingecko.com/en/api
- **GitHub**: https://github.com/coingecko

## 免责声明

⚠️ **重要提示**：

- 数据仅供参考，不构成投资建议
- 加密货币市场波动大，投资需谨慎
- 请遵守相关法律法规
- 尊重数据版权

## 更新日志

### v1.0.0 (2026-05-06)

- 初始版本
- 支持10,000+加密货币
- 免费使用，无需API Key
- REST API接口
- 实时价格、市值、历史K线
