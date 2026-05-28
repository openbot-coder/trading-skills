# 公司事件数据 (Corporate Event Data)

## 概述

提供 A 股公司事件数据：董监高增减持、定向增发（定增）、股权激励等信息。

## 数据源

| 数据 | 函数 | 数据源 | 状态 |
|------|------|--------|------|
| 上交所增减持 | `stock_share_hold_change_sse()` | akshare | ✅ 国内正常 |
| 深交所增减持 | `stock_share_hold_change_szse()` | akshare | ✅ 国内正常 |
| 定向增发 | `stock_add_stock(symbol)` | akshare | ✅ 国内正常 |

## 命令

### `corp.py share_change` — 股东增减持

```bash
python corp.py share_change --market sse               # 上交所
python corp.py share_change --market szse               # 深交所
python corp.py share_change --market sse --json         # JSON 输出
```

### `corp.py placement <symbol>` — 定向增发明细

```bash
python corp.py placement 600519           # 贵州茅台定增
python corp.py placement 300750 --json    # 宁德时代定增 JSON
```

## 数据状态

✅ 国内直连可用，无需 API key
🔄 每日更新
