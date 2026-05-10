---
name: crawldata
description: 财经爬虫数据接口 - 腾讯财经(股票/指数/国际期货) + 新浪财经(中国期货)实时行情查询 + K线数据下载
disable-model-invocation: true
---

# CrawlData - 财经爬虫数据接口

整合腾讯财经和新浪财经公开接口，提供全面的实时行情数据查询和K线数据下载。

## 接口信息

### 腾讯财经接口（股票、指数、国际期货）
- **接口地址**: `https://qt.gtimg.cn/q=`
- **请求方式**: GET
- **数据格式**: 文本格式，以 `~` 分隔字段
- **编码**: GBK

### 新浪财经接口（中国期货）
- **接口地址**: `http://hq.sinajs.cn/list=`
- **请求方式**: GET
- **数据格式**: JavaScript变量，以 `,` 分隔字段
- **编码**: GBK
- **需要Header**: `Referer: http://finance.sina.com.cn/`

## K线数据接口

### 腾讯K线接口（推荐）
- **日K线**: `https://data.gtimg.cn/flashdata/hushen/latest/daily/{code}.js`
- **周K线**: `https://data.gtimg.cn/flashdata/hushen/latest/weekly/{code}.js`
- **月K线**: `https://data.gtimg.cn/flashdata/hushen/monthly/{code}.js`
- **指定年份日K**: `https://data.gtimg.cn/flashdata/hushen/daily/{year}/{code}.js`

### 新浪K线接口（分钟K线）
- **接口地址**: `http://money.finance.sina.com.cn/quotes_service/api/json_v2.php/CN_MarketData.getKLineData`
- **参数**: `symbol={code}&scale={minutes}&ma={ma}&datalen={datalen}`

## 支持品种

### 腾讯财经 - 股票代码格式

| 市场 | 前缀 | 示例 |
|------|------|------|
| 上海 | sh | sh600000 |
| 深圳 | sz | sz000001 |

### 腾讯财经 - 指数代码

| 代码 | 名称 |
|------|------|
| sh000001 | 上证指数 |
| sh000300 | 沪深300 |
| sh000016 | 上证50 |
| sh000905 | 中证500 |
| sh000852 | 中证1000 |
| sh000688 | 科创50 |
| sz399001 | 深证成指 |
| sz399006 | 创业板指 |

### 腾讯财经 - 国际期货代码

| 代码 | 名称 |
|------|------|
| hf_GC | 纽约黄金 |
| hf_SI | 纽约白银 |
| hf_HG | 纽约铜 |
| hf_CL | 纽约原油 |
| hf_OIL | 布伦特原油 |
| hf_NG | 美国天然气 |
| hf_XAU | 伦敦金（现货） |
| hf_XAG | 伦敦银（现货） |

### 新浪财经 - 中国期货代码

#### 商品期货连续合约（品种代码 + 0）

| 代码 | 名称 | 交易所 |
|------|------|--------|
| M0 | 豆粕连续 | 大商所 |
| Y0 | 豆油连续 | 大商所 |
| A0 | 豆一连续 | 大商所 |
| C0 | 玉米连续 | 大商所 |
| I0 | 铁矿石连续 | 大商所 |
| J0 | 焦炭连续 | 大商所 |
| JM0 | 焦煤连续 | 大商所 |
| L0 | 聚乙烯连续 | 大商所 |
| P0 | 棕榈油连续 | 大商所 |
| V0 | PVC连续 | 大商所 |
| JD0 | 鸡蛋连续 | 大商所 |
| RB0 | 螺纹钢连续 | 上期所 |
| CU0 | 沪铜连续 | 上期所 |
| AU0 | 黄金连续 | 上期所 |
| AG0 | 白银连续 | 上期所 |
| RU0 | 橡胶连续 | 上期所 |
| BU0 | 沥青连续 | 上期所 |
| FU0 | 燃油连续 | 上期所 |
| AL0 | 沪铝连续 | 上期所 |
| ZN0 | 沪锌连续 | 上期所 |
| PB0 | 沪铅连续 | 上期所 |
| NI0 | 沪镍连续 | 上期所 |
| SN0 | 沪锡连续 | 上期所 |
| SS0 | 不锈钢连续 | 上期所 |
| NR0 | 20号胶连续 | 上期能源 |
| SC0 | 原油连续 | 上期能源 |
| LU0 | 低硫燃油连续 | 上期能源 |
| TA0 | PTA连续 | 郑商所 |
| SR0 | 白糖连续 | 郑商所 |
| CF0 | 棉花连续 | 郑商所 |
| FG0 | 玻璃连续 | 郑商所 |
| MA0 | 甲醇连续 | 郑商所 |
| RM0 | 菜粕连续 | 郑商所 |
| OI0 | 菜籽油连续 | 郑商所 |
| ZC0 | 动力煤连续 | 郑商所 |
| EG0 | 乙二醇连续 | 大商所 |
| EB0 | 苯乙烯连续 | 大商所 |
| PG0 | 液化石油气连续 | 大商所 |
| LC0 | 碳酸锂连续 | 广期所 |

#### 金融期货（NF_前缀 + 合约代码）

| 代码格式 | 说明 | 示例 |
|----------|------|------|
| NF_IF{年月} | 沪深300股指期货 | NF_IF2508 |
| NF_IC{年月} | 中证500股指期货 | NF_IC2508 |
| NF_IH{年月} | 上证50股指期货 | NF_IH2508 |
| NF_IM{年月} | 中证1000股指期货 | NF_IM2508 |
| NF_T{年月} | 10年期国债期货 | NF_T2506 |
| NF_TF{年月} | 5年期国债期货 | NF_TF2506 |
| NF_TS{年月} | 2年期国债期货 | NF_TS2506 |

