---
name: yfinancedata
description: Yahoo Finance数据接口 | 全球市场数据 | 支持美股、港股、指数、ETF、期货、外汇、加密货币
version: 1.0.0
author: Yahoo Finance / Ran Aroussi
tags:
  - quantitative
  - finance
  - us-stock
  - global-market
  - yahoo-finance
  - historical-data
supported_markets:
  - 美股（NYSE、NASDAQ、AMEX）
  - 港股
  - A股（沪、深）
  - 全球指数
  - ETF
  - 期货
  - 外汇
  - 加密货币
---

# yFinance Data - 全球金融市场数据专家

Yahoo Finance 官方API接口，提供全球金融市场数据访问。

## 核心定位

**yFinance** 是一个专注于全球金融市场数据的免费数据源，提供：

1. **全球市场覆盖**：美股、港股、A股、全球指数、ETF等
2. **多资产类别**：股票、指数、ETF、期货、外汇、加密货币
3. **丰富的财务数据**：财务报表、估值指标、收益数据
4. **实时/历史数据**：支持日内、历史、盘后数据
5. **Python原生**：直接返回Pandas DataFrame格式

## 核心优势

| 特性 | 说明 |
|------|------|
| **全球市场** | 美股为主，覆盖港股、A股、全球市场 |
| **多资产类别** | 股票、ETF、指数、期货、外汇、加密货币 |
| **数据丰富** | 历史行情、财务报表、机构持仓、分析师预期 |
| **免费使用** | 无需注册，完全免费 |
| **Python原生** | 直接返回Pandas DataFrame |
| **社区活跃** | 持续更新，积极维护 |

## 数据覆盖

### 1. 美股数据（核心优势）

| 数据类型 | 时间范围 | 说明 |
|---------|---------|------|
| **历史行情** | 最多20年+ | 日、周、月K线，支持前复权 |
| **分钟数据** | 最近30天 | 1/5/15/30/60分钟 |
| **实时行情** | 实时 | 当日价格、成交量等 |
| **财务报表** | 10年+ | 资产负债表、利润表、现金流量表 |
| **财务比率** | 10年+ | PE、PB、PS等估值指标 |
| **股息数据** | 历史全量 | 分红历史、分红收益率 |
| **股票拆分** | 历史全量 | 拆股、合股记录 |
| **期权数据** | 当前 | 期权链、到期日等 |
| **分析师预期** | 当前 | 评级、目标价、盈利预期 |
| **机构持仓** | 季度 | 13F机构持仓变化 |
| **基本面数据** | 当前 | 公司信息、行业分类 |

### 2. 港股数据

| 数据类型 | 时间范围 | 说明 |
|---------|---------|------|
| **历史行情** | 20年+ | 日、周、月K线 |
| **实时行情** | 实时 | 当日价格、成交量 |
| **财务报表** | 10年+ | 港股财报 |
| **分红数据** | 历史全量 | 分红历史 |

### 3. A股数据（沪、深）

| 数据类型 | 时间范围 | 说明 |
|---------|---------|------|
| **历史行情** | 有限 | 部分股票数据完整 |
| **实时行情** | 实时 | 当日价格 |
| **财务报表** | 部分 | 数据可能不完整 |

### 4. 其他市场

| 资产类别 | 示例 | 说明 |
|---------|------|------|
| **指数** | ^GSPC (S&P 500) | 全球主要指数 |
| **ETF** | SPY, QQQ | 美国ETF |
| **期货** | CL=F (原油) | 商品期货 |
| **外汇** | EURUSD=X | 货币对 |
| **加密货币** | BTC-USD | 主流加密货币 |

## 环境要求

### 安装

```bash
pip install yfinance
```

或使用国内镜像：

```bash
pip install yfinance -i https://pypi.tuna.tsinghua.edu.cn/simple --trusted-host pypi.tuna.tsinghua.edu.cn
```

### 依赖

- Python 3.6+
- pandas
- numpy
- requests（自动安装）
- multitasking（自动安装）

### 验证安装

```python
python -c "import yfinance as yf; print(yf.__version__)"
```

输出版本号表示安装成功。

## 快速开始

### 基础使用流程

