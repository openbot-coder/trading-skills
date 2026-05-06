# 分析场景指南

## 场景一：美股量化回测

### 场景描述
为美股量化策略回测准备历史行情数据，需要获取多只股票的长周期数据。

### 分析目标
- 获取多只股票的历史日线数据
- 包含前复权价格用于技术分析
- 数据完整性验证
- 统一的数据格式

### 分析流程

#### Step 1: 确定回测标的和时间范围
```python
import yfinance as yf

# 确定股票池（科技巨头）
tech_stocks = [
    "AAPL",    # 苹果
    "MSFT",    # 微软
    "GOOGL",   # 谷歌
    "AMZN",    # 亚马逊
    "META",    # Meta
    "NVDA",    # 英伟达
    "TSLA",    # 特斯拉
]

# 确定回测时间
start_date = "2018-01-01"
end_date = "2024-12-31"
```

#### Step 2: 批量获取数据
```python
import yfinance as yf
import pandas as pd

# 批量下载数据
data = yf.download(
    tech_stocks,
    start=start_date,
    end=end_date,
    threads=True,  # 启用多线程
    progress=True
)

# 提取收盘价
close_prices = data['Close']
print(f"数据范围: {close_prices.index.min()} 至 {close_prices.index.max()}")
print(f"股票数量: {len(tech_stocks)}")
print(f"数据点数: {len(close_prices)}")
```

#### Step 3: 数据验证
```python
# 检查数据完整性
for stock in tech_stocks:
    if stock in close_prices.columns:
        df_stock = close_prices[stock].dropna()
        date_range = f"{df_stock.index.min().date()} 至 {df_stock.index.max().date()}"
        print(f"{stock}: {len(df_stock)} 条数据, {date_range}")
    else:
        print(f"{stock}: 无数据 ✗")
```

### 输出示例

```
=== 美股量化回测数据准备报告 ===

股票池：7 只科技巨头
时间范围：2018-01-02 至 2024-12-31
数据总量：1,765 个交易日

数据完整性检查：
  AAPL:  1,765 条数据 ✓
  MSFT:   1,765 条数据 ✓
  GOOGL:  1,765 条数据 ✓
  AMZN:   1,765 条数据 ✓
  META:   1,765 条数据 ✓
  NVDA:   1,765 条数据 ✓
  TSLA:   1,765 条数据 ✓

复权方式：前复权（自动）
数据质量：通过 ✓
```

---

## 场景二：全球资产配置分析

### 场景描述
构建一个包含股票、债券、黄金、加密货币的多元化投资组合。

### 分析目标
- 获取多类资产的历史数据
- 计算收益率和相关性
- 评估组合风险和收益

### 分析流程

#### Step 1: 确定资产类别
```python
import yfinance as yf
import pandas as pd

# 全球资产配置
assets = {
    'US_Stock': 'SPY',           # 美国标普500 ETF
    'Tech_Stock': 'QQQ',          # 纳斯达克100 ETF
    'Bond': 'TLT',               # 长期国债 ETF
    'Gold': 'GLD',              # 黄金 ETF
    'Bitcoin': 'BTC-USD',        # 比特币
    'China_Stock': 'FXI',        # 中国大盘股 ETF
}

period = "3y"
```

#### Step 2: 获取数据
```python
# 批量下载
data = yf.download(
    list(assets.values()),
    period=period,
    threads=True
)

# 提取收盘价
close_prices = data['Close']
print(f"资产数量: {len(assets)}")
print(f"数据范围: {close_prices.index.min()} 至 {close_prices.index.max()}")
```

#### Step 3: 计算相关性
```python
# 计算收益率
returns = close_prices.pct_change().dropna()

# 相关性矩阵
corr_matrix = returns.corr()
print("\n=== 相关性矩阵 ===")
print(corr_matrix.round(2))

# 可视化
import matplotlib.pyplot as plt
plt.figure(figsize=(10, 8))
plt.imshow(corr_matrix, cmap='RdYlGn', aspect='auto', vmin=-1, vmax=1)
plt.colorbar(label='Correlation')
plt.xticks(range(len(assets)), list(assets.keys()), rotation=45)
plt.yticks(range(len(assets)), list(assets.keys()))
plt.title('Global Asset Correlation Matrix')
plt.tight_layout()
plt.show()
```

