---
name: macrodata
description: 宏观经济数据采集 - 爬虫采集东方财富/金十数据等公开宏观数据，支持中国/美国/欧元区/日本等主要经济体的 CPI/PPI/GDP/PMI/非农等 30+ 项指标
version: 1.0.0
author: macrodata team
tags:
  - macro
  - economic
  - cpi
  - gdp
  - pmi
  - finance
  - macroeconomics
  - 宏观
  - 经济
  - 数据
supported_markets:
  - 中国宏观
  - 美国宏观
  - 欧元区宏观
  - 日本宏观
  - 全球宏观
---

# MacroData - 宏观经济数据采集

宏观经济数据采集中心，支持中国、美国、欧元区、日本等主要经济体的宏观数据查询。

**数据获取优先级链：**

```
爬虫脚本（requests） ⟶  AKShare API（兜底） ⟶  浏览器（最后手段）
    ✓ 快速、低成本             △ 不稳定                ✗ 高 tokens
    ✓ 可控制重试               ○ 接口可能变更            ○ 仅用于经济日历
```

## 快速使用

### 查看所有可用指标

```bash
python scripts/macro.py list
```

### 查询指标

```bash
# 中国 CPI
python scripts/macro.py query cn cpi

# 中国 GDP（季度）
python scripts/macro.py query cn gdp

# 美国非农就业人数
python scripts/macro.py query us nonfarm

# 美国 CPI
python scripts/macro.py query us cpi
```

### 完整宏观报告

```bash
python scripts/macro.py report
```

## 数据源

| 来源 | 数据类型 | 优先级 | 说明 |
|------|---------|--------|------|
| **东方财富** | 中国宏观（CPI/PPI/PMI/GDP/LPR/M2 等 20+ 项） | 🥇 首选 | REST API，返回 JSON，稳定快速 |
| **金十数据** | 美国宏观（非农/CPI/失业率/ADP/零售等 15+ 项） | 🥇 首选 | REST API，返回 JSON |
| **AKShare** | 上述所有 + 其他市场 | 🥈 兜底 | `pip install akshare`，接口可能不稳定 |
| **浏览器** | 经济日历、政策动态、新闻 | 🥉 最后手段 | 仅用于非结构化数据采集 |

## 查询路由规则

| 数据类型 | 识别关键词 | 采集方式 | 路由目标 |
|---------|-----------|---------|---------|
| 中国宏观 | cn/cpi/ppi/gdp/pmi/lpr/m2/社融/工业/进出口 | 爬虫 | macro.py |
| 美国宏观 | us/nonfarm/cpi/ppi/失业/adp/零售/ism/pce | 爬虫 | macro.py |
| 欧元区宏观 | eu/euro/欧央行/欧元 | 爬虫/AKShare | macro.py |
| 日本宏观 | jp/japan/日本/日元 | 爬虫/AKShare | macro.py |
| 经济日历 | 日历/发布时间/经济事件 | 浏览器 | macro_monitor.py |
| 政策动态 | 政策/央行/监管/决议 | 浏览器 | macro_monitor.py |
| 宏观报告 | 报告/汇总/一键 | 组合 | macro.py report |

## 脚本说明

### macro.py - 宏观数据查询脚本

```bash
python scripts/macro.py list                           # 列出所有指标
python scripts/macro.py query <region> <indicator>     # 查询指标
python scripts/macro.py report                         # 生成宏观报告

# 可选参数
python scripts/macro.py query us nonfarm --days 30     # 指定数据天数
python scripts/macro.py query cn cpi --source eastmoney # 指定数据源
python scripts/macro.py query cn cpi --json            # JSON 输出
```

### macro_monitor.py - 深度采集脚本

```bash
python scripts/macro_monitor.py calendar               # 经济日历
python scripts/macro_monitor.py policy                  # 政策动态
python scripts/macro_monitor.py report                  # 完整监控报告
```

## 注意事项

1. **查询频率**: 建议避免频繁请求，间隔至少 1 秒
2. **数据延迟**: 爬虫获取的数据可能有数分钟延迟
3. **接口变更**: 目标网站可能随时调整 API，如遇异常请反馈
4. **AKShare**: 可选择安装以获得额外的数据源兜底（`pip install akshare`）
5. **仅供学习**: 数据仅供参考，不构成投资建议

## 版本历史

### v1.0.0 (2026-05-14)

- 初始版本
- 支持东方财富中国宏观数据爬虫（20+ 指标）
- 支持金十数据美国宏观数据爬虫（15+ 指标）
- 支持 AKShare 兜底
- 支持浏览器深度采集
- 包含指标科普知识库
