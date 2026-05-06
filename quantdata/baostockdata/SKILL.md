---
name: baostockdata
description: Baostock证券数据接口 | 免费开源的A股历史行情数据 | 支持日/周/月K线、分钟线、财务数据
version: 1.0.0
author: baostock team
tags:
  - quantitative
  - finance
  - A股
  - historical-data
  - kline
  - financial-data
supported_markets:
  - A股（沪市/深市/北交所）
supported_data_types:
  - kline
  - minute
  - financial
  - dividend
  - index
---

# Baostock Data - A股历史数据专家

免费、开源的证券历史数据接口，专为量化回测和数据分析设计。

## 核心定位

**Baostock** 是一个专注于A股历史数据的免费数据源，提供：

1. **超长历史数据**：1990年至今的完整行情数据
2. **多时间频率**：日、周、月K线，以及5/15/30/60分钟线
3. **完整财务数据**：财务报表、估值指标、公司报告
4. **复权数据**：支持前复权、后复权、不复权
5. **Python原生**：直接返回Pandas DataFrame格式

## 核心优势

| 特性 | 说明 |
|------|------|
| **免费使用** | 无需注册，无需API Key |
| **无请求限制** | 不限次数，适合批量获取 |
| **超长历史** | 数据从1990年开始 |
| **复权支持** | 前复权/后复权/不复权 |
| **Python原生** | 直接返回DataFrame |
| **稳定可靠** | 高校量化课程默认数据源 |

## 数据覆盖

### 行情数据

| 数据类型 | 时间范围 | 频率 | 说明 |
|---------|---------|------|------|
| **日K线** | 1990-12-19至今 | 日 | 支持前/后复权 |
| **周K线** | 1990-12-19至今 | 周 | 每周最后一个交易日 |
| **月K线** | 1990-12-19至今 | 月 | 每月最后一个交易日 |
| **5分钟线** | 1999-07-26至今 | 5分钟 | 日内高频数据 |
| **15分钟线** | 1999-07-26至今 | 15分钟 | 日内高频数据 |
| **30分钟线** | 1999-07-26至今 | 30分钟 | 日内高频数据 |
| **60分钟线** | 1999-07-26至今 | 60分钟 | 日内高频数据 |

### 指数数据

| 指数类型 | 说明 |
|---------|------|
| **综合指数** | 上证综指、深证成指等 |
| **规模指数** | 沪深300、中证500等 |
| **行业指数** | 一级行业、二级行业指数 |
| **策略指数** | 各种策略指数 |
| **基金指数** | ETF、LOF等基金指数 |

### 财务数据

| 数据类型 | 时间范围 | 频率 | 说明 |
|---------|---------|------|------|
| **资产负债表** | 2007年至今 | 季频 | 上市公司资产负债信息 |
| **利润表** | 2007年至今 | 季频 | 上市公司利润信息 |
| **现金流量表** | 2007年至今 | 季频 | 上市公司现金信息 |
| **杜邦指标** | 2007年至今 | 季频 | 财务指标综合分析 |
| **估值指标** | 日频 | 日 | PE、PB、PS等 |

### 公司报告

| 数据类型 | 时间范围 | 频率 | 说明 |
|---------|---------|------|------|
| **业绩预告** | 2003年至今 | 季频 | 上市公司业绩预告信息 |
| **业绩快报** | 2006年至今 | 季频 | 上市公司业绩快报信息 |

### 宏观经济数据

| 数据类型 | API函数 | 时间范围 | 频率 | 说明 |
|---------|---------|---------|------|------|
| **存款利率** | `query_deposit_rate_data()` | 历史至今 | 月频 | 人民币存款基准利率 |
| **贷款利率** | `query_loan_rate_data()` | 历史至今 | 月频 | 人民币贷款基准利率 |
| **存款准备金率** | `query_required_reserve_ratio_data()` | 历史至今 | 月频 | 金融机构存款准备金率 |
| **货币供应量** | `query_money_supply_data_month()` | 历史至今 | 月频 | 月度货币供应量(M0/M1/M2) |
| **货币供应量(年底余额)** | `query_money_supply_data_year()` | 历史至今 | 年频 | 年度货币供应量 |