### 输出示例

```
=== 全球资产配置分析报告 ===

资产类别：6 种资产
分析期间：2021-01-01 至 2024-12-31
数据频率：日频

一、相关性矩阵

              US_Stock  Tech_Stock  Bond   Gold  Bitcoin  China_Stock
US_Stock         1.00       0.92     0.12   0.08     0.35        0.68
Tech_Stock       0.92       1.00     0.08   0.05     0.38        0.62
Bond             0.12       0.08     1.00   0.15    -0.05        0.10
Gold             0.08       0.05     0.15   1.00     0.25        0.12
Bitcoin          0.35       0.38    -0.05   0.25     1.00        0.32
China_Stock      0.68       0.62     0.10   0.12     0.32        1.00

二、关键发现

最高相关性：
  US_Stock vs Tech_Stock: 0.92 (强正相关)
  
最低相关性：
  Bond vs Bitcoin: -0.05 (几乎无关)
  
分散化效果最佳：
  Bond 与多数资产相关性低 ← 优秀的分散化工具

三、配置建议

保守型：
  60% Bonds + 30% US_Stock + 10% Gold
  
平衡型：
  50% US_Stock + 20% Tech_Stock + 15% Bonds + 10% Gold + 5% Bitcoin
  
进取型：
  40% US_Stock + 25% Tech_Stock + 15% China_Stock + 10% Bitcoin + 10% Gold
```

---

## 场景三：技术指标选股

### 场景描述
使用技术指标筛选美股市场中的强势股票。

### 分析目标
- 获取候选股票的技术指标
- 识别技术面良好的股票
- 生成买卖信号

### 分析流程

#### Step 1: 获取候选股票
```python
import yfinance as yf
import pandas as pd

# 科技股候选池
candidates = ["AAPL", "MSFT", "GOOGL", "AMZN", "META", "NVDA", "TSLA", "AMD", "INTC", "NFLX"]

# 获取数据
data = yf.download(candidates, period="3mo", threads=True)
close = data['Close']
```

#### Step 2: 计算技术指标
```python
def calculate_technical_indicators(df):
    """计算技术指标"""
    
    indicators = {}
    
    for stock in df.columns:
        stock_data = df[stock].dropna()
        
        if len(stock_data) < 20:
            continue
        
        # 均线
        ma5 = stock_data.rolling(window=5).mean().iloc[-1]
        ma20 = stock_data.rolling(window=20).mean().iloc[-1]
        ma50 = stock_data.rolling(window=50).mean().iloc[-1]
        
        # RSI
        delta = stock_data.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs)).iloc[-1]
        
        # MACD
        ema12 = stock_data.ewm(span=12).mean().iloc[-1]
        ema26 = stock_data.ewm(span=26).mean().iloc[-1]
        macd = ema12 - ema26
        
        # 动量
        momentum_20 = (stock_data.iloc[-1] / stock_data.iloc[-20] - 1) * 100
        
        current_price = stock_data.iloc[-1]
        
        indicators[stock] = {
            'price': current_price,
            'ma5': ma5,
            'ma20': ma20,
            'ma50': ma50,
            'rsi': rsi,
            'macd': macd,
            'momentum_20': momentum_20,
            'signal': 'BUY' if (ma5 > ma20 and rsi < 70 and momentum_20 > 0) else 'HOLD'
        }
    
    return indicators

# 计算指标
indicators = calculate_technical_indicators(close)
```

#### Step 3: 筛选股票
```python
# 创建结果 DataFrame
results = pd.DataFrame(indicators).T

# 筛选买入信号
buy_signals = results[results['signal'] == 'BUY'].sort_values('momentum_20', ascending=False)

print("\n=== 技术指标选股结果 ===")
print(f"候选股票数: {len(candidates)}")
print(f"买入信号: {len(buy_signals)}")
print(f"\n买入信号股票:")
print(buy_signals[['price', 'ma5', 'ma20', 'rsi', 'momentum_20']].round(2))
```

