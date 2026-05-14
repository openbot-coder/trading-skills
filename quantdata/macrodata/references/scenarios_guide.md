# MacroData 场景指南

## 场景 1：查看最新 CPI 数据

```
用户：最近 CPI 数据怎么样？
AI：python scripts/macro.py query cn cpi
```

## 场景 2：查看美国非农就业

```
用户：美国非农数据发布了没有？
AI：python scripts/macro.py query us nonfarm
```

## 场景 3：对比中美通胀数据

```
用户：对比一下中美 CPI
AI：
  python scripts/macro.py query cn cpi
  python scripts/macro.py query us cpi
```

## 场景 4：生成宏观晨报

```
用户：给我一份今天的宏观数据汇总
AI：python scripts/macro.py report
```

## 场景 5：查看经济日历

```
用户：本周有哪些重要的经济数据发布？
AI：python scripts/macro_monitor.py calendar
```

## 场景 6：检查最新政策动态

```
用户：最近央行有什么新政策？
AI：python scripts/macro_monitor.py policy
```

## 场景 7：数据可视化分析

```
用户：最近一年 CPI 走势如何？
AI：
  python scripts/macro.py query cn cpi --days 365 --json
  （将 JSON 数据转换为图表）
```

## 场景 8：组合查询多个指标

```
用户：中国经济现状怎么样？
AI：
  python scripts/macro.py query cn gdp    # GDP
  python scripts/macro.py query cn cpi    # 通胀
  python scripts/macro.py query cn pmi    # PMI
  python scripts/macro.py query cn m2     # 货币供应
```
