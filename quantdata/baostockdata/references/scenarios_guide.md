# 分析场景指南

## 场景一：量化回测数据准备

### 场景描述
为量化策略回测准备历史行情数据，需要获取多只股票的长周期数据。

### 分析目标
- 获取多只股票的历史日线数据
- 包含前复权价格用于技术分析
- 数据完整性验证
- 统一的数据格式

### 分析流程

#### Step 1: 确定回测标的和时间范围
```python
# 确定股票池
stock_pool = [
    'sh.600000',  # 浦发银行
    'sh.600036',  # 招商银行
    'sh.601398',  # 工商银行
    'sz.000001',  # 平安银行
    'sz.000002',  # 万科A
]

# 确定回测时间
start_date = "2015-01-01"
end_date = "2024-12-31"
```

#### Step 2: 批量获取数据
```python
import baostock as bs
import pandas as pd

bs.login()

all_data = []

for code in stock_pool:
    print(f"正在获取: {code}")
    
    rs = bs.query_history_k_data_plus(
        code=code,
        fields="date,code,open,high,low,close,volume,amount,pctChg",
        start_date=start_date,
        end_date=end_date,
        frequency="d",
        adjustflag="2"  # 前复权
    )
    
    data_list = []
    while (rs.error_code == '0') & rs.next():
        data_list.append(rs.get_row_data())
    
    if data_list:
        df = pd.DataFrame(data_list, columns=rs.fields)
        all_data.append(df)
        print(f"  成功获取 {len(df)} 条数据")
    else:
        print(f"  获取失败")

bs.logout()

# 合并数据
df_all = pd.concat(all_data, ignore_index=True)

# 类型转换
numeric_cols = ['open', 'high', 'low', 'close', 'volume', 'amount', 'pctChg']
for col in numeric_cols:
    df_all[col] = pd.to_numeric(df_all[col], errors='coerce')

df_all['date'] = pd.to_datetime(df_all['date'])
```

#### Step 3: 数据验证
```python
# 检查数据完整性
for code in stock_pool:
    df_stock = df_all[df_all['code'] == code]
    date_range = f"{df_stock['date'].min()} 至 {df_stock['date'].max()}"
    print(f"{code}: {len(df_stock)} 条数据, {date_range}")
```

### 输出示例

```
=== 量化回测数据准备报告 ===

股票池：5 只股票
时间范围：2015-01-01 至 2024-12-31
数据总量：12,500 条

数据完整性检查：
  sh.600000 (浦发银行): 2435 条数据 ✓
  sh.600036 (招商银行): 2435 条数据 ✓
  sh.601398 (工商银行): 2435 条数据 ✓
  sz.000001 (平安银行): 2435 条数据 ✓
  sz.000002 (万科A): 2435 条数据 ✓

复权方式：前复权
数据质量：通过 ✓
```

---

## 场景二：技术指标计算

### 场景描述
计算股票的技术指标，包括均线、MACD、RSI等，用于技术分析。

### 分析目标
- 计算多种技术指标
- 识别买卖信号
- 可视化技术分析结果

### 分析流程

#### Step 1: 获取数据
```python
import baostock as bs
import pandas as pd
import numpy as np

bs.login()

rs = bs.query_history_k_data_plus(
    "sh.600519",  # 贵州茅台
    "date,code,open,high,low,close,volume",
    start_date="2023-01-01",
    end_date="2024-12-31",
    frequency="d",
    adjustflag="2"
)

data_list = []
while (rs.error_code == '0') & rs.next():
    data_list.append(rs.get_row_data())

df = pd.DataFrame(data_list, columns=rs.fields)

numeric_cols = ['open', 'high', 'low', 'close', 'volume']
for col in numeric_cols:
    df[col] = pd.to_numeric(df[col], errors='coerce')

df['date'] = pd.to_datetime(df['date'])
df = df.sort_values('date').reset_index(drop=True)

bs.logout()
```

#### Step 2: 计算均线
```python
# 简单移动平均线
for window in [5, 10, 20, 60]:
    df[f'MA{window}'] = df['close'].rolling(window=window).mean()

# 指数移动平均线
for window in [12, 26]:
    df[f'EMA{window}'] = df['close'].ewm(span=window, adjust=False).mean()
```

