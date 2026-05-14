# MacroData AI 使用指南

## 概述

MacroData 是宏观经济数据采集子技能，通过爬虫脚本直接从东方财富、金十数据等公开数据源获取宏观数据。

## 命令执行方式

### 1. 查询指标

```bash
python scripts/macro.py query cn cpi
python scripts/macro.py query us nonfarm
python scripts/macro.py query cn gdp
```

### 2. 列出所有可用指标

```bash
python scripts/macro.py list
```

### 3. 生成宏观报告

```bash
python scripts/macro.py report
```

### 4. 深度采集（浏览器）

```bash
python scripts/macro_monitor.py calendar
python scripts/macro_monitor.py policy
```

## 输出格式

所有命令输出为表格格式，方便阅读：

```
指标名       当前值      前值      变动      更新时间
─────────────────────────────────────────────────────
中国CPI      0.3%       0.1%      +0.2%     2026-04
中国GDP      5.4%       5.3%      +0.1%     2026-Q1
```

使用 `--json` 参数可获取 JSON 格式输出。

## 数据源优先级

1. **东方财富 API**（中国宏观，最稳定）
2. **金十数据 API**（美国/全球宏观）
3. **AKShare**（兜底，需安装）
4. **浏览器采集**（仅经济日历/政策）

## 常见问题

- **数据不更新**：目标网站接口可能变更，等待修复
- **AKShare 报错**：AKShare 内部代码可能已更新，不影响主要爬虫功能
- **浏览器采集慢**：属于正常现象，建议优先使用爬虫脚本