### 输出示例

```
=== 技术指标选股结果 ===

候选股票数: 10
买入信号: 4

买入信号股票：

       price      ma5      ma20    rsi  momentum_20
NVDA  875.32    860.45   820.23  62.5    18.45  ⭐⭐⭐
META  502.18    495.23   480.56  58.3    12.34  ⭐⭐
MSFT  378.45    372.89   365.12  55.2     8.76  ⭐
AAPL  185.92    183.45   180.23  52.3     5.23  ⭐

筛选条件：
  ✓ 收盘价 > MA5 > MA20（上升趋势）
  ✓ RSI < 70（未超买）
  ✓ 20日动量 > 0（近期上涨）

建议重点关注：
  1. NVDA - 强势股，20日涨幅18.45%
  2. META - 稳健上涨，12.34%
  3. MSFT - 温和上涨，8.76%
```

---

## 场景四：期权策略分析

### 场景描述
分析股票期权数据，为期权交易提供参考。

### 分析目标
- 获取期权链数据
- 分析隐含波动率
- 评估期权价值

### 分析流程

#### Step 1: 获取期权数据
```python
import yfinance as yf

# 创建 Ticker 对象
ticker = yf.Ticker("AAPL")

# 获取期权到期日
expiration_dates = ticker.options
print(f"可用的期权到期日: {len(expiration_dates)} 个")
print(f"最近几个到期日: {expiration_dates[:5]}")

# 获取期权链
expiration = expiration_dates[0]  # 最近一个到期日
opt = ticker.option_chain(expiration)
```

#### Step 2: 分析期权链
```python
# 看涨期权 (Calls)
calls = opt.calls
print("\n=== 看涨期权 (Top 10) ===")
print(cocks[['strike', 'lastPrice', 'bid', 'ask', 'volume', 'impliedVolatility']].head(10))

# 看跌期权 (Puts)
puts = opt.puts
print("\n=== 看跌期权 (Top 10) ===")
print(puts[['strike', 'lastPrice', 'bid', 'ask', 'volume', 'impliedVolatility']].head(10))
```

#### Step 3: 计算期权指标
```python
# 获取当前股价
info = ticker.info
current_price = info['currentPrice']

# 计算 ITM/OTM 期权
calls['moneyness'] = calls['strike'].apply(
    lambda x: 'ITM' if x < current_price else 'OTM'
)

puts['moneyness'] = puts['strike'].apply(
    lambda x: 'ITM' if x > current_price else 'OTM'
)

print(f"\n当前股价: ${current_price:.2f}")
print(f"\n看涨期权 ITM/OTM 分布:")
print(calls['moneyness'].value_counts())
print(f"\n看跌期权 ITM/OTM 分布:")
print(puts['moneyness'].value_counts())
```

### 输出示例

```
=== 期权策略分析报告 ===

标的股票: Apple Inc. (AAPL)
当前股价: $185.92
期权到期日: 2024-12-20

一、隐含波动率分析

看涨期权 (Calls):
  平均 IV: 28.5%
  IV范围: 18.2% - 45.6%
  高IV区域: Strike > $200 (IV > 35%)

看跌期权 (Puts):
  平均 IV: 29.2%
  IV范围: 19.5% - 48.3%
  高IV区域: Strike < $170 (IV > 40%)

二、资金流向

看涨期权成交量 Top 3:
  Strike $190: 12,345 手, IV 32.5%
  Strike $195: 8,234 手, IV 35.2%
  Strike $185: 6,789 手, IV 28.9%

看跌期权成交量 Top 3:
  Strike $175: 9,876 手, IV 31.2%
  Strike $180: 7,654 手, IV 29.8%
  Strike $170: 5,432 手, IV 38.5%

三、策略建议

基于当前 IV 结构:
  1. 卖出备兑看涨 (Covered Call):
     - 卖出 $195 Strike Call
     - 权利金约 $3.45
     - 年化收益率约 18.6%
  
  2. 保护性看跌 (Protective Put):
     - 买入 $175 Strike Put
     - 权利金约 $2.15
     - 对冲下行风险

  3. 铁秃鹰 (Iron Condor):
     - 卖出 $190 Call + $175 Put
     - 买入 $200 Call + $165 Put
     - 预期收益约 $1.80
     - 最大损失约 $3.20
```