#### 宏观经济数据API使用示例

```python
# 查询存款利率
rs = bs.query_deposit_rate_data()
df_deposit = rs.get_data()

# 查询贷款利率
rs = bs.query_loan_rate_data()
df_loan = rs.get_data()

# 查询存款准备金率
rs = bs.query_required_reserve_ratio_data()
df_reserve = rs.get_data()

# 查询月度货币供应量
rs = bs.query_money_supply_data_month()
df_money = rs.get_data()

# 查询年度货币供应量
rs = bs.query_money_supply_data_year()
df_money_year = rs.get_data()
```

#### 存款利率数据结构

| 字段 | 说明 |
|------|------|
| date | 日期 |
| deposit_type | 存款类型 |
| rate | 利率 |

**存款类型示例**：
- 活期
- 3个月定期
- 6个月定期
- 1年定期
- 2年定期
- 3年定期
- 5年定期

#### 贷款利率数据结构

| 字段 | 说明 |
|------|------|
| date | 日期 |
| loan_type | 贷款类型 |
| rate | 利率 |

**贷款类型示例**：
- 6个月以内(含6个月)
- 6个月至1年(含1年)
- 1年至3年(含3年)
- 3年至5年(含5年)
- 5年以上

#### 存款准备金率数据结构

| 字段 | 说明 |
|------|------|
| date | 日期 |
| reserve_ratio | 大型金融机构存款准备金率 |
| small_reserve_ratio | 中小型金融机构存款准备金率 |

#### 货币供应量数据结构

| 字段 | 说明 |
|------|------|
| date | 日期 |
| monthM0 | 流通中货币(M0) |
| monthM0Y | M0同比增长 |
| monthM1 | 狭义货币(M1) |
| monthM1Y | M1同比增长 |
| monthM2 | 广义货币(M2) |
| monthM2Y | M2同比增长 |

## 环境要求

### 安装

```bash
pip install baostock
```

或使用国内镜像（推荐）：

```bash
pip install baostock -i https://pypi.tuna.tsinghua.edu.cn/simple --trusted-host pypi.tuna.tsinghua.edu.cn
```

### 验证安装

```python
python -c "import baostock as bs; bs.login()"
```

输出 `login success!` 表示安装成功。

### 依赖

- Python 3.6+
- pandas
- numpy（可选，用于数据分析）

## 快速开始

### 基础使用流程

```python
import baostock as bs
import pandas as pd

# 1. 登录系统
bs.login()

# 2. 执行查询
rs = bs.query_history_k_data_plus(
    "sh.600000",  # 股票代码
    "date,code,open,high,low,close,volume,amount",  # 字段
    start_date='2020-01-01',  # 开始日期
    end_date='2024-12-31',  # 结束日期
    frequency="d",  # 日K线
    adjustflag="2"  # 前复权
)

# 3. 转换为DataFrame
data_list = []
while (rs.error_code == '0') & rs.next():
    data_list.append(rs.get_row_data())
df = pd.DataFrame(data_list, columns=rs.fields)

# 4. 数据处理
print(df.head())
print(df.dtypes)

# 5. 登出系统
bs.logout()
```

### 基本查询示例

#### 1. 日K线数据（后复权）

```python
rs = bs.query_history_k_data_plus(
    "sz.000002",  # 万科A
    "date,code,open,high,low,close,volume,amount,turn,pctChg",
    start_date="2010-01-01",
    end_date="2024-08-20",
    frequency="d",
    adjustflag="1"  # 后复权
)
df = rs.get_data()
```

#### 2. 5分钟K线数据

```python
rs = bs.query_history_k_data_plus(
    "sh.600036",  # 招商银行
    "date,time,open,high,low,close,volume",
    start_date="2024-08-01",
    end_date="2024-08-20",
    frequency="5"  # 5分钟
)
df = rs.get_data()
```

