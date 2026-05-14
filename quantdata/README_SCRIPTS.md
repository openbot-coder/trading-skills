# QuantData CLI 脚本使用说明

本目录下包含了各子 skills 的 Python CLI 脚本，方便快速查询数据。

## 前置准备

### 安装依赖

```bash
# 基础依赖
pip install requests

# 根据需要安装各个子 skills 的依赖
pip install yfinance pandas
pip install baostock
```

## 目录结构

```
quantdata/
├── coingeckodata/
│   └── scripts/
│       ├── coingecko.py          # CoinGecko 综合脚本（推荐）
│       ├── get_crypto_price.py   # 加密货币价格
│       └── get_top_crypto.py     # 加密货币市值排行
├── yfinancedata/
│   └── scripts/
│       ├── yfinance.py          # Yahoo Finance 综合脚本（推荐）
│       ├── get_stock_price.py   # 股票价格
│       └── get_kline.py        # 股票K线
├── baostockdata/
│   └── scripts/
│       ├── baostock.py         # Baostock 综合脚本（推荐）
│       └── get_kline.py       # A股K线
├── westockdata/
│   └── scripts/
│       └── get_quote.py        # 股票行情
├── okxdata/
│   └── scripts/
│       └── okx.py             # OKX 综合脚本（推荐）
├── binancedata/
│   └── scripts/
│       └── binance.py          # Binance 综合脚本（推荐）
├── crawldata/
│   └── scripts/
│       └── get_quote.py        # 腾讯/新浪财经综合脚本（推荐）- 实时行情 + K线
└── README_SCRIPTS.md          # 本文档
```

## 综合脚本使用（推荐）

### 0. CrawlData - crawldata/scripts/get_quote.py (A股/K线推荐)

```bash
# 查看帮助
python quantdata/crawldata/scripts/get_quote.py --help

# 实时行情查询
python quantdata/crawldata/scripts/get_quote.py sh600000
python quantdata/crawldata/scripts/get_quote.py sh600000 sz000001 hf_GC M0
python quantdata/crawldata/scripts/get_quote.py sh600000 --detail
python quantdata/crawldata/scripts/get_quote.py sh600000 --json

# K线数据查询 - 腾讯财经（推荐）
python quantdata/crawldata/scripts/get_quote.py --kline sz000001
python quantdata/crawldata/scripts/get_quote.py --kline --period weekly sz000001
python quantdata/crawldata/scripts/get_quote.py --kline --period monthly sz000001
python quantdata/crawldata/scripts/get_quote.py --kline --year 2024 sz000001

# K线数据查询 - 新浪财经（分钟K线）
python quantdata/crawldata/scripts/get_quote.py --kline --source sina --period 5min sz000001
python quantdata/crawldata/scripts/get_quote.py --kline --source sina --period 15min sz000001
```

### 1. CoinGecko - coingeckodata/scripts/coingecko.py

```bash
# 查看帮助
python quantdata/coingeckodata/scripts/coingecko.py --help

# 获取加密货币价格
python quantdata/coingeckodata/scripts/coingecko.py price bitcoin
python quantdata/coingeckodata/scripts/coingecko.py price "bitcoin,ethereum,solana" --cny

# 获取市值排行榜
python quantdata/coingeckodata/scripts/coingecko.py top
python quantdata/coingeckodata/scripts/coingecko.py top --top 10 --change 7d

# 获取K线历史
python quantdata/coingeckodata/scripts/coingecko.py kline bitcoin --days 30

# 获取全球市场数据
python quantdata/coingeckodata/scripts/coingecko.py global

# 搜索加密货币
python quantdata/coingeckodata/scripts/coingecko.py search bitcoin
```

### 2. Yahoo Finance - yfinancedata/scripts/yfinance.py

```bash
# 查看帮助
python quantdata/yfinancedata/scripts/yfinance.py --help

# 获取股票实时价格
python quantdata/yfinancedata/scripts/yfinance.py price AAPL
python quantdata/yfinancedata/scripts/yfinance.py price AAPL MSFT TSLA

# 获取K线数据
python quantdata/yfinancedata/scripts/yfinance.py kline AAPL
python quantdata/yfinancedata/scripts/yfinance.py kline AAPL --period 1y --interval 1d --top 60

# 获取股票详细信息
python quantdata/yfinancedata/scripts/yfinance.py info AAPL

# 获取财务数据
python quantdata/yfinancedata/scripts/yfinance.py financials AAPL
```

### 3. Baostock - baostockdata/scripts/baostock.py