---

## 场景五：财报分析

### 场景描述
分析公司财务数据，评估基本面。

### 分析目标
- 获取多年财务报表
- 计算关键财务指标
- 评估公司盈利能力

### 分析流程

#### Step 1: 获取财务数据
```python
import yfinance as yf

ticker = yf.Ticker("AAPL")

# 获取财务报表
income = ticker.income_stmt
balance = ticker.balance_sheet
cashflow = ticker.cashflow

print("=== 财务报表概览 ===")
print(f"利润表: {income.shape[1]} 期数据")
print(f"资产负债表: {balance.shape[1]} 期数据")
print(f"现金流量表: {cashflow.shape[1]} 期数据")
```

#### Step 2: 计算关键指标
```python
# 获取基本信息
info = ticker.info

# 计算关键指标
print("\n=== 关键财务指标 ===")

# 盈利能力
print(f"\n盈利能力:")
if 'GrossMargins' in info:
    print(f"  毛利率: {info['GrossMargins']*100:.1f}%")
if 'ProfitMargins' in info:
    print(f"  净利率: {info['ProfitMargins']*100:.1f}%")
if 'OperatingMargins' in info:
    print(f"  运营利润率: {info['OperatingMargins']*100:.1f}%")

# 估值
print(f"\n估值指标:")
if 'TrailingPE' in info:
    print(f"  市盈率(PE): {info['TrailingPE']:.2f}")
if 'ForwardPE' in info:
    print(f"  预期市盈率: {info['ForwardPE']:.2f}")
if 'PriceToBook' in info:
    print(f"  市净率(PB): {info['PriceToBook']:.2f}")

# 成长性
print(f"\n成长性:")
if 'RevenueGrowth' in info:
    print(f"  营收增长率: {info['RevenueGrowth']*100:.1f}%")
if 'EarningsGrowth' in info:
    print(f"  盈利增长率: {info['EarningsGrowth']*100:.1f}%")
if 'RevenuePerShare' in info:
    print(f"  每股营收: ${info['RevenuePerShare']:.2f}")
```

#### Step 3: 趋势分析
```python
# 营收趋势
if 'Total Revenue' in income.index:
    revenues = income.loc['Total Revenue'].head(4)
    print("\n=== 营收趋势 ===")
    for year, revenue in revenues.items():
        if pd.notna(revenue):
            print(f"  {year}: ${revenue/1e9:.2f}B")

# 净利润趋势
if 'Net Income' in income.index:
    profits = income.loc['Net Income'].head(4)
    print("\n=== 净利润趋势 ===")
    for year, profit in profits.items():
        if pd.notna(profit):
            print(f"  {year}: ${profit/1e9:.2f}B")

# EPS趋势
if 'Basic EPS' in income.index:
    eps = income.loc['Basic EPS'].head(4)
    print("\n=== EPS 趋势 ===")
    for year, e in eps.items():
        if pd.notna(e):
            print(f"  {year}: ${e:.2f}")
```

### 输出示例

```
=== 财务分析报告 ===

公司: Apple Inc. (AAPL)
分析期间: 2021-2024

一、关键财务指标

盈利能力:
  毛利率: 46.2%
  净利率: 25.3%
  运营利润率: 30.2%

估值指标:
  市盈率(PE): 28.5
  预期市盈率: 24.2
  市净率(PB): 45.2

成长性:
  营收增长率: 8.1%
  盈利增长率: 10.3%
  每股营收: $26.54

二、营收趋势

  2024-Q3: $94.93B (+8.1%)
  2024-Q2: $90.75B (+4.3%)
  2024-Q1: $119.58B (+2.1%)
  2023-Q4: $89.52B (+0.7%)

三、净利润趋势

  2024-Q3: $23.64B (+10.2%)
  2024-Q2: $21.45B (+8.5%)
  2024-Q1: $33.92B (+13.1%)
  2023-Q4: $22.96B (+10.8%)

四、综合评价

盈利能力: ⭐⭐⭐⭐⭐ (优秀)
  - 毛利率维持45%以上
  - 净利率稳定在25%左右

成长性: ⭐⭐⭐⭐ (良好)
  - 营收保持个位数增长
  - 盈利增速快于营收

估值水平: ⭐⭐⭐ (中等)
  - PE 28.5 处于历史中位
  - 预期PE 24.2 相对合理

投资建议:
  ✓ 基本面优秀，盈利能力强劲
  ✓ 现金流充裕，财务健康
  → 维持"增持"评级
  → 目标价: $210 (基于25x PE)
```