#### 3. 获取全市场股票列表

```python
rs = bs.query_all_stock(day="2024-08-20")
df = rs.get_data()
print(df.head(10))
```

#### 4. 财务数据查询

```python
# 利润表
rs = bs.query_profit_data(code="sh.600000", year=2023, quarter=4)
profit_df = rs.get_data()

# 资产负债表
rs = bs.query_balance_data(code="sh.600000", year=2023, quarter=4)
balance_df = rs.get_data()

# 现金流量表
rs = bs.query_cash_flow_data(code="sh.600000", year=2023, quarter=4)
cashflow_df = rs.get_data()
```

## 股票代码格式

| 市场 | 格式 | 示例 |
|------|------|------|
| 上海主板 | `sh.6位数字` | `sh.600000`（浦发银行） |
| 上海科创板 | `sh.688开头` | `sh.688981`（中芯国际） |
| 深圳主板 | `sz.0或3开头` | `sz.000001`（平安银行） |
| 深圳创业板 | `sz.3开头` | `sz.300750`（宁德时代） |
| 北交所 | `bj.8或4开头` | `bj.430047` |

### 常用股票代码

```python
# 指数
"sh.000001"  # 上证指数
"sz.399001"  # 深证成指
"sh.000300"  # 沪深300
"sz.399006"  # 创业板指

# 银行股
"sh.601398"  # 工商银行
"sh.600000"  # 浦发银行
"sz.000001"  # 平安银行
"sh.600036"  # 招商银行

# 白酒龙头
"sh.600519"  # 贵州茅台
"sz.000858"  # 五粮液

# 科技龙头
"sz.300750"  # 宁德时代
"sh.688981"  # 中芯国际
```

## 字段说明

### K线数据字段

| 字段名 | 说明 | 示例 |
|-------|------|------|
| date | 交易日期 | 2024-08-20 |
| code | 股票代码 | sh.600000 |
| open | 开盘价 | 10.25 |
| high | 最高价 | 10.45 |
| low | 最低价 | 10.20 |
| close | 收盘价 | 10.38 |
| preclose | 前收盘价 | 10.15 |
| volume | 成交量（手） | 1250000 |
| amount | 成交额（元） | 12950000.00 |
| adjustflag | 复权标志 | 1 |
| turn | 换手率 | 0.52 |
| tradestatus | 交易状态 | 1 |
| pctChg | 涨跌幅 | 2.27 |
| peTTM | 滚动市盈率 | 5.23 |
| pbMRQ | 市净率 | 0.58 |
| psTTM | 滚动市销率 | 1.85 |
| pcfNcfTTM | 滚动市现率 | - |
| isST | 是否ST | 0 |

### 财务数据字段

| 字段名 | 说明 | 示例 |
|-------|------|------|
| code | 股票代码 | sh.600000 |
| pubDate | 发布日期 | 2024-08-20 |
| statDate | 统计日期 | 2024-06-30 |
| (其他) | 各财务指标 | 具体值 |

## API 参考

### 1. 系统登录登出

#### bs.login()

登录系统，建立与服务器的连接。

```python
lg = bs.login()
print('login respond error_code:', lg.error_code)
print('login respond error_msg:', lg.error_msg)
```

#### bs.logout()

登出系统，断开与服务器的连接。

```python
bs.logout()
```

**注意**：登录后超过一段时间没有操作会超时，需要重新登录。

### 2. 历史行情数据

#### bs.query_history_k_data_plus()

获取A股历史交易数据。

**参数**：

| 参数名 | 类型 | 必填 | 默认值 | 说明 |
|-------|------|------|--------|------|
| code | str | 是 | - | 股票代码，如 `sh.600000` |
| fields | str | 是 | - | 返回字段，多字段用逗号分隔 |
| start_date | str | 否 | 2015-01-01 | 开始日期，格式 YYYY-MM-DD |
| end_date | str | 否 | 最近交易日 | 结束日期，格式 YYYY-MM-DD |
| frequency | str | 否 | d | 数据频率：d=日，w=周，m=月，5/15/30/60=分钟 |
| adjustflag | str | 否 | 3 | 复权类型：1=后复权，2=前复权，3=不复权 |