```bash
# 查看帮助
python quantdata/baostockdata/scripts/baostock.py --help

# 获取K线数据
python quantdata/baostockdata/scripts/baostock.py kline sh.600000
python quantdata/baostockdata/scripts/baostock.py kline sh.600000 --start 2024-01-01 --frequency d --adjustflag 2

# 获取财务数据
python quantdata/baostockdata/scripts/baostock.py profit sh.600000

# 获取宏观经济数据
python quantdata/baostockdata/scripts/baostock.py macro deposit
python quantdata/baostockdata/scripts/baostock.py macro loan
```

### 4. OKX - okxdata/scripts/okx.py

```bash
# 查看帮助
python quantdata/okxdata/scripts/okx.py --help

# 获取最新价格
python quantdata/okxdata/scripts/okx.py ticker BTC-USDT
python quantdata/okxdata/scripts/okx.py ticker BTC-USDT ETH-USDT

# 获取K线数据
python quantdata/okxdata/scripts/okx.py kline BTC-USDT --bar 1d --limit 100
```

### 6. MacroData - macrodata/scripts/macro.py (新增，宏观数据)

```bash
# 查看帮助
python quantdata/macrodata/scripts/macro.py --help

# 列出所有可用宏观指标
python quantdata/macrodata/scripts/macro.py list

# 查询中国宏观指标
python quantdata/macrodata/scripts/macro.py query cn cpi
python quantdata/macrodata/scripts/macro.py query cn ppi
python quantdata/macrodata/scripts/macro.py query cn pmi
python quantdata/macrodata/scripts/macro.py query cn gdp
python quantdata/macrodata/scripts/macro.py query cn m2
python quantdata/macrodata/scripts/macro.py query cn lpr

# 查询美国宏观指标
python quantdata/macrodata/scripts/macro.py query us nonfarm
python quantdata/macrodata/scripts/macro.py query us cpi
python quantdata/macrodata/scripts/macro.py query us unemployment
python quantdata/macrodata/scripts/macro.py query us ism_pmi

# 输出 JSON 格式
python quantdata/macrodata/scripts/macro.py query cn cpi --json

# 生成综合宏观报告
python quantdata/macrodata/scripts/macro.py report
```

### 5. Binance - binancedata/scripts/binance.py

```bash
# 查看帮助
python quantdata/binancedata/scripts/binance.py --help

# 获取最新价格
python quantdata/binancedata/scripts/binance.py ticker BTCUSDT
python quantdata/binancedata/scripts/binance.py ticker BTCUSDT ETHUSDT

# 获取K线数据
python quantdata/binancedata/scripts/binance.py kline BTCUSDT --interval 1d --limit 100
```

## 子命令说明

### coingecko.py

| 子命令 | 功能 |
|--------|------|
| `price` | 获取加密货币价格 |
| `top` | 获取市值排行榜 |
| `kline` | 获取K线历史 |
| `global` | 获取全球市场数据 |
| `search` | 搜索加密货币 |

### yfinance.py

| 子命令 | 功能 |
|--------|------|
| `price` | 获取股票实时价格 |
| `kline` | 获取K线数据 |
| `info` | 获取股票详细信息 |
| `financials` | 获取财务数据 |

### baostock.py

| 子命令 | 功能 |
|--------|------|
| `kline` | 获取K线数据 |
| `profit` | 获取财务数据 |
| `macro` | 获取宏观经济数据 |

### okx.py / binance.py

| 子命令 | 功能 |
|--------|------|
| `ticker` | 获取最新价格 |
| `kline` | 获取K线数据 |

## 快速参考

| 数据源 | 综合脚本 | 主要功能 |
|--------|---------|---------|
| **crawldata** | `get_quote.py` | A股实时行情、期货行情、K线数据（日K/周K/月K/分钟K） |
| **coingeckodata** | `coingecko.py` | 加密货币价格、市值排行、K线、全球数据 |
| **yfinancedata** | `yfinance.py` | 美股/全球股票、K线、财务数据 |
| **baostockdata** | `baostock.py` | A股K线、财务数据、宏观经济 |
| **okxdata** | `okx.py` | OKX 加密货币行情、K线 |
| **binancedata** | `binance.py` | Binance 加密货币行情、K线 |
| **macrodata** | `macro.py` | 宏观数据查询（中国/美国 CPI/PPI/PMI/GDP 等 30+ 指标） |

## 注意事项

1. **网络问题**: 部分数据源需要良好的网络环境
2. **API限流**: 频繁调用可能触发限流，注意控制频率
3. **数据延迟**: 不同数据源延迟不同，实时性要求高时注意选择
4. **时区问题**: 注意数据的时区设置

## 反馈

如有问题或建议，欢迎反馈！