```python
import yfinance as yf

# 获取苹果公司数据
ticker = yf.Ticker("AAPL")

# 获取历史行情
hist = ticker.history(period="1mo")

# 获取财务报表
financials = ticker.financials
balance_sheet = ticker.balance_sheet
cashflow = ticker.cashflow

# 获取基本信息
info = ticker.info

print(hist.head())
print(financials)
```

### 基本查询示例

#### 1. 获取股票历史数据

```python
import yfinance as yf

# 单只股票
apple = yf.Ticker("AAPL")
hist = apple.history(period="1y")  # 最近1年
print(hist.head())

# 多只股票
data = yf.download("AAPL TSLA GOOGL", start="2023-01-01", end="2024-12-31")
print(data.head())
```

#### 2. 获取实时数据

```python
import yfinance as yf

# 当日数据（盘中）
aapl = yf.Ticker("AAPL")
todays_data = aapl.history(period="1d")
print(todays_data.tail())

# 实时信息
info = aapl.info
print(f"当前价格: ${info['currentPrice']}")
print(f"今日涨跌: {info['regularMarketChangePercent']:.2f}%")
```

#### 3. 获取财务报表

```python
import yfinance as yf

ticker = yf.Ticker("AAPL")

# 利润表
income_stmt = ticker.income_stmt
print(income_stmt)

# 资产负债表
balance = ticker.balance_sheet
print(balance)

# 现金流量表
cashflow = ticker.cashflow
print(cashflow)

# 获取多年数据
income_history = ticker.financials
print(income_history)
```

#### 4. 获取分钟数据

```python
import yfinance as yf

ticker = yf.Ticker("AAPL")

# 盘中分钟数据（最近7天）
minutes = ticker.history(period="7d", interval="5m")
print(minutes.tail(20))

# 盘中分钟数据（指定日期）
data = yf.download("AAPL", start="2024-01-15", end="2024-01-16", interval="5m")
print(data.head())
```

#### 5. 获取ETF和指数数据

```python
import yfinance as yf

# S&P 500指数
spy = yf.Ticker("SPY")
spy_hist = spy.history(period="1mo")
print(spy_hist.head())

# 纳斯达克100
qqq = yf.Ticker("QQQ")
qqq_hist = qqq.history(period="1mo")
print(qqq_hist.head())

# 黄金ETF
gld = yf.Ticker("GLD")
gld_hist = gld.history(period="1mo")
print(gld_hist.head())
```

#### 6. 批量获取多只股票

```python
import yfinance as yf

# 方法1：使用 Tickers
tickers = yf.Tickers("AAPL MSFT GOOGL AMZN META")
for ticker in tickers.tickers:
    print(f"{ticker.info['shortName']}: ${ticker.info['currentPrice']}")

# 方法2：使用 download
data = yf.download(["AAPL", "MSFT", "GOOGL"], period="1mo")
print(data['Close'].head())

# 方法3：获取同行业多只股票
tech_stocks = ["AAPL", "MSFT", "GOOGL", "META", "NVDA"]
data = yf.download(tech_stocks, period="3mo")
print(data['Adj Close'].describe())
```

## 股票代码格式

### 美股代码

| 类型 | 格式 | 示例 |
|------|------|------|
| **普通股票** | 股票代码 | `AAPL`, `TSLA`, `GOOGL` |
| **带交易所后缀** | 代码.交易所 | `BRK.B`（波克夏B股） |
| **优先股** | 代码-P | `AAPL-P`（苹果优先股） |

### 特殊代码

| 类型 | 代码 | 说明 |
|------|------|------|
| **S&P 500** | `^GSPC` | 标普500指数 |
| **纳斯达克综合** | `^IXIC` | 纳斯达克综合指数 |
| **道琼斯工业** | `^DJI` | 道琼斯工业平均指数 |
| **VIX恐慌指数** | `^VIX` | VIX波动率指数 |

### 港股代码

| 格式 | 示例 | 说明 |
|------|------|------|
| 代码.HK | `0700.HK` | 腾讯控股 |
| | `9988.HK` | 阿里巴巴 |
| | `3690.HK` | 美团 |

### A股代码

| 格式 | 示例 | 说明 |
|------|------|------|
| 代码.SS | `600000.SS` | 上证指数 |
| 代码.SZ | `000001.SZ` | 深证成指 |

### 其他资产