**示例**：

```python
rs = bs.query_history_k_data_plus(
    code="sh.600000",
    fields="date,code,open,high,low,close,volume,amount",
    start_date="2023-01-01",
    end_date="2023-12-31",
    frequency="d",
    adjustflag="2"
)
```

### 3. 股票列表查询

#### bs.query_all_stock()

获取指定日期所有股票列表。

**参数**：

| 参数名 | 类型 | 必填 | 默认值 | 说明 |
|-------|------|------|--------|------|
| day | str | 否 | 当天 | 查询日期，格式 YYYY-MM-DD |

**示例**：

```python
rs = bs.query_all_stock(day="2024-08-20")
df = rs.get_data()
```

### 4. 财务数据查询

#### bs.query_profit_data()

获取利润表数据。

```python
rs = bs.query_profit_data(code="sh.600000", year=2023, quarter=4)
```

#### bs.query_balance_data()

获取资产负债表数据。

```python
rs = bs.query_balance_data(code="sh.600000", year=2023, quarter=4)
```

#### bs.query_cash_flow_data()

获取现金流量表数据。

```python
rs = bs.query_cash_flow_data(code="sh.600000", year=2023, quarter=4)
```

### 5. 除权除息数据

#### bs.query_dividend_data()

获取除权除息信息。

```python
rs = bs.query_dividend_data(code="sh.600000", year="2023")
df = rs.get_data()
```

### 6. 复权因子

#### bs.query_adjust_factor()

获取复权因子信息。

```python
rs = bs.query_adjust_factor(code="sh.600000", start_date="2023-01-01", end_date="2023-12-31")
df = rs.get_data()
```

### 7. 指数数据

#### bs.query_index_cycle_data()

获取指数成分股及行业权重数据。

```python
rs = bs.query_index_cycle_data(code="sh.000300")
df = rs.get_data()
```

## 数据质量保证

### 数据更新时效

| 数据类型 | 更新时间 | 说明 |
|---------|---------|------|
| **日K线** | 交易日17:30 | T日收盘后更新 |
| **分钟K线** | 交易日20:30 | T日盘后更新 |
| **财务数据** | 第二自然日1:30 | T-1日数据入库 |

### 数据完整性

- ✅ 所有历史K线数据完整，无缺失
- ✅ 复权数据计算准确
- ✅ 财务报表经过审计验证
- ✅ 指数成分股定期更新

## 最佳实践

### 1. 数据获取优化

✅ **推荐做法**：

```python
# 批量获取多只股票
stocks = ['sh.600000', 'sh.600036', 'sz.000001']

for code in stocks:
    rs = bs.query_history_k_data_plus(
        code,
        fields="date,code,open,high,low,close,volume,amount",
        start_date="2020-01-01",
        end_date="2024-12-31",
        frequency="d",
        adjustflag="2"
    )
    
    data_list = []
    while (rs.error_code == '0') & rs.next():
        data_list.append(rs.get_row_data())
    
    df = pd.DataFrame(data_list, columns=rs.fields)
    df.to_csv(f"{code.replace('.', '_')}_daily.csv", index=False)
```

❌ **不推荐**：

```python
# 单次请求数据量过大
rs = bs.query_history_k_data_plus(
    "sh.600000",
    "*",  # 获取所有字段
    start_date="1990-01-01",
    end_date="2024-12-31",
    frequency="5"  # 分钟线，30多年的数据量巨大
)
```

### 2. 错误处理

