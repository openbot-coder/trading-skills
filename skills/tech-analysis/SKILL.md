---
name: tech-analysis
version: 2.0.0
description: 整合7大技术分析引擎生成综合报告 | K线形态/缠论/波浪/谐波/一目均衡/SMC/基础指标
license: MIT
---

# 技术分析综合报告

整合 7 大技术分析引擎，对指定标的生成综合技术面报告。支持加密货币、A股、美股、期货。

## 使用方法

```bash
# === 推荐: 本地 CSV 分析 (离线可用) ===

# 1) 先下载 CSV (以 CCXT 加密货币为例)
cd quantdata/ccxtdata/scripts && python3 ccxt_data.py kline BTC/USDT -e okx -t 1d -l 200 > btc.csv
cd quantdata/baostockdata/scripts && python3 baostock.py kline sz.002050 --start 2025-01-01 > 002050.csv

# 2) 再分析
python3 scripts/ta_report.py --csv btc.csv BTC/USDT
python3 scripts/ta_report.py --csv 002050.csv 002050

# === 在线获取 (需网络+代理) ===
python3 scripts/ta_report.py BTC/USDT -e binance -t 1d -p http://127.0.0.1:7890
python3 scripts/ta_report.py 000001 -e akshare -p http://127.0.0.1:7890
python3 scripts/ta_report.py AAPL -e yfinance -p http://127.0.0.1:7890

# === 指定引擎 ===
python3 scripts/ta_report.py --csv btc.csv BTC/USDT --engines candlestick smc technical-basic

# === 列出所有引擎 ===
python3 scripts/ta_report.py --list-engines
```

## 参数说明

| 参数 | 说明 | 默认值 |
|------|------|--------|
| symbol | 标的代码 | 必填 |
| --csv, -c | 本地 CSV 文件路径 | - |
| --exchange, -e | 交易所 | binance |
| --timeframe, -t | K线周期 | 1d |
| --limit, -n | K线数量 | 200 |
| --engines | 指定引擎 | 全部 |
| --list-engines | 列出引擎 | - |
| --proxy, -p | HTTP(S)代理 | - |

## 数据获取与搜索分工

⚠️ **K线行情数据和市场分析观点使用不同工具，严格分工：**

| 用途 | 工具 | 说明 |
|------|------|------|
| **K线行情数据 (OHLCV)** | quantdata 系列脚本 | 精确价格数据，速度快，不要用搜索替代 |
| **市场观点/研报/舆情** | web-search skill | 多引擎并行搜索，获取分析师观点和市场情绪 |

### K线数据准备

推荐工作流：用 quantdata 工具下载 CSV，再离线分析。

| 数据类型 | 下载工具 | 命令示例 |
|---------|---------|---------|
| 加密货币 | ccxtdata | `ccxt_data.py kline BTC/USDT -e okx -t 1d -l 200 > btc.csv` |
| A股 | baostockdata | `baostock.py kline sz.002050 --start 2025-01-01 > 002050.csv` |
| A股指数 | crawldata | `get_quote.py --kline sh000300` |
| 美股 | yfinancedata | `get_kline.py AAPL --period 1y --interval 1d > aapl.csv` |
| A股(实时) | aksharedata | `akshare.py stock_zh_a_hist 002050 --period daily > 002050.csv` |

> 详见 `quantdata/README_SCRIPTS.md` 了解各数据源完整用法。

### 市场信息搜索（web-search）

需要获取市场分析观点、研报摘要、板块轮动、资金流向等**非价格数据**时，使用 web-search skill：

```bash
# 多引擎并行搜索（推荐，快）
web-search search "沪深300 技术分析 均线 支撑阻力" --json

# 深度研究（多轮搜索）
web-search deep "沪深300 走势研判 后市展望"

# 股票专用搜索
web-search stock "贵州茅台 资金流向"
```

> 详见 `skills/web-search/SKILL.md`。支持 28 个搜索引擎并行抓取。

CSV 自动识别列名 (中英文均支持):
- 英文: `date/time/timestamp, open, high, low, close, volume`
- 中文: `日期/时间, 开盘/开盘价, 最高/最高价, 最低/最低价, 收盘/收盘价, 成交量`
- 编码: UTF-8 / GBK / GB2312 自动检测

## 引擎列表

| 引擎 | 说明 | 依赖 |
|------|------|------|
| candlestick | 15 种经典蜡烛图形态 | 无 |
| chanlun | 分型→笔→中枢→买卖点 | czsc |
| elliott-wave | 5 浪推动 + 3 浪调整 | 无 |
| harmonic | Gartley/Bat/Butterfly/Crab XABCD 五点形态 | 无 |
| ichimoku | 五线系统 + 云带过滤 | 无 |
| smc | BOS/ChoCH 结构突破 + FVG 缺口 | smartmoneyconcepts |
| technical-basic | EMA/RSI/BB/ADX/OBV 投票 | 无 |

## 依赖

```bash
pip install pandas numpy czsc smartmoneyconcepts
# 加密货币数据
pip install ccxt
# A股数据
pip install akshare
# 美股数据
pip install yfinance
```

## 架构

```
skills/tech-analysis/
├── SKILL.md              # 本文件
├── engines/              # 7 个独立信号引擎
│   ├── candlestick.py    # K线形态识别
│   ├── chanlun.py        # 缠论信号
│   ├── elliott_wave.py   # 艾略特波浪
│   ├── harmonic.py       # 谐波形态
│   ├── ichimoku.py       # 一目均衡
│   ├── smc.py            # SMC/ICT
│   └── technical_basic.py # 基础指标
└── scripts/
    └── ta_report.py      # 报告生成器
```

## 信号约定

- `1` = 做多 🟢
- `-1` = 做空 🔴
- `0` = 观望 ⚪

## 输出示例

```
📊 技术分析报告 | BTC/USDT (BINANCE)
⏰ 周期: 1d | 💰 价格: 108,433.57
📈 7日: -3.17% | 30日: +5.27%

📍 关键价位:
  7日区间: 106,150.00 ~ 111,850.00
 30日区间: 102,000.00 ~ 111,850.00

🔬 引擎信号:
  K线形态: 观望 ⚪
  缠论: 观望 ⚪
  艾略特波浪: 观望 ⚪
  谐波形态: 做多 🟢
  一目均衡: 观望 ⚪
  SMC/ICT: 观望 ⚪
  基础指标: 做多 🟢

✅ 综合判定: 偏多 — 多数引擎看涨

⚠ 以上为技术面参考，不构成投资建议。
```

## 完整工作流示例

```
用户: "分析沪深300走势"

Step 1 - 获取K线数据 (quantdata, 快):
  python3 quantdata/crawldata/scripts/get_quote.py --kline sh000300 > /tmp/hs300.csv

Step 2 - 运行技术引擎 (本地计算, 快):
  python3 scripts/ta_report.py --csv /tmp/hs300.csv 沪深300

Step 3 - 搜索市场观点 (web-search, 多路并行快):
  web-search search "沪深300 走势研判 均线支撑" --json
  web-search search "A股 板块轮动 资金流向" --json

Step 4 - 综合引擎信号 + 市场观点，输出报告
```

⚠️ **禁止用 web-search 获取K线价格数据**——慢且不准，必须用 quantdata。

## 脚本路径

本 skill 位于 `skills/tech-analysis/`。脚本通过 `__import__` 从本地 `engines/` 目录加载引擎，无需外部路径依赖。

---

*引擎来源: Vibe-Trading 项目 (HKUDS)*