| 类型 | 格式 | 示例 |
|------|------|------|
| **ETF** | 代码 | `SPY`, `QQQ`, `GLD`, `TLT` |
| **期货** | 代码=F | `CL=F`（WTI原油） |
| **外汇** | 代码=X | `EURUSD=X` |
| **加密货币** | 代码-USD | `BTC-USD`, `ETH-USD` |

## API 参考

### 1. Ticker 类

单只股票的数据访问。

```python
ticker = yf.Ticker("AAPL")
```

#### 主要属性/方法

| 方法 | 说明 | 返回类型 |
|------|------|---------|
| `history()` | 历史价格数据 | DataFrame |
| `info` | 公司基本信息 | dict |
| `income_stmt` | 利润表 | DataFrame |
| `balance_sheet` | 资产负债表 | DataFrame |
| `cashflow` | 现金流量表 | DataFrame |
| `dividends` | 分红历史 | Series |
| `splits` | 拆股历史 | Series |
| `options` | 期权到期日 | tuple |
| `option_chain()` | 期权链 | OptionChain |
| `recommendations` | 分析师推荐 | DataFrame |
| `analyst_price_targets` | 分析师目标价 | DataFrame |
| `earnings_dates` | 财报发布日 | DataFrame |
| `institutional_holders` | 机构持仓 | DataFrame |
| `mutualfund_holders` | 基金持仓 | DataFrame |
| `major_holders` | 主要股东 | DataFrame |

### 2. history() 方法详解

获取历史价格数据。

**参数**：

| 参数 | 类型 | 说明 | 示例 |
|------|------|------|------|
| `period` | str | 时间周期 | "1d", "5d", "1mo", "3mo", "1y", "5y", "max" |
| `interval` | str | 数据频率 | "1m", "2m", "5m", "15m", "30m", "60m", "1h", "1d", "1wk", "1mo" |
| `start` | str | 开始日期 | "2023-01-01" |
| `end` | str | 结束日期 | "2024-01-01" |
| `auto_adjust` | bool | 自动复权 | True/False |
| `back_adjust` | bool | 后复权 | True/False |
| `actions` | bool | 包含分红和拆股 | True/False |
| `group_by` | str | 分组方式 | "ticker" / "column" |
| `adjust_kwargs` | dict | 复权参数 | `{"method": "split"}` |

**period 可选值**：

| 值 | 说明 |
|------|------|
| `1d` | 最近1天 |
| `5d` | 最近5天 |
| `1mo` | 最近1个月 |
| `3mo` | 最近3个月 |
| `6mo` | 最近6个月 |
| `1y` | 最近1年 |
| `2y` | 最近2年 |
| `5y` | 最近5年 |
| `10y` | 最近10年 |
| `ytd` | 今年至今 |
| `max` | 全部历史 |

**interval 可选值**：

| 值 | 说明 | 限制 |
|------|------|------|
| `1m` | 1分钟 | 最近7天 |
| `2m` | 2分钟 | 最近60天 |
| `5m` | 5分钟 | 最近60天 |
| `15m` | 15分钟 | 最近60天 |
| `30m` | 30分钟 | 最近60天 |
| `60m` | 60分钟 | 最近730天 |
| `1h` | 1小时 | 最近730天 |
| `1d` | 日线 | 无限制 |
| `1wk` | 周线 | 无限制 |
| `1mo` | 月线 | 无限制 |

**示例**：

```python
# 最近1年的日线数据
data = ticker.history(period="1y")
print(data.head())

# 指定日期范围的日线
data = ticker.history(start="2023-01-01", end="2024-01-01")
print(data.head())

# 最近5天的分钟数据
data = ticker.history(period="5d", interval="5m")
print(data.head())

# 不复权的原始数据
data = ticker.history(period="1mo", auto_adjust=False)
print(data.head())

# 包含分红和拆股数据
data = ticker.history(period="1y", actions=True)
print(data.head())
```

### 3. info 属性

获取公司基本信息。

```python
info = ticker.info
print(info.keys())
```

**常用字段**：

