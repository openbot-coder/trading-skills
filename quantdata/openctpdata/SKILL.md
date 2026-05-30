---
name: openctpdata
description: OpenCTP 数据中心 | 国内期货/期权/股票全市场品种、合约、交易时段、交易所基础数据 | 完全免费无需注册无限制
version: 0.1.0
author: openctp
tags:
  - futures
  - option
  - stock
  - china
  - exchange
  - contract
  - instrument
  - trading_session
  - data
  - 期货
  - 期权
  - 合约
  - 交易时段
  - 交易所
  - 国内期货
supported_markets:
  - A股（沪深/科创/北交所）
  - 国内期货（全品种）
  - 商品期权
  - 股票期权
  - 债券/基金
---

# OpenCTP Data - 国内期货/期权数据源

免费、无需注册、无访问限制的国内期货数据中心。

## 🔗 API 端点

| 端点 | 用途 | 关键字段 |
|------|------|---------|
| `dict.openctp.cn/products` | 品种信息 | 品种ID、名称、交易所、商品类别 |
| `dict.openctp.cn/instruments` | 合约信息 | 合约乘数、最小变动价位、保证金率、手续费率、交割日期 |
| `dict.openctp.cn/prices` | 行情数据 | 收盘价、结算价、持仓量、涨跌、限价 |
| `dict.openctp.cn/times` | 交易时段 | 夜盘/日盘/午间时段起止时间 |
| `dict.openctp.cn/markets` | 交易所信息 | 交易所ID、全称、简称、时区 |

## 📡 查询示例

### 品种列表
```
查询国内期货全部品种
GET https://dict.openctp.cn/products?types=futures

查询黄金、白银、铜、螺纹的品种
GET https://dict.openctp.cn/products?products=au,ag,cu,rb

查询中金所全部品种
GET https://dict.openctp.cn/products?markets=CFFEX
```

### 合约详情
```
查询黄金、螺纹、沪深300、中证1000合约
GET https://dict.openctp.cn/instruments?types=futures&markets=SHFE,CFFEX&products=au,rb,IF,IM

返回字段：合约乘数、最小变动价位、保证金率、开仓/平仓/平今手续费率、
         交割日期、上市/到期日期、合约状态
```

### 交易时段
```
查询期货夜盘时段（如白银21:00-02:30）
GET https://dict.openctp.cn/times?types=futures&products=ag

查询股指期货交易时段
GET https://dict.openctp.cn/times?types=futures&markets=CFFEX
```

### 实时行情
```
查询所有期货实时行情（前10条）
GET https://dict.openctp.cn/prices?exchanges=SHFE,DCE,CZCE,CFFEX&types=futures&limit=10

查询指定合约行情
GET https://dict.openctp.cn/prices?instruments=au2508,rb2510
```

### 交易所列表
```
查询国内全部交易所
GET https://dict.openctp.cn/markets?areas=China
```

## 🎯 适用场景

| 需求 | 推荐 | 原因 |
|------|------|------|
| **合约保证金/手续费** | openctpdata ⭐ | 实时更新，含做空保证金 |
| **交易时段（夜盘/日盘）** | openctpdata ⭐ | 直接按品种/交易所查询 |
| **品种/合约基础信息** | openctpdata ⭐ | 无需注册，免费无限制 |
| **期货实时行情** | crawldata / 新浪 | openctp盘中数据有延迟，建议用新浪补充 |
| **期货历史K线** | AKShare / 新浪 | openctp无历史K线接口 |
| **tick级数据** | 不支持 | 需CTP实盘或付费数据源 |

## 🔍 参数说明

| 参数 | 含义 | 示例 |
|------|------|------|
| `types` | 商品类型 | `futures`, `option`, `stock`, `bond`, `fund` |
| `areas` | 国家/地区 | `China`, `USA`, `UK`, `Singapore` |
| `markets` | 交易所列表 | `SHFE`, `DCE`, `CZCE`, `CFFEX`, `INE`, `GFEX` |
| `products` | 品种列表 | `au`, `ag`, `cu`, `rb`, `IF`, `IM` |
| `instruments` | 合约列表 | `au2508`, `rb2510`, `IF2606` |
| `limit` | 返回条数 | `10`, `100` |

## 📝 注意事项

- 品种/合约数据在每日盘前（08:15后）、盘后（20:15后）从实盘同步
- 盘中行情可能不完整，建议盘后查询
- **无历史K线数据**，需配合 AKShare 或新浪财经
- 实时行情建议用新浪期货接口补足

## 💡 使用示例

```
✅ 查黄金期货保证金率和手续费
✅ 查白银夜盘交易时段
✅ 查某合约最后交易日和交割日期
✅ 查螺纹钢所有在途合约列表
✅ 查国内全部期货交易所及简称
```