## 字段说明（前52个字段）

| 序号 | 字段名 | 说明 |
|------|--------|------|
| 0 | exchange_id | 交易所ID: 1=上海, 51=深圳 |
| 1 | name | 合约名称 |
| 2 | code | 合约代码 |
| 3 | last_price | 最新价 |
| 4 | pre_close | 昨收价 |
| 5 | open | 开盘价 |
| 6 | volume | 成交量（手） |
| 7 | outer_plate | 外盘（手） |
| 8 | inner_plate | 内盘（手） |
| 9 | bid1_price | 买1价 |
| 10 | bid1_volume | 买1量 |
| 11 | bid2_price | 买2价 |
| 12 | bid2_volume | 买2量 |
| 13 | bid3_price | 买3价 |
| 14 | bid3_volume | 买3量 |
| 15 | bid4_price | 买4价 |
| 16 | bid4_volume | 买4量 |
| 17 | bid5_price | 买5价 |
| 18 | bid5_volume | 买5量 |
| 19 | ask1_price | 卖1价 |
| 20 | ask1_volume | 卖1量 |
| 21 | ask2_price | 卖2价 |
| 22 | ask2_volume | 卖2量 |
| 23 | ask3_price | 卖3价 |
| 24 | ask3_volume | 卖3量 |
| 25 | ask4_price | 卖4价 |
| 26 | ask4_volume | 卖4量 |
| 27 | ask5_price | 卖5价 |
| 28 | ask5_volume | 卖5量 |
| 29 | recent_trades | 最近逐笔成交 |
| 30 | datetime | 时间 (yyyymmddhhmmss) |
| 31 | change | 涨跌额 |
| 32 | change_pct | 涨跌幅(%) |
| 33 | high | 最高价 |
| 34 | low | 最低价 |
| 35 | combined | 组合字段: 最新价/成交量/成交额(元) |
| 36 | volume2 | 成交量（手） |
| 37 | turnover | 成交额（万） |
| 38 | turnover_rate | 换手率(%) |
| 39 | pe_ratio | 市盈率 |
| 40 | field40 | 空字段 |
| 41 | high2 | 最高价 |
| 42 | low2 | 最低价 |
| 43 | amplitude | 振幅(%) |
| 44 | market_cap_float | 流通市值 |
| 45 | market_cap_total | 总市值 |
| 46 | pb_ratio | 市净率 |
| 47 | price_limit_high | 涨停价 |
| 48 | price_limit_low | 跌停价 |
| 49 | volume_ratio | 量比 |
| 50 | field50 | 空字段 |
| 51 | average_price | 均价 |

## 使用说明

### 单品种查询

```
https://qt.gtimg.cn/q=sh600000
```

### 批量查询（最多100个）

```
https://qt.gtimg.cn/q=sh600000,sz000001,hf_GC
```

### 响应示例

```
v_sh600000="1~浦发银行~600000~8.50~8.45~8.48~1234567~...";
```

## 注意事项

1. **查询频率**: 建议间隔100ms以上，避免IP被封
2. **批量查询**: 一次最多查询100个代码
3. **编码**: 返回数据使用GBK编码
4. **数据延迟**: 实时行情可能有轻微延迟
5. **用途**: 仅供学习和研究使用

## 脚本使用

见 `scripts/` 目录下的查询脚本。

### get_quote.py - 综合行情查询脚本

#### 实时行情查询
```bash
# 查看帮助
python scripts/get_quote.py --help

# 查询单个品种
python scripts/get_quote.py sh600000

# 批量查询
python scripts/get_quote.py sh600000 sz000001 hf_GC

# 详细信息输出
python scripts/get_quote.py sh600000 --detail

# JSON格式输出
python scripts/get_quote.py sh600000 --json
```

#### K线数据查询
```bash
# 腾讯日K线（默认）
python scripts/get_quote.py --kline sz000001

# 腾讯周K线
python scripts/get_quote.py --kline --period weekly sz000001

# 腾讯月K线
python scripts/get_quote.py --kline --period monthly sz000001

# 腾讯指定年份日K线
python scripts/get_quote.py --kline --year 2024 sz000001

# 新浪5分钟K线
python scripts/get_quote.py --kline --source sina --period 5min sz000001

# 新浪15分钟K线
python scripts/get_quote.py --kline --source sina --period 15min sz000001

# K线JSON输出
python scripts/get_quote.py --kline sz000001 --json
```

#### K线查询参数说明
| 参数 | 说明 | 可选值 |
|------|------|--------|
| `--kline` | 启用K线查询模式 | - |
| `--period` | K线周期 | daily/weekly/monthly/5min/15min/30min/60min |
| `--year` | 指定年份（仅腾讯日K有效） | 如2024 |
| `--source` | 数据源 | tencent（默认）/ sina |

#### 缓存控制参数
| 参数 | 说明 |
|------|------|
| `--no-cache` | 禁用缓存（每次请求都从网络获取） |
| `--clear-cache` | 清除所有缓存并退出 |

## 缓存机制

### 缓存策略
- **实时行情**: A股3秒，其他市场1秒
- **K线数据**: 1小时
- **缓存存储**: 内存 + 文件双重缓存

### 缓存目录
默认缓存目录：`~/.quantdata_cache/`

### 缓存清除
```bash
# 清除所有缓存
python scripts/get_quote.py --clear-cache

# 单次不使用缓存
python scripts/get_quote.py --no-cache sh600000
```

## 相关文档

- `references/field_reference.md` - 完整字段参考
- `references/api_guide.md` - API使用指南