| 字段 | 说明 | 示例 |
|------|------|------|
| `shortName` | 简称 | Apple Inc. |
| `longName` | 全称 | Apple Inc. |
| `sector` | 行业 | Technology |
| `industry` | 细分行业 | Consumer Electronics |
| `currentPrice` | 当前价格 | 185.92 |
| `marketCap` | 市值 | 2890000000000 |
| `peRatio` | 市盈率 | 30.12 |
| `dividendYield` | 股息率 | 0.0048 |
| `beta` | Beta系数 | 1.29 |
| `52WeekHigh` | 52周最高 | 199.62 |
| `52WeekLow` | 52周最低 | 124.17 |
| `averageVolume` | 平均成交量 | 54330000 |
| `earningsGrowth` | 盈利增长 | 0.08 |
| `revenueGrowth` | 营收增长 | 0.02 |
| `totalRevenue` | 总营收 | 385600000000 |
| `grossMargins` | 毛利率 | 0.45 |
| `profitMargins` | 净利率 | 0.25 |

### 4. download() 函数

批量下载多只股票数据。

```python
data = yf.download("AAPL MSFT GOOGL", start="2023-01-01", end="2024-01-01")
```

**参数**：

| 参数 | 类型 | 说明 |
|------|------|------|
| `tickers` | str/list | 股票代码，多个用空格分隔 |
| `start` | str | 开始日期 |
| `end` | str | 结束日期 |
| `period` | str | 时间周期 |
| `interval` | str | 数据频率 |
| `group_by` | str | 分组方式 |
| `auto_adjust` | bool | 自动复权 |
| `actions` | bool | 包含分红和拆股 |
| `threads` | bool | 多线程下载 |
| `progress` | bool | 显示进度条 |

**返回数据结构**：

```
                    AAPL        MSFT       GOOGL
Date                                            
2023-01-03  Open    125.98     226.75     86.75
            High    127.13     229.35     88.19
            Low     125.12     226.05     86.15
            Close   126.74     228.95     88.00
            Volume  49843400   18956800   21000000
```

### 5. 财务数据

#### 利润表 (income_stmt)

```python
income = ticker.income_stmt
print(income)
```

返回字段：
- Total Revenue（总营收）
- Cost of Revenue（营业成本）
- Gross Profit（毛利润）
- Operating Expense（运营费用）
- Operating Income（运营利润）
- Net Income（净利润）
- Earnings Per Share（每股收益）

#### 资产负债表 (balance_sheet)

```python
balance = ticker.balance_sheet
print(balance)
```

返回字段：
- Total Assets（总资产）
- Total Liabilities（总负债）
- Total Equity（总权益）
- Cash And Cash Equivalents（现金）
- Long Term Debt（长期负债）

#### 现金流量表 (cashflow)

```python
cashflow = ticker.cashflow
print(cashflow)
```

返回字段：
- Operating Cash Flow（经营现金流）
- Investing Cash Flow（投资现金流）
- Financing Cash Flow（融资现金流）
- Capital Expenditures（资本支出）
- Free Cash Flow（自由现金流）

### 6. 分红和拆股数据

```python
# 分红历史
dividends = ticker.dividends
print(dividends)
# 2023-01-01    0.23
# 2023-04-01    0.24
# 2023-07-01    0.24
# 2023-10-01    0.24

# 拆股历史
splits = ticker.splits
print(splits)
# 2020-08-31    4.0  # 4股合1股

# 完整的分红再投资历史
actions = ticker.history(period="5y", actions=True)
print(actions[['Dividends', 'Stock Splits']].head())
```

## 数据质量保证

### 数据更新时效

| 数据类型 | 更新时间 | 说明 |
|---------|---------|------|
| **实时行情** | 实时 | 可能有15分钟延迟 |
| **分钟数据** | 实时 | 最近7天 |
| **日线数据** | 盘后 | 美股收盘后1-2小时 |
| **财务报表** | 季报后 | 财报发布后1-2天 |
| **分析师数据** | 实时 | 分析师更新时 |

### 数据完整性

- ✅ 美股数据：非常完整，历史悠久
- ✅ 港股数据：较完整
- ⚠️ A股数据：部分股票数据可能不完整
- ⚠️ 分钟数据：仅保留最近7-60天

### 限制和注意事项

⚠️ **重要限制**：

1. **分钟数据限制**：
   - 1分钟数据：仅最近7天
   - 2-60分钟数据：最近60天
   - 1小时及以上：无限制