#### Step 3: 计算MACD
```python
# MACD指标
df['EMA12'] = df['close'].ewm(span=12, adjust=False).mean()
df['EMA26'] = df['close'].ewm(span=26, adjust=False).mean()
df['DIF'] = df['EMA12'] - df['EMA26']
df['DEA'] = df['DIF'].ewm(span=9, adjust=False).mean()
df['MACD'] = (df['DIF'] - df['DEA']) * 2

# MACD柱状图颜色
df['MACD_color'] = np.where(df['MACD'] >= 0, 'red', 'green')
```

#### Step 4: 计算RSI
```python
# RSI指标
for period in [6, 12, 24]:
    delta = df['close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
    rs = gain / loss
    df[f'RSI{period}'] = 100 - (100 / (1 + rs))
```

#### Step 5: 计算KDJ
```python
# KDJ指标
n = 9
low_list = df['low'].rolling(window=n, min_periods=1).min()
high_list = df['high'].rolling(window=n, min_periods=1).max()

rsv = (df['close'] - low_list) / (high_list - low_list) * 100
df['K'] = rsv.ewm(com=2, adjust=False).mean()
df['D'] = df['K'].ewm(com=2, adjust=False).mean()
df['J'] = 3 * df['K'] - 2 * df['D']
```

### 输出示例

```
=== 技术指标分析报告 ===

股票：贵州茅台 (sh.600519)
分析期间：2023-01-03 至 2024-12-31
最新价格：¥1,847.23

一、均线系统
  MA5:  ¥1,823.45 (价格上方)
  MA10: ¥1,812.67 (价格上方)
  MA20: ¥1,798.23 (价格上方)
  MA60: ¥1,756.89 (价格上方)
  判断：多头排列，上升趋势 ✓

二、MACD指标
  DIF:  28.56
  DEA:  25.34
  MACD: 6.44 (红柱)
  判断：金叉后持续在零轴上方，强势 ✓

三、RSI指标
  RSI6:  68.5 (偏强区域)
  RSI12: 65.3
  RSI24: 62.8
  判断：处于强势但未超买

四、KDJ指标
  K: 72.3
  D: 68.5
  J: 79.9
  判断：金叉状态

五、综合结论
  趋势：上升趋势（均线多头排列）
  动量：强势（MACD零轴上方）
  动能：偏强（RSI在60-70区间）
  建议：持有，回调至MA20可考虑加仓
```

---

## 场景三：财务报表分析

### 场景描述
分析上市公司的财务状况，包括盈利能力、偿债能力、运营能力等。

### 分析目标
- 获取多年季度财务数据
- 分析财务指标趋势
- 评估公司基本面

### 分析流程

#### Step 1: 获取财务数据
```python
import baostock as bs
import pandas as pd

bs.login()

# 利润表数据
rs_profit = bs.query_profit_data(
    code="sh.600519",
    year=2023,
    quarter=4
)

profit_data = []
while (rs_profit.error_code == '0') & rs_profit.next():
    profit_data.append(rs_profit.get_row_data())

df_profit = pd.DataFrame(profit_data, columns=rs_profit.fields)

# 资产负债表
rs_balance = bs.query_balance_data(
    code="sh.600519",
    year=2023,
    quarter=4
)

balance_data = []
while (rs_balance.error_code == '0') & rs_balance.next():
    balance_data.append(rs_balance.get_row_data())

df_balance = pd.DataFrame(balance_data, columns=rs_balance.fields)

# 现金流量表
rs_cashflow = bs.query_cash_flow_data(
    code="sh.600519",
    year=2023,
    quarter=4
)

cashflow_data = []
while (rs_cashflow.error_code == '0') & rs_cashflow.next():
    cashflow_data.append(rs_cashflow.get_row_data())

df_cashflow = pd.DataFrame(cashflow_data, columns=rs_cashflow.fields)

bs.logout()
```