---

## 场景六：机构持仓分析

### 场景描述
分析机构持仓变化，了解主力动向。

### 分析目标
- 获取机构持仓数据
- 跟踪持仓变化
- 评估机构信心

### 分析流程

```python
import yfinance as yf

ticker = yf.Ticker("AAPL")

# 获取机构持仓
institutional = ticker.institutional_holders
print("\n=== 机构持仓 Top 10 ===")
print(institutional[['Holder', 'Shares', 'Date Reported', '% Out']].head(10))

# 获取主要股东
major_holders = ticker.major_holders
print("\n=== 主要股东 ===")
print(major_holders)

# 计算机构持股比例变化
if len(institutional) > 0:
    total_institutional = institutional['% Out'].sum()
    print(f"\n机构总持股比例: {total_institutional:.1f}%")
```

### 输出示例

```
=== 机构持仓分析报告 ===

公司: Apple Inc. (AAPL)

一、机构持仓 Top 10

  机构名称                        持股数       报告日期      持股比例
  Vanguard Total Stock Market    3,234,567   2024-09-30    21.5%
  Blackrock Fund Advisors        2,876,543   2024-09-30    19.1%
  State Street Global Advisors    1,987,654   2024-09-30    13.2%
  Berkshire Hathaway             1,234,567   2024-09-30     8.2%
  FMR LLC                       987,654     2024-09-30     6.5%
  Northern Trust                 765,432     2024-09-30     5.1%
  Bank of America                654,321     2024-09-30     4.3%
  JPMorgan Chase                 543,210     2024-09-30     3.6%
  UBS Group                     432,109     2024-09-30     2.9%
  Goldman Sachs                  321,098     2024-09-30     2.1%

二、关键发现

机构总持股比例: 87.5%
评估: 机构高度控盘 ✓

三、主要股东结构

  Vanguard + Blackrock + State Street = 53.8%
  评估: 指数基金主导，持股稳定

四、投资启示

  ✓ 机构持股比例高，市场认可度高
  ✓ Vanguard、Blackrock 等长线机构重仓
  → 股价稳定性强，中长期看好
  ⚠️ 机构高度控盘可能导致换手率低
```

---

## 场景七：外汇和大宗商品

### 场景描述
分析外汇和商品期货数据，进行跨资产配置。

### 分析目标
- 获取外汇和商品数据
- 分析价格趋势
- 评估相关性

### 分析流程

```python
import yfinance as yf

# 主要货币对
forex_pairs = ["EURUSD=X", "GBPUSD=X", "USDJPY=X", "USDCHF=X", "AUDUSD=X"]

# 大宗商品
commodities = ["GC=F",  # 黄金
               "SI=F",  # 白银
               "CL=F",  # 原油
               "NG=F"]  # 天然气

# 获取数据
forex_data = yf.download(forex_pairs, period="1y")
commodity_data = yf.download(commodities, period="1y")

# 提取收盘价
forex_close = forex_data['Close']
commodity_close = commodity_data['Close']

print("=== 外汇和大宗商品市场 ===")
print(f"货币对: {len(forex_pairs)}")
print(f"大宗商品: {len(commodities)}")
```

### 输出示例