2. **请求限制**：
   - 无明确限制，但建议合理使用
   - 批量请求时使用多线程

3. **数据延迟**：
   - 实时数据可能有15分钟延迟
   - 历史数据准确可靠

4. **A股数据**：
   - 数据覆盖不如美股完整
   - 建议优先使用 baostockdata

## 最佳实践

### 1. 数据获取优化

✅ **推荐做法**：

```python
import yfinance as yf

# 批量下载使用多线程
data = yf.download(
    ["AAPL", "MSFT", "GOOGL"],
    start="2023-01-01",
    end="2024-01-01",
    threads=True  # 启用多线程
)

# 缓存频繁访问的数据
ticker = yf.Ticker("AAPL")
info = ticker.info  # 一次性获取
```

❌ **不推荐**：

```python
# 大量请求时逐个获取
for code in stock_list:
    ticker = yf.Ticker(code)
    data = ticker.history()  # 逐个请求，效率低
```

### 2. 错误处理

```python
import yfinance as yf

def get_stock_data(ticker_symbol, period="1y"):
    """获取股票数据，带错误处理"""
    
    try:
        ticker = yf.Ticker(ticker_symbol)
        
        # 获取历史数据
        hist = ticker.history(period=period)
        
        if hist.empty:
            print(f"警告: {ticker_symbol} 无历史数据")
            return None
        
        # 获取基本信息
        info = ticker.info
        
        return {
            'symbol': ticker_symbol,
            'history': hist,
            'info': info,
            'success': True
        }
        
    except Exception as e:
        print(f"错误: {ticker_symbol} - {str(e)}")
        return None

# 使用
result = get_stock_data("AAPL")
if result:
    print(f"成功获取 {result['symbol']} 的数据")
```

### 3. 性能优化

```python
import yfinance as yf

# ✅ 高效：使用多线程批量下载
data = yf.download(
    ["AAPL", "MSFT", "GOOGL", "AMZN", "META"],
    period="1y",
    threads=True,
    progress=False
)

# ✅ 高效：使用 Tickers 批量获取多只股票信息
tickers = yf.Tickers("AAPL MSFT GOOGL AMZN META")
for ticker in tickers.tickers:
    info = ticker.info
    print(f"{info['symbol']}: ${info['currentPrice']}")

# ✅ 高效：缓存 info 数据
ticker = yf.Ticker("AAPL")
info = ticker.info  # 获取一次
print(info['currentPrice'])  # 多次使用
print(info['marketCap'])  # 多次使用
```

### 4. 数据处理

```python
import yfinance as yf
import pandas as pd

# 获取数据
ticker = yf.Ticker("AAPL")
hist = ticker.history(period="1y")

# 数据类型转换
hist['Close'] = pd.to_numeric(hist['Close'], errors='coerce')
hist['Volume'] = pd.to_numeric(hist['Volume'], errors='coerce')

# 计算收益率
hist['Returns'] = hist['Close'].pct_change()
hist['Cumulative_Returns'] = (1 + hist['Returns']).cumprod()

# 计算移动平均
hist['MA20'] = hist['Close'].rolling(window=20).mean()
hist['MA50'] = hist['Close'].rolling(window=50).mean()

print(hist.tail())
```

## 与其他数据源对比

| 特性 | yFinance | westockdata | baostockdata |
|------|---------|-------------|--------------|
| **美股数据** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ❌ |
| **港股数据** | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ❌ |
| **A股数据** | ⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| **历史深度** | 20年+ | 较短 | 1990年至今 |
| **实时性** | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ❌ |
| **分钟数据** | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ |
| **财务报表** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐ |
| **期权数据** | ⭐⭐⭐⭐⭐ | ❌ | ❌ |
| **分析师数据** | ⭐⭐⭐⭐⭐ | ❌ | ❌ |
| **请求限制** | 无 | 无 | 无 |
| **注册要求** | 无 | 无 | 无 |
| **成本** | 免费 | 免费 | 免费 |

## 使用场景推荐

### 1. 量化回测（美股）

```python
import yfinance as yf

# 获取多只股票5年日线数据
stocks = ["AAPL", "MSFT", "GOOGL", "AMZN", "META", "NVDA", "TSLA"]
data = yf.download(stocks, period="5y", threads=True)

# 提取收盘价
close_prices = data['Close']
returns = close_prices.pct_change()

# 计算相关系数矩阵
corr_matrix = returns.corr()
print(corr_matrix)
```