#### Step 2: 多季度数据汇总
```python
# 获取近8个季度的数据
all_profit = []

for year in [2022, 2023]:
    for quarter in [1, 2, 3, 4]:
        rs = bs.query_profit_data(
            code="sh.600519",
            year=year,
            quarter=quarter
        )
        
        data = []
        while (rs.error_code == '0') & rs.next():
            data.append(rs.get_row_data())
        
        if data:
            df_q = pd.DataFrame(data, columns=rs.fields)
            df_q['year'] = year
            df_q['quarter'] = quarter
            all_profit.append(df_q)

df_profit_all = pd.concat(all_profit, ignore_index=True)
df_profit_all = df_profit_all.sort_values(['year', 'quarter'])
```

### 输出示例

```
=== 财务分析报告 ===

公司：贵州茅台 (sh.600519)
分析期间：2022Q1 - 2023Q4

一、盈利能力分析

| 指标 | 2022Q4 | 2023Q1 | 2023Q2 | 2023Q3 | 2023Q4 |
|------|--------|--------|--------|--------|--------|
| 营业收入(亿) | 369.5 | 391.2 | 415.8 | 445.2 | 469.3 |
| 净利润(亿) | 183.2 | 195.6 | 208.9 | 223.5 | 235.6 |
| 毛利率(%) | 91.5 | 92.1 | 92.3 | 92.5 | 92.8 |
| 净利率(%) | 49.6 | 50.0 | 50.2 | 50.2 | 50.2 |

趋势分析：
  营业收入：逐季增长 (+27.0%)
  净利润：同步增长 (+28.6%)
  毛利率：持续提升 (+1.3%)
  净利率：保持稳定 (50%+)

二、偿债能力

| 指标 | 2023Q4 | 行业平均 | 评价 |
|------|--------|---------|------|
| 资产负债率(%) | 18.5 | 35.2 | 优秀 ✓ |
| 流动比率 | 4.2 | 2.1 | 优秀 ✓ |
| 速动比率 | 4.0 | 1.8 | 优秀 ✓ |

三、运营能力

| 指标 | 2023Q4 | 行业平均 | 评价 |
|------|--------|---------|------|
| 存货周转天数 | 1235 | 456 | 较低 |
| 应收账款周转天数 | 8.5 | 45.2 | 优秀 ✓ |

四、杜邦分析

  净资产收益率(ROE): 28.5%
  资产周转率: 0.52
  权益乘数: 1.23
  销售净利率: 50.2%

综合评价：
  盈利能力：⭐⭐⭐⭐⭐ (优秀)
  偿债能力：⭐⭐⭐⭐⭐ (优秀)
  运营能力：⭐⭐⭐⭐ (良好)
  成长性：⭐⭐⭐⭐⭐ (优秀)

投资建议：
  ✓ 茅台财务数据表现优秀
  ✓ 盈利能力强劲且稳定
  ✓ 现金流充裕
  ✓ 资产负债率低
  → 维持"强烈推荐"评级
```

---

## 场景四：市场宽度分析

### 场景描述
分析市场整体涨跌股票数量，计算市场广度指标。

### 分析目标
- 获取某日全市场股票涨跌情况
- 计算上涨/下跌股票比例
- 判断市场整体趋势

### 分析流程

#### Step 1: 获取全市场数据
```python
import baostock as bs
import pandas as pd

bs.login()

# 获取指定日期所有股票
date = "2024-08-20"
rs = bs.query_all_stock(day=date)

stock_list = []
while (rs.error_code == '0') & rs.next():
    stock_list.append(rs.get_row_data())

df_all_stocks = pd.DataFrame(stock_list, columns=rs.fields)

# 筛选A股（排除指数、基金等）
df_stocks = df_all_stocks[
    (df_all_stocks['code'].str.startswith('sh.6')) |
    (df_all_stocks['code'].str.startswith('sz.0')) |
    (df_all_stocks['code'].str.startswith('sz.3')) |
    (df_all_stocks['code'].str.startswith('bj.'))
]

print(f"当日上市A股数量: {len(df_stocks)}")
print(f"正常交易股票数: {len(df_stocks[df_stocks['tradeStatus'] == '1'])}")

bs.logout()
```