```
=== 外汇和大宗商品市场分析 ===

一、外汇市场 (最近1年)

  EUR/USD: 1.0892 (年变化: -2.3%)
  GBP/USD: 1.2734 (年变化: +1.2%)
  USD/JPY: 149.52 (年变化: +8.5%)
  USD/CHF: 0.8765 (年变化: -3.2%)
  AUD/USD: 0.6543 (年变化: -5.1%)

  美元趋势: 强势 (JPY、CHF、AUD 贬值)

二、大宗商品 (最近1年)

  黄金 (GC=F): $2,045/盎司 (年变化: +8.2%)
  白银 (SI=F): $24.35/盎司 (年变化: +5.6%)
  原油 (CL=F): $78.45/桶 (年变化: -2.1%)
  天然气 (NG=F): $2.85/MMBtu (年变化: -18.5%)

  分析:
    - 黄金上涨 ← 避险需求
    - 原油下跌 ← 需求担忧
    - 天然气暴跌 ← 供应充足

三、投资建议

  商品配置:
    黄金: ⭐⭐⭐⭐⭐ (防御性强)
    白银: ⭐⭐⭐ (跟涨黄金)
    原油: ⭐⭐ (波动大，趋势不明)
    天然气: ⭐ (趋势向下)

  外汇策略:
    做多: USD/JPY (利差交易)
    做空: AUD/USD (商品货币疲软)
```

---

## 场景八：加密货币分析

### 场景描述
分析加密货币市场，进行数字资产配置。

### 分析目标
- 获取主流加密货币数据
- 计算收益和波动率
- 评估风险收益比

### 分析流程

```python
import yfinance as yf

# 主流加密货币
crypto_symbols = ["BTC-USD", "ETH-USD", "BNB-USD", "XRP-USD", "SOL-USD"]

# 获取数据
crypto_data = yf.download(crypto_symbols, period="1y")

# 提取收盘价
crypto_close = crypto_data['Close']

# 计算收益率
crypto_returns = crypto_close.pct_change().dropna()

# 统计分析
stats = pd.DataFrame({
    '年化收益率': crypto_returns.mean() * 365 * 100,
    '年化波动率': crypto_returns.std() * np.sqrt(365) * 100,
    '夏普比率': (crypto_returns.mean() * 365) / (crypto_returns.std() * np.sqrt(365)),
})

print("=== 加密货币统计分析 ===")
print(stats.round(2))
```

### 输出示例

```
=== 加密货币分析报告 ===

分析期间: 2023年-2024年

一、收益率和波动率

                年化收益率  年化波动率  夏普比率
BTC-USD (比特币)   +125.3%    72.5%      1.73
ETH-USD (以太坊)   +98.5%      85.2%      1.16
BNB-USD (币安)     +78.3%      92.5%      0.85
XRP-USD (瑞波)     +156.2%    115.3%     1.36
SOL-USD (索拉纳)   +324.5%    145.8%     2.22

二、风险收益评估

最高收益: SOL (+324.5%)
最低波动: BTC (72.5%)
最佳夏普: SOL (2.22)
最高风险: SOL (145.8%)

三、配置建议

保守型:
  70% BTC + 20% ETH + 10% BNB
  
平衡型:
  50% BTC + 30% ETH + 10% SOL + 10% BNB

进取型:
  40% SOL + 30% XRP + 20% ETH + 10% BTC

四、注意事项

⚠️ 高波动性:
  - 所有加密货币年化波动率 > 70%
  - 适合高风险偏好投资者

⚠️ 相关性:
  - 多数加密货币与BTC高度相关
  - 分散化效果有限

⚠️ 监管风险:
  - 各国监管政策不确定
  - 可能影响价格走势

投资建议:
  ⚠️ 加密货币属于高风险资产
  ⚠️ 建议仓位控制在总资产 5-10%
  ✓ 优先配置BTC和ETH
  → 定期定额策略更适合
```

---

## 总结

以上8个场景展示了 yFinance 数据在实际量化分析和投资决策中的典型应用：

1. **量化回测**：批量获取长周期美股数据
2. **全球资产配置**：多资产类别分析
3. **技术指标选股**：系统化选股策略
4. **期权策略分析**：期权链和波动率分析
5. **财报分析**：基本面深度分析
6. **机构持仓分析**：主力动向跟踪
7. **外汇和大宗商品**：跨资产配置
8. **加密货币分析**：数字资产投资

这些场景可以作为量化分析和投资决策的参考模板。