### 2. 技术分析（全球市场）

```python
import yfinance as yf

# 获取任意市场的数据
markets = {
    'AAPL': 'AAPL',        # 苹果
    'SP500': '^GSPC',      # 标普500
    'BTC': 'BTC-USD',      # 比特币
    'Gold': 'GC=F',        # 黄金期货
    'Oil': 'CL=F'          # 原油期货
}

for name, symbol in markets.items():
    ticker = yf.Ticker(symbol)
    hist = ticker.history(period="1mo")
    print(f"{name}: 最新价 ${hist['Close'].iloc[-1]:.2f}")
```

### 3. 基本面分析

```python
import yfinance as yf

ticker = yf.Ticker("AAPL")

# 获取财务数据
income = ticker.income_stmt
balance = ticker.balance_sheet
cashflow = ticker.cashflow

# 计算关键指标
print("=== 基本面分析 ===")
print(f"市盈率(PE): {ticker.info['trailingPE']:.2f}")
print(f"市净率(PB): {ticker.info['priceToBook']:.2f}")
print(f"股息率: {ticker.info['dividendYield']*100:.2f}%")
print(f"市值: ${ticker.info['marketCap']/1e12:.2f}万亿")
print(f"年营收: ${ticker.info['totalRevenue']/1e9:.2f}十亿")
print(f"净利润率: {ticker.info['profitMargins']*100:.2f}%")
```

### 4. 机构持仓分析

```python
import yfinance as yf

ticker = yf.Ticker("AAPL")

# 获取机构持仓
institutional = ticker.institutional_holders
print("=== 机构持仓 Top 10 ===")
print(institutional[['Holder', 'Shares', 'Date Reported']].head(10))

# 获取主要股东
major = ticker.major_holders
print("\n=== 主要股东 ===")
print(major)
```

## 局限性

⚠️ **已知限制**：

1. **A股数据**：不如美股完整，建议使用 baostockdata
2. **实时数据**：可能有15分钟延迟
3. **分钟数据**：有保存期限限制（7-60天）
4. **请求频率**：虽无明确限制，但应合理使用
5. **数据准确性**：依赖 Yahoo Finance，可能有调整

## 扩展使用

### 与 Pandas 分析

```python
import yfinance as yf
import pandas as pd

# 获取数据
data = yf.download("AAPL", period="2y")

# 转换为月度数据
monthly = data['Close'].resample('M').last()

# 计算月度收益率
monthly_returns = monthly.pct_change().dropna()

# 统计分析
print(f"平均月收益: {monthly_returns.mean()*100:.2f}%")
print(f"月收益标准差: {monthly_returns.std()*100:.2f}%")
print(f"夏普比率: {(monthly_returns.mean()/monthly_returns.std())*12**0.5:.2f}")
```

### 与 Matplotlib 可视化

```python
import yfinance as yf
import matplotlib.pyplot as plt

# 获取数据
data = yf.download("AAPL", period="1y")

# 绘图
plt.figure(figsize=(12, 6))
plt.plot(data['Close'], label='AAPL')
plt.title('Apple Stock Price - 1 Year')
plt.xlabel('Date')
plt.ylabel('Price ($)')
plt.legend()
plt.grid(True)
plt.show()
```

## 版本信息

- **当前版本**: 1.3.0
- **官方网站**: https://github.com/ranaroussi/yfinance
- **PyPI页面**: https://pypi.org/project/yfinance/
- **文档网站**: https://ranaroussi.github.io/yfinance

## 免责声明

⚠️ **重要提示**：

- yfinance 不是 Yahoo, Inc. 的关联公司、认可或认证的产品
- 数据仅供参考，不构成投资建议
- Yahoo Finance API 仅供个人使用
- 投资有风险，决策需谨慎
- 请遵守 Yahoo 的服务条款

## 更新日志

### v1.0.0 (2026-05-06)

- 初始版本
- 支持美股、港股、A股、全球指数
- 支持股票、ETF、指数、期货、外汇、加密货币
- 支持历史行情、分钟数据、财务报表
- 支持分红、拆股、期权数据
- 支持分析师预期、机构持仓
- 完整的API参考文档