#### Step 2: 获取涨跌幅数据
```python
# 批量获取涨跌幅
bs.login()

rising_stocks = []
falling_stocks = []
unchanged_stocks = []

# 获取每只股票当日数据（示例取前100只）
for code in df_stocks['code'].head(100):
    rs = bs.query_history_k_data_plus(
        code=code,
        fields="date,code,close,pctChg",
        start_date=date,
        end_date=date,
        frequency="d"
    )
    
    data_list = []
    while (rs.error_code == '0') & rs.next():
        data_list.append(rs.get_row_data())
    
    if data_list:
        df_stock = pd.DataFrame(data_list, columns=rs.fields)
        pctChg = float(df_stock['pctChg'].iloc[0])
        
        if pctChg > 0:
            rising_stocks.append(code)
        elif pctChg < 0:
            falling_stocks.append(code)
        else:
            unchanged_stocks.append(code)

bs.logout()
```

### 输出示例

```
=== 市场宽度分析报告 ===

分析日期：2024-08-20

一、市场概况
  总股票数: 5,320
  上涨股票: 2,890 (54.3%)
  下跌股票: 2,180 (41.0%)
  平盘股票: 250 (4.7%)

二、涨跌分布
  涨停股票: 89 (1.7%)
  涨幅 >5%: 456 (8.6%)
  涨幅 3-5%: 678 (12.7%)
  涨幅 0-3%: 1,667 (31.3%)
  跌幅 0-3%: 1,234 (23.2%)
  跌幅 3-5%: 567 (10.7%)
  跌幅 5-10%: 345 (6.5%)
  跌停股票: 34 (0.6%)

三、市场广度指标
  广度指标: +13.3% (上涨-下跌比例)
  强势股比例: 22.6% (涨幅>3%)
  弱势股比例: 17.3% (跌幅>3%)

四、分析结论

市场情绪：偏乐观
  - 上涨股票数量超过下跌股票
  - 涨停数量较多，市场活跃
  - 跌幅超过5%的股票较少

趋势判断：
  上涨股票占比 > 60%: 强势市场
  上涨股票占比 40-60%: 中性市场 ← 当前
  上涨股票占比 < 40%: 弱势市场

操作建议：
  ✓ 市场整体偏强，可适当加仓
  ✓ 关注强势板块轮动机会
  ⚠️ 注意获利盘回吐风险
```

---

## 场景五：指数成分股分析

### 场景描述
分析特定指数（如沪深300）的成分股结构，包括行业分布、市值分布等。

### 分析目标
- 获取指数成分股权重
- 分析行业分布
- 识别权重股

### 分析流程

#### Step 1: 获取指数数据
```python
import baostock as bs
import pandas as pd

bs.login()

# 获取指数K线
rs_index = bs.query_history_k_data_plus(
    "sh.000300",  # 沪深300
    "date,code,open,high,low,close,volume,amount",
    start_date="2024-01-01",
    end_date="2024-08-20",
    frequency="d"
)

index_data = []
while (rs_index.error_code == '0') & rs_index.next():
    index_data.append(rs_index.get_row_data())

df_index = pd.DataFrame(index_data, columns=rs_index.fields)

# 获取成分股权重（如果有接口）
rs_constituent = bs.query_index_cycle_data(code="sh.000300")
if rs_constituent.error_code == '0':
    constituent_data = []
    while rs_constituent.next():
        constituent_data.append(rs_constituent.get_row_data())
    
    if constituent_data:
        df_constituent = pd.DataFrame(constituent_data, columns=rs_constituent.fields)
        print(f"沪深300成分股数量: {len(df_constituent)}")

bs.logout()
```

#### Step 2: 批量获取成分股数据
```python
# 获取前20大权重股的数据
top_stocks = df_constituent.head(20)['code'].tolist() if 'df_constituent' in dir() else []

bs.login()

all_weight_data = []

for code in top_stocks:
    rs = bs.query_history_k_data_plus(
        code=code,
        fields="date,code,close,pctChg",
        start_date="2024-08-19",
        end_date="2024-08-20",
        frequency="d"
    )
    
    data_list = []
    while (rs.error_code == '0') & rs.next():
        data_list.append(rs.get_row_data())
    
    if data_list:
        df_stock = pd.DataFrame(data_list, columns=rs.fields)
        all_weight_data.append(df_stock)

bs.logout()

if all_weight_data:
    df_weight_stocks = pd.concat(all_weight_data, ignore_index=True)
```

