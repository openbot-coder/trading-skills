# 分析师一致预期数据 (Analyst Data)

## 概述

提供 A 股分析师一致预期数据：盈利预测（EPS）、机构评级分布、研报数量统计。

## 数据源

- **`stock_profit_forecast_em`** — 东方财富全市场分析师一致预期
  - 覆盖: A 股 2700+ 只股票
  - 字段: EPS-2025e/2026e/2027e/2028e、买入/增持/中性/减持/卖出评级分布、研报数

## 命令

### `analyst.py forecast` — 分析师一致预期

```bash
python analyst.py forecast                   # 表格输出
python analyst.py forecast --json            # JSON 输出
```

### `analyst.py detail <symbol>` — 个股研报明细

```bash
python analyst.py detail 600519              # 贵州茅台研报明细
python analyst.py detail 300750              # 宁德时代
```

## 输出字段

| 字段 | 说明 |
|------|------|
| symbol | 股票代码 |
| name | 股票名称 |
| report_count | 近6个月研报数 |
| rating_buy/hold/neutral/reduce/sell | 机构评级分布 |
| eps_2025e ... eps_2028e | 预测每股收益 |

## 数据状态

✅ 国内直连可用，无需 API key
📊 覆盖 2700+ A 股
🔄 每日更新
