# 宏观数据模块 (Macro Data)

## 概述

提供中美债券收益率、外汇汇率、VIX 恐慌指数、美元指数等宏观数据查询。

## 命令

### `macro_aux.py bond` — 中美国债收益率

基于 akshare `bond_zh_us_rate()`，包含：
- 中国国债收益率：2Y / 5Y / 10Y / 30Y
- 美国国债收益率：2Y / 5Y / 10Y / 30Y

```bash
python macro_aux.py bond                    # 最近30天
python macro_aux.py bond -d 5               # 最近5天
python macro_aux.py bond --json             # JSON 输出
```

### `macro_aux.py curve` — 中国国债收益率曲线

基于 akshare `bond_china_yield()`，全期限曲线。

```bash
python macro_aux.py curve
```

### `macro_aux.py fx` — 外汇实时汇率

基于 akshare `fx_spot_quote()`，25个货币对 (USD/CNY, EUR/CNY, JPY/CNY 等)。

```bash
python macro_aux.py fx
python macro_aux.py fx --json
```

### `macro_aux.py vix` — VIX 恐慌指数

基于 yfinance `^VIX`。包含 OHLC 日线数据。支持超时配置。

```bash
python macro_aux.py vix                    # 默认超时15秒
python macro_aux.py vix -d 60              # 最近60天
python macro_aux.py vix -t 30              # 超时30秒
python macro_aux.py vix --json             # JSON 输出
```

### `macro_aux.py dxy` — 美元指数 DXY

基于 yfinance `DX-Y.NYB`。支持超时配置。

```bash
python macro_aux.py dxy                    # 默认超时15秒
python macro_aux.py dxy -t 30              # 超时30秒
python macro_aux.py dxy --json
```

### `macro_aux.py fred` — FRED 数据查询

基于 FRED API (CSV 直接下载)。支持系列：
DGS10, DGS2, DGS30, DGS5, DGS1, DTWEXBGS, DTWEXM, VIXCLS, DEXUSEU, DEXJPUS, DEXCHUS, DEXUSUK

**注意**: FRED 从中国大陆连接不稳定，可能超时。

```bash
python macro_aux.py fred -s DGS10,VIXCLS
python macro_aux.py fred -s DGS10 -d 90 --json
```

## 数据源优先级

| 数据              | 主力源              | 备用源       | 工作状态          |
|------------------|---------------------|-------------|------------------|
| 中美国债收益率     | akshare            | —           | ✅ 国内正常        |
| 中国收益率曲线     | akshare            | —           | ✅ 国内正常        |
| 外汇汇率          | akshare            | —           | ✅ 国内正常        |
| VIX              | yfinance (^VIX)    | FRED VIXCLS | ⚠️ 需海外网络      |
| 美元指数 DXY      | yfinance (DX-Y.NYB)| —           | ⚠️ 需海外网络      |
| FRED 系列         | 直接 CSV 下载       | —           | ⚠️ 国内不稳定      |
| 融资融券余额       | akshare            | —           | ✅ 国内正常        |
| 恐贪指数          | alternative.me     | —           | ✅ 免费无 key      |