### 输出示例

```
=== 沪深300指数分析报告 ===

分析日期：2024-08-20

一、指数表现
  指数代码: sh.000300
  收盘点位: 3,456.78
  日涨跌幅: +1.23%
  成交额: 2,890亿元

二、前十大权重股表现

| 排名 | 股票代码 | 股票名称 | 权重(%) | 涨跌幅(%) |
|------|---------|---------|--------|----------|
| 1 | sh.600519 | 贵州茅台 | 5.23 | +1.56 |
| 2 | sh.600036 | 招商银行 | 4.12 | +2.34 |
| 3 | sh.601318 | 中国平安 | 3.89 | +0.87 |
| 4 | sh.600276 | 恒瑞医药 | 3.45 | -0.56 |
| 5 | sh.600900 | 长江电力 | 3.12 | +0.23 |
| 6 | sz.000858 | 五粮液 | 2.98 | +1.89 |
| 7 | sh.601398 | 工商银行 | 2.87 | +0.45 |
| 8 | sh.600028 | 中国石化 | 2.76 | -0.12 |
| 9 | sz.002594 | 比亚迪 | 2.65 | +3.21 |
| 10 | sh.601288 | 农业银行 | 2.54 | +0.34 |

三、行业分布（前五大行业）
  1. 金融业: 32.5%
  2. 消费: 18.7%
  3. 信息技术: 15.3%
  4. 医药: 12.8%
  5. 能源: 8.9%

四、指数分析
  成分股上涨: 189 (63.0%)
  成分股下跌: 98 (32.7%)
  成分股平盘: 13 (4.3%)

五、结论
  ✓ 指数收涨，市场整体偏强
  ✓ 权重股多数上涨
  ✓ 消费、金融板块表现较好
  → 指数有望继续走强
```

---

## 场景六：分红数据查询

### 场景描述
查询股票的分红历史，包括历年分红金额、分红方案等。

### 分析目标
- 获取多年分红历史
- 计算累计分红收益率
- 评估股东回报

### 分析流程

```python
import baostock as bs
import pandas as pd

bs.login()

# 获取近5年分红数据
all_dividends = []

for year in range(2020, 2025):
    rs = bs.query_dividend_data(
        code="sh.600519",  # 贵州茅台
        year=str(year)
    )
    
    data = []
    while (rs.error_code == '0') & rs.next():
        data.append(rs.get_row_data())
    
    if data:
        df_div = pd.DataFrame(data, columns=rs.fields)
        all_dividends.append(df_div)

bs.logout()

if all_dividends:
    df_dividends = pd.concat(all_dividends, ignore_index=True)
    print(df_dividends)
```

### 输出示例

```
=== 分红历史分析报告 ===

股票：贵州茅台 (sh.600519)
分析期间：2020年 - 2024年

一、分红历史

| 分红年度 | 分红方案 | 分红金额(元/股) | 派息日 | 分红收益率 |
|---------|---------|---------------|--------|-----------|
| 2024 | 10派259.71 | 25.971 | 2025-06-15 | 1.45% |
| 2023 | 10派247.58 | 24.758 | 2024-06-18 | 1.52% |
| 2022 | 10派219.86 | 21.986 | 2023-06-20 | 1.38% |
| 2021 | 10派193.72 | 19.372 | 2022-06-20 | 1.25% |
| 2020 | 10派170.25 | 17.025 | 2021-06-22 | 1.15% |

二、分红统计
  连续分红年限: 22年 ✓
  累计分红金额: 109.12元/股
  累计分红收益率: 6.75%
  年均分红增长率: +11.2%
  2024年股息率: 1.45%

三、分红能力评估
  盈利能力: 净利润持续增长 ✓
  分红意愿: 稳定且增长 ✓
  分红比例: 约50%的净利润分红
  现金流: 充裕 ✓

四、投资价值分析
  股价(2024-08-20): ¥1,792.35
  2024年分红: ¥25.971/股
  股息率: 1.45%
  
  对比十年期国债收益率: 2.85%
  评估: 股息率低于无风险收益率
        但股票有资本增值潜力

五、结论
  ✓ 茅台分红连续22年未间断
  ✓ 分红金额稳定增长
  ✓ 股东回报意识强
  ⚠️ 股息率相对较低
  → 适合追求资本增值的投资者
```

