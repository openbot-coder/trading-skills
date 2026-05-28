---
name: tech-analysis
description: 综合技术分析报告生成器 | 整合7大技术分析体系（K线形态/缠论/艾略特波浪/谐波/一目均衡/SMC/基础指标）| 一键生成多维度技术面报告
version: 1.0.0
author: quantdata
tags:
  - technical-analysis
  - report
  - candlestick
  - elliott-wave
  - harmonic
  - ichimoku
  - smc
  - chanlun
  - indicator
supported_markets:
  - A股
  - 港股
  - 美股
  - 加密货币
  - 期货
---

# Tech Analysis — 综合技术分析报告

整合 7 大技术分析体系，一键生成多维度技术面报告。

## 技术分析体系

| 体系 | 来源 | 核心方法 | 信号类型 |
|------|------|---------|---------|
| **K线形态** | candlestick | 15种经典蜡烛图形态 | 反转/持续 |
| **缠论** | chanlun | 分型→笔→中枢→买卖点 | 结构性买卖点 |
| **艾略特波浪** | elliott-wave | 5浪推动+3浪调整 | 趋势/调整 |
| **谐波形态** | harmonic | XABCD五点+Fibonacci | PRZ反转 |
| **一目均衡** | ichimoku | 五线+云带 | 趋势确认 |
| **SMC/ICT** | smc | BOS/ChoCH/FVG/OB | 机构行为 |
| **基础指标** | technical-basic | EMA/ADX/BB/RSI/OBV | 趋势/超买超卖/量价 |

## 命令用法

```bash
# 生成综合技术分析报告（默认日线）
python3 {base}/scripts/ta_report.py BTC/USDT
python3 {base}/scripts/ta_report.py BTC/USDT --exchange okx --timeframe 4h

# A股
python3 {base}/scripts/ta_report.py 000001.SZ --exchange akshare

# 指定输出格式
python3 {base}/scripts/ta_report.py BTC/USDT --format markdown
python3 {base}/scripts/ta_report.py BTC/USDT --format json

# 选择性分析（只跑部分体系）
python3 {base}/scripts/ta_report.py BTC/USDT --engines candlestick,technical-basic,ichimoku
```

## 报告结构

```
═══ BTC/USDT 技术分析报告 ═══
时间: 2026-05-28 | 周期: 1d | 收盘: 68,452.30

── 1. 综合信号 ──────────────
多空比: 5看多 / 2看空 / 0中性 → 偏多 ✅
综合评分: +3 (范围 -7 ~ +7)

── 2. K线形态 ──────────────
最新形态: 看涨吞没 (Bullish Engulfing) → +1
近期形态: 锤子线 (Hammer) @ 05-25 → +1

── 3. 缠论 ──────────────
当前: 日线三买形成中
中枢: [67200, 68800]
最近买卖点: 二买 @ 67,450 (05-22)

── 4. 艾略特波浪 ──────────────
当前结构: 第3浪上升中
Fibonacci目标: 70,200 (1.618×浪1)

── 5. 谐波形态 ──────────────
检测到: 看涨Bat形态 (D点未到)
PRZ区域: 66,800 ~ 67,500

── 6. 一目均衡 ──────────────
云带位置: 价格在云上方 → 看多
TK交叉: 金叉 (05-20)
云带方向: 上升

── 7. SMC/ICT ──────────────
最近BOS: 看涨BOS (05-26) → +1
ChoCH: 无
FVG: 看涨FVG @ 67,100 ~ 67,800

── 8. 基础指标 ──────────────
趋势: EMA12>EMA26, ADX=28 (强趋势)
均值回归: RSI=62, BB中轨上方
量价: OBV上升, 量比1.2
投票: 看多 (+2)

── 9. 关键价位 ──────────────
强阻力: 70,200 (Fib 1.618 + 前高)
弱阻力: 69,000
当前价: 68,452
弱支撑: 67,500 (BB中轨 + FVG下沿)
强支撑: 66,800 (谐波PRZ + 缠论中枢)
```

## 信号汇总规则

每个引擎输出 `+1`(看多) / `-1`(看空) / `0`(中性)，最终汇总：

| 综合评分 | 含义 |
|---------|------|
| +5 ~ +7 | 强烈看多 |
| +2 ~ +4 | 偏多 |
| -1 ~ +1 | 中性/震荡 |
| -4 ~ -2 | 偏空 |
| -7 ~ -5 | 强烈看空 |

## 数据源要求

脚本需要获取 OHLCV 数据，支持以下数据源（按优先级）：

| 数据源 | 市场 | 需要Key |
|--------|------|---------|
| akshare | A股 | ❌ |
| ccxt | 加密货币 | ❌ |
| okxdata | 加密货币 | ❌ |
| binancedata | 加密货币 | ❌ |
| yfinance | 美股/港股 | ❌ |
| tushare | A股 | ✅ |

## 依赖

- Python >= 3.10
- pandas, numpy
- czsc（缠论，可选）
- smartmoneyconcepts（SMC，可选）

缺少可选依赖时，对应引擎自动跳过，不影响其他分析。

## 使用场景

- **每日复盘**：收盘后跑一次，快速了解多空格局
- **入场决策**：交易前检查多体系是否共振
- **风控预警**：关注看空信号占比
- **研报素材**：导出 markdown 格式作为研报附件
