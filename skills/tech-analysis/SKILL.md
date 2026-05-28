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
# 全引擎分析（默认）
python3 scripts/ta_report.py BTC/USDT -e binance -t 1d

# A股分析
python3 scripts/ta_report.py 000001 -e akshare

# 美股分析
python3 scripts/ta_report.py AAPL -e yfinance

# 指定引擎
python3 scripts/ta_report.py BTC/USDT --engines candlestick smc technical-basic

# 列出所有引擎
python3 scripts/ta_report.py --list-engines
```

## 参数说明

| 参数 | 说明 | 默认值 |
|------|------|--------|
| symbol | 标的代码 | 必填 |
| --exchange, -e | 交易所 | binance |
| --timeframe, -t | K线周期 | 1d |
| --limit, -n | K线数量 | 200 |
| --engines | 指定引擎 | 全部 |
| --list-engines | 列出引擎 | - |

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

## 脚本路径

本 skill 位于 `skills/tech-analysis/`。脚本通过 `__import__` 从本地 `engines/` 目录加载引擎，无需外部路径依赖。

---

*引擎来源: Vibe-Trading 项目 (HKUDS)*