---

## 场景七：配对交易策略

### 场景描述
使用两只高度相关的股票进行配对交易，当价差偏离均值时买入一只、卖空另一只。

### 分析目标
- 获取两只相关股票的历史数据
- 计算价差的均值和标准差
- 生成交易信号

### 分析流程

#### Step 1: 获取两只银行股数据
```python
import baostock as bs
import pandas as pd
import numpy as np

bs.login()

# 浦发银行和招商银行
stocks = ['sh.600000', 'sh.600036']

all_data = {}
for code in stocks:
    rs = bs.query_history_k_data_plus(
        code=code,
        fields="date,code,close",
        start_date="2020-01-01",
        end_date="2024-08-20",
        frequency="d",
        adjustflag="2"
    )
    
    data_list = []
    while (rs.error_code == '0') & rs.next():
        data_list.append(rs.get_row_data())
    
    if data_list:
        df = pd.DataFrame(data_list, columns=rs.fields)
        df['close'] = pd.to_numeric(df['close'], errors='coerce')
        df['date'] = pd.to_datetime(df['date'])
        all_data[code] = df.set_index('date')['close']

bs.logout()

# 合并数据
df_pair = pd.DataFrame(all_data)
df_pair.columns = ['PAIFA', 'ZHAOSHANG']
df_pair = df_pair.dropna()
```

#### Step 2: 计算价差
```python
# 计算价格比率（配对交易常用）
df_pair['ratio'] = df_pair['PAIFA'] / df_pair['ZHAOSHANG']

# 计算Z-Score
df_pair['ratio_ma'] = df_pair['ratio'].rolling(window=60).mean()
df_pair['ratio_std'] = df_pair['ratio'].rolling(window=60).std()
df_pair['zscore'] = (df_pair['ratio'] - df_pair['ratio_ma']) / df_pair['ratio_std']

# 生成信号
df_pair['signal'] = 0
df_pair.loc[df_pair['zscore'] > 2, 'signal'] = -1  # 价差过大，卖空PAIFA，买入ZHAOSHANG
df_pair.loc[df_pair['zscore'] < -2, 'signal'] = 1   # 价差过小，买入PAIFA，卖空ZHAOSHANG
df_pair.loc[(df_pair['zscore'] > 0.5) & (df_pair['zscore'] < 2), 'signal'] = 0  # 回归均值，平仓
df_pair.loc[(df_pair['zscore'] < -0.5) & (df_pair['zscore'] > -2), 'signal'] = 0  # 回归均值，平仓
```

### 输出示例

```
=== 配对交易分析报告 ===

配对股票：浦发银行 vs 招商银行
分析期间：2020-01-02 至 2024-08-20
交易信号：基于Z-Score的均值回归策略

一、相关性分析
  Pearson相关系数: 0.8932 ✓
  相关性评估: 高度相关，适合配对交易

二、价差统计
  平均比率: 0.1765
  比率标准差: 0.0123
  当前比率: 0.1892
  当前Z-Score: 1.03

三、交易信号
  上一笔交易日期: 2024-07-15
  上一笔交易类型: 平仓
  当前持仓状态: 空仓
  当前信号: 无信号（Z-Score在±1之间）

四、回测统计（2020-2024）
  总交易次数: 23次
  盈利交易: 17次
  亏损交易: 6次
  胜率: 73.9%
  
  平均盈利: +2.3%
  平均亏损: -1.8%
  盈亏比: 1.28
  
  累计收益率: +28.5%
  年化收益率: +5.7%
  最大回撤: -8.2%

五、策略评估
  ✓ 策略稳定盈利
  ✓ 胜率较高
  ✓ 相关性持续稳定
  ⚠️ 年化收益相对有限
  ⚠️ 最大回撤需要注意

六、结论
  配对策略表现良好
  建议：可作为对冲策略使用
  仓位建议：不超过总仓位的20%
```

---

## 场景八：市场情绪指标

### 场景描述
通过多个维度构建市场情绪指标，包括上涨股票比例、创新高/新低股票数量等。

### 分析目标
- 综合多个市场宽度指标
- 判断市场整体情绪
- 识别极端情绪区间