```python
import baostock as bs
import pandas as pd

def get_stock_data(code, start_date, end_date):
    """获取股票数据，带错误处理"""
    
    try:
        # 登录
        lg = bs.login()
        if lg.error_code != '0':
            print(f"登录失败: {lg.error_msg}")
            return None
        
        # 查询数据
        rs = bs.query_history_k_data_plus(
            code=code,
            fields="date,code,open,high,low,close,volume,amount",
            start_date=start_date,
            end_date=end_date,
            frequency="d",
            adjustflag="2"
        )
        
        # 检查查询结果
        if rs.error_code != '0':
            print(f"查询失败: {rs.error_msg}")
            return None
        
        # 转换数据
        data_list = []
        while rs.next():
            data_list.append(rs.get_row_data())
        
        df = pd.DataFrame(data_list, columns=rs.fields)
        
        # 数据类型转换
        for col in ['open', 'high', 'low', 'close', 'volume', 'amount']:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce')
        
        return df
        
    except Exception as e:
        print(f"数据获取异常: {str(e)}")
        return None
    
    finally:
        # 确保登出
        bs.logout()
```

### 3. 性能优化

```python
# 使用批量查询
import baostock as bs

bs.login()

# 获取股票列表
rs = bs.query_all_stock(day="2024-08-20")
stock_df = rs.get_data()

# 筛选上海股票
sh_stocks = stock_df[stock_df['code'].str.startswith('sh.')]

# 批量获取数据
for code in sh_stocks['code'].head(10):  # 示例：取前10只
    rs = bs.query_history_k_data_plus(
        code,
        fields="date,code,open,high,low,close",
        start_date="2024-01-01",
        end_date="2024-08-20",
        frequency="d"
    )
    df = rs.get_data()
    # 处理数据...

bs.logout()
```

## 常见问题

### Q: 数据获取失败怎么办？

**A**: 检查以下几点：

1. 网络连接是否正常
2. 是否正确登录（调用 `bs.login()`）
3. 股票代码格式是否正确
4. 日期格式是否为 `YYYY-MM-DD`
5. 是否超时（需要重新登录）

### Q: 如何处理返回的空数据？

**A**:

```python
rs = bs.query_history_k_data_plus(...)
df = rs.get_data()

if df.empty:
    print("未获取到数据，可能原因：")
    print("1. 日期为非交易日")
    print("2. 股票代码不存在")
    print("3. 日期范围错误")
else:
    print(f"成功获取 {len(df)} 条数据")
```

### Q: 分钟线数据如何获取？

**A**:

```python
# 获取5分钟线
rs = bs.query_history_k_data_plus(
    "sh.600000",
    "date,time,open,high,low,close,volume",
    start_date="2024-08-20",
    end_date="2024-08-20",
    frequency="5"  # 5分钟
)
df = rs.get_data()
```

**注意**：指数没有分钟线数据。

### Q: 如何获取财务数据？

**A**:

```python
# 利润表（最新季度）
rs = bs.query_profit_data(code="sh.600000", year=2023, quarter=4)
profit_df = rs.get_data()

# 多个季度的数据需要循环
for year in [2022, 2023]:
    for quarter in [1, 2, 3, 4]:
        rs = bs.query_profit_data(code="sh.600000", year=year, quarter=quarter)
        df = rs.get_data()
        if not df.empty:
            # 处理数据...
            pass
```

### Q: 复权数据如何选择？

**A**:

| 复权类型 | 参数值 | 适用场景 |
|---------|-------|---------|
| **后复权** | `1` | 技术分析、量化策略 |
| **前复权** | `2` | 视觉图表、成本分析（推荐） |
| **不复权** | `3` | 实际价格计算、分红除权分析 |

### Q: 与其他数据源比较？

**A**:

| 特性 | Baostock | Tushare | Westockdata |
|------|---------|---------|-------------|
| **数据范围** | 仅A股 | A股+港股+美股 | A股+港股+美股 |
| **历史深度** | 1990年至今 ⭐ | 较短 | 较短 |
| **实时性** | 无 ⭐ | 部分实时 | 实时行情 ⭐ |
| **请求限制** | 无 ⭐ | 积分限制 | 无 ⭐ |
| **注册要求** | 无 ⭐ | 需要Token | 无 ⭐ |
| **财务数据** | 完整 ⭐ | 完整 ⭐ | 有限 |
| **使用场景** | 量化回测 | 综合分析 | 实时监控 |