### 分析流程

```python
import baostock as bs
import pandas as pd
import numpy as np

bs.login()

date = "2024-08-20"

# 获取全市场股票
rs_all = bs.query_all_stock(day=date)
all_stocks = []
while (rs_all.error_code == '0') & rs_all.next():
    all_stocks.append(rs_all.get_row_data())

df_all = pd.DataFrame(all_stocks, columns=rs_all.fields)

# 筛选正常交易的A股
df_stocks = df_all[
    (df_all['code'].str.startswith('sh.6')) |
    (df_all['code'].str.startswith('sz.0')) |
    (df_all['code'].str.startswith('sz.3'))
].copy()

trading_codes = df_stocks['code'].tolist()

# 批量获取近期数据（获取前200只作为示例）
stock_data = {}
for code in trading_codes[:200]:
    rs = bs.query_history_k_data_plus(
        code=code,
        fields="date,code,close",
        start_date="2024-07-01",
        end_date=date,
        frequency="d",
        adjustflag="2"
    )
    
    data_list = []
    while (rs.error_code == '0') & rs.next():
        data_list.append(rs.get_row_data())
    
    if data_list and len(data_list) >= 20:
        df = pd.DataFrame(data_list, columns=rs.fields)
        df['close'] = pd.to_numeric(df['close'], errors='coerce')
        stock_data[code] = df

bs.logout()

# 计算各项指标
high_count = 0
low_count = 0
rising_count = 0
falling_count = 0

for code, df in stock_data.items():
    if len(df) >= 2:
        current_price = df['close'].iloc[-1]
        price_20d_ago = df['close'].iloc[-20] if len(df) >= 20 else df['close'].iloc[0]
        
        # 20日新高/新低（简化版：与20日前相比）
        if current_price > price_20d_ago * 1.05:
            high_count += 1
        elif current_price < price_20d_ago * 0.95:
            low_count += 1
        
        # 涨跌统计
        pct_chg = (current_price - price_20d_ago) / price_20d_ago * 100
        if pct_chg > 0:
            rising_count += 1
        else:
            falling_count += 1

total = len(stock_data)
```

### 输出示例

```
=== 市场情绪分析报告 ===

分析日期：2024-08-20
样本股票数：200只（示例）

一、市场宽度指标

1. 20日涨跌股票分布
  上涨股票: 123只 (61.5%) ✓
  下跌股票: 77只 (38.5%)
  净涨跌幅: +23只

2. 20日新高/新低
  20日新高: 35只 (17.5%) ⚠️ 偏多
  20日新低: 12只 (6.0%)
  新高/新低比: 2.92

3. 创历史新高/新低（需更长时间窗口）
  暂无数据

二、情绪指标

| 指标 | 数值 | 情绪判断 |
|------|------|---------|
| 上涨股票占比 | 61.5% | 偏乐观 |
| 新高/新低比 | 2.92 | 偏乐观 |
| 市场广度 | +23 | 中性偏强 |

三、情绪区间

极端区间阈值：
  极度乐观: 上涨占比 > 80%
  极度悲观: 上涨占比 < 20%
  
当前区间：中性偏乐观 (61.5%)

历史分位数：
  2024年最高: 78.3% (2024-03-15)
  2024年最低: 28.9% (2024-07-15)
  当前所处: 67.5%分位

四、结论

市场情绪状态：
  ✅ 整体偏乐观
  ✅ 多头力量占优
  ⚠️ 但未达到极端乐观区间

操作建议：
  - 短期：可维持偏多策略
  - 中期：注意追高风险
  - 仓位：建议7-8成仓位
  - 对冲：可考虑适度对冲
```

---

## 总结

以上8个场景展示了 Baostock 数据在实际量化分析中的典型应用：

1. **量化回测**：批量获取长周期数据
2. **技术分析**：计算多种技术指标
3. **财务分析**：深度财务数据分析
4. **市场宽度**：市场整体广度分析
5. **指数分析**：成分股结构分析
6. **分红分析**：股东回报评估
7. **配对交易**：均值回归策略
8. **市场情绪**：综合情绪指标

这些场景可以作为量化分析和投资决策的参考模板。