**推荐组合**：
- **量化回测**：Baostock（免费、无限制、历史长）
- **实时监控**：Westockdata（实时行情）
- **综合分析**：组合使用多个数据源

## 局限性

⚠️ **使用限制**：

1. **仅支持A股**：不支持港股、美股、期货等
2. **无实时数据**：只能获取历史数据，不支持实时行情
3. **登录超时**：长时间无操作需要重新登录
4. **单次查询限制**：单次查询数据量不宜过大
5. **分钟数据量大**：分钟线数据量巨大，需控制时间范围

## 扩展使用

### 与其他库配合

#### Pandas Data Analysis

```python
import baostock as bs
import pandas as pd
import numpy as np

bs.login()

# 获取数据
rs = bs.query_history_k_data_plus(
    "sh.600000",
    "date,code,open,high,low,close,volume,pctChg",
    start_date="2020-01-01",
    end_date="2024-12-31"
)

data_list = []
while (rs.error_code == '0') & rs.next():
    data_list.append(rs.get_row_data())

df = pd.DataFrame(data_list, columns=rs.fields)

# 数据类型转换
numeric_cols = ['open', 'high', 'low', 'close', 'volume', 'pctChg']
for col in numeric_cols:
    df[col] = pd.to_numeric(df[col], errors='coerce')

# 分析
print(df.describe())
print(f"平均收益率: {df['pctChg'].mean():.2f}%")
print(f"最大日涨幅: {df['pctChg'].max():.2f}%")
print(f"最大日跌幅: {df['pctChg'].min():.2f}%")

bs.logout()
```

#### Matplotlib 可视化

```python
import matplotlib.pyplot as plt

plt.figure(figsize=(12, 6))
plt.plot(pd.to_datetime(df['date']), df['close'])
plt.title('浦发银行股价走势')
plt.xlabel('日期')
plt.ylabel('价格')
plt.grid(True)
plt.show()
```

### 量化策略开发

```python
# 示例：简单均线策略
import baostock as bs
import pandas as pd

def moving_average_strategy(code, short_window=5, long_window=20):
    """均线策略"""
    
    bs.login()
    
    # 获取数据
    rs = bs.query_history_k_data_plus(
        code,
        "date,code,close",
        start_date="2022-01-01",
        end_date="2024-12-31",
        frequency="d"
    )
    
    data_list = []
    while (rs.error_code == '0') & rs.next():
        data_list.append(rs.get_row_data())
    
    df = pd.DataFrame(data_list, columns=rs.fields)
    df['close'] = pd.to_numeric(df['close'], errors='coerce')
    df['MA5'] = df['close'].rolling(window=short_window).mean()
    df['MA20'] = df['close'].rolling(window=long_window).mean()
    
    bs.logout()
    
    return df

# 使用策略
df = moving_average_strategy("sh.600000")
print(df.tail(10))
```

## 版本信息

- **当前版本**: 1.0.0
- **官方网站**: http://baostock.com
- **官方文档**: http://baostock.com/baostock/index.php/Python_API%E6%96%87%E6%A1%A3
- **官方QQ群**: 974440047
- **联系邮箱**: baostock@163.com

## 免责声明

⚠️ **重要提示**：

- 本技能提供的数据仅供参考
- 数据可能有延迟，请以交易所官方数据为准
- 投资有风险，决策需谨慎
- 不构成任何投资建议

## 更新日志

### v1.0.0 (2026-05-06)

- 初始版本
- 支持日、周、月K线数据
- 支持5/15/30/60分钟线数据
- 支持财务数据查询
- 支持指数数据查询
- 支持复权数据
- 完整的API参考文档
