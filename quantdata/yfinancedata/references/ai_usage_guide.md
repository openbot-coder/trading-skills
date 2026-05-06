# AI 使用指南

## 数据查询最佳实践

### 1. 基础使用流程

yFinance 数据查询的标准流程：

```python
import yfinance as yf
import pandas as pd

# Step 1: 创建 Ticker 对象
ticker = yf.Ticker("AAPL")

# Step 2: 获取数据
hist = ticker.history(period="1y")  # 历史行情
info = ticker.info  # 基本信息
income = ticker.income_stmt  # 利润表

# Step 3: 数据处理
print(hist.head())
print(f"当前价格: ${info['currentPrice']}")
```

### 2. 数据解析规范

#### 返回值结构

```python
# history() 返回 DataFrame
hist = ticker.history(period="1y")
# 列: Open, High, Low, Close, Volume, Dividends, Stock Splits

# info 返回 dict
info = ticker.info
# 包含所有基本信息字段

# 财务报表返回 DataFrame
income = ticker.income_stmt
# 每行是一个财务指标，每列是一个季度/年度
```

#### 数据类型转换

```python
import yfinance as yf

ticker = yf.Ticker("AAPL")
hist = ticker.history(period="1y")

# 自动转换类型（yfinance 通常已处理）
print(hist.dtypes)
# Open         float64
# High         float64
# Low          float64
# Close        float64
# Volume       int64
# Dividends    float64
# Stock Splits float64

# 如果需要手动转换
hist['Close'] = pd.to_numeric(hist['Close'], errors='coerce')
hist['Volume'] = pd.to_numeric(hist['Volume'], errors='coerce')
```

### 3. 错误处理模式

#### 基础错误处理

```python
import yfinance as yf

def get_ticker_data(symbol, period="1y"):
    """获取股票数据，带错误处理"""
    
    try:
        # 创建 Ticker 对象
        ticker = yf.Ticker(symbol)
        
        # 尝试获取历史数据
        hist = ticker.history(period=period)
        
        if hist.empty:
            print(f"警告: {symbol} 无历史数据")
            return None
        
        # 获取基本信息
        try:
            info = ticker.info
        except:
            info = {}
            print(f"警告: {symbol} 无法获取基本信息")
        
        return {
            'symbol': symbol,
            'history': hist,
            'info': info,
            'success': True
        }
        
    except Exception as e:
        print(f"错误: {symbol} - {str(e)}")
        return None

# 使用
result = get_ticker_data("AAPL")
if result:
    print(f"成功获取 {result['symbol']} 的数据")
```

#### 批量查询错误处理

```python
import yfinance as yf

def batch_get_ticker_data(symbols, period="1y"):
    """批量获取多只股票数据"""
    
    results = {}
    failed_symbols = []
    
    for symbol in symbols:
        try:
            ticker = yf.Ticker(symbol)
            hist = ticker.history(period=period)
            
            if not hist.empty:
                results[symbol] = hist
            else:
                failed_symbols.append((symbol, "空数据集"))
                
        except Exception as e:
            failed_symbols.append((symbol, str(e)))
    
    # 输出失败信息
    if failed_symbols:
        print(f"失败股票数: {len(failed_symbols)}")
        for symbol, reason in failed_symbols[:5]:  # 只显示前5个
            print(f"  {symbol}: {reason}")
    
    return results, failed_symbols

# 使用
symbols = ["AAPL", "MSFT", "GOOGL", "INVALID", "AMZN"]
results, failed = batch_get_ticker_data(symbols)
print(f"成功获取: {len(results)} 只股票")
```

### 4. 数据验证

#### 完整性检查

```python
import yfinance as yf

def validate_data(df, expected_cols=None):
    """验证数据完整性"""
    
    checks = {
        'row_count': len(df),
        'columns': list(df.columns),
        'null_counts': df.isnull().sum().to_dict(),
        'date_range': (df.index.min(), df.index.max()) if len(df) > 0 else None
    }
    
    # 检查必要字段
    if expected_cols:
        missing_cols = set(expected_cols) - set(df.columns)
        if missing_cols:
            print(f"缺少字段: {missing_cols}")
    
    # 检查空值
    if df.isnull().any().any():
        print(f"存在空值:\n{df.isnull().sum()}")
    
    # 检查日期连续性
    if len(df) > 1:
        date_diffs = df.index.to_series().diff()
        gaps = date_diffs[date_diffs > pd.Timedelta(days=10)]
        if len(gaps) > 0:
            print(f"存在大于10天的数据缺口: {len(gaps)} 处")
    
    return checks
```

#### 数据合理性检查

```python
import yfinance as yf

def sanity_check(df):
    """数据合理性检查"""
    
    issues = []
    
    # 价格检查
    if 'Close' in df.columns:
        if (df['Close'] <= 0).any():
            issues.append("存在非正价格")
        
        if 'High' in df.columns and 'Low' in df.columns:
            if (df['High'] < df['Low']).any():
                issues.append("存在最高价<最低价")
    
    # 成交量检查
    if 'Volume' in df.columns:
        if (df['Volume'] < 0).any():
            issues.append("存在负成交量")
    
    if issues:
        print("数据问题:")
        for issue in issues:
            print(f"  - {issue}")
        return False
    else:
        print("数据通过合理性检查")
        return True

# 使用
ticker = yf.Ticker("AAPL")
hist = ticker.history(period="1mo")
sanity_check(hist)
```

### 5. 数据处理模板

#### 日线数据处理

```python
import yfinance as yf
import pandas as pd
import numpy as np

def process_daily_data(df):
    """处理日线数据"""
    
    # 确保数据类型正确
    numeric_cols = ['Open', 'High', 'Low', 'Close', 'Volume']
    for col in numeric_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')
    
    # 计算收益率
    df['Returns'] = df['Close'].pct_change()
    df['Log_Returns'] = np.log(df['Close'] / df['Close'].shift(1))
    
    # 计算移动平均
    for window in [5, 10, 20, 60]:
        df[f'MA{window}'] = df['Close'].rolling(window=window).mean()
    
    # 计算波动率
    df['Volatility_20'] = df['Returns'].rolling(window=20).std()
    
    # 计算成交量移动平均
    df['Volume_MA20'] = df['Volume'].rolling(window=20).mean()
    df['Volume_Ratio'] = df['Volume'] / df['Volume_MA20']
    
    return df

# 使用
ticker = yf.Ticker("AAPL")
hist = ticker.history(period="1y")
processed = process_daily_data(hist)
print(processed.tail())
```

#### 财务报表处理

```python
import yfinance as yf
import pandas as pd

def process_financial_data(ticker):
    """处理财务数据"""
    
    # 获取财务数据
    income = ticker.income_stmt
    balance = ticker.balance_sheet
    cashflow = ticker.cashflow
    
    # 转置数据（让时间成为行）
    if not income.empty:
        income_t = income.T
        print(f"最近4个季度营收趋势:")
        if 'Total Revenue' in income.index:
            print(income.loc['Total Revenue'].head(4))
    
    return income, balance, cashflow

# 使用
ticker = yf.Ticker("AAPL")
income, balance, cashflow = process_financial_data(ticker)
```

### 6. 数据缓存策略

```python
import os
import pickle
from datetime import datetime, timedelta
import yfinance as yf

def get_cached_data(symbol, period="1y", cache_dir='cache', cache_hours=24):
    """带缓存的数据获取"""
    
    # 生成缓存文件名
    cache_file = os.path.join(
        cache_dir, 
        f"{symbol}_{period}.pkl"
    )
    
    # 检查缓存
    if os.path.exists(cache_file):
        file_time = datetime.fromtimestamp(os.path.getmtime(cache_file))
        if datetime.now() - file_time < timedelta(hours=cache_hours):
            print(f"使用缓存: {cache_file}")
            with open(cache_file, 'rb') as f:
                return pickle.load(f)
    
    # 获取新数据
    ticker = yf.Ticker(symbol)
    hist = ticker.history(period=period)
    
    # 保存缓存
    os.makedirs(cache_dir, exist_ok=True)
    with open(cache_file, 'wb') as f:
        pickle.dump(hist, f)
    
    print(f"新数据已缓存: {cache_file}")
    return hist
```

### 7. 性能优化技巧

#### 批量查询优化

```python
import yfinance as yf

# ❌ 低效：逐个查询
for symbol in stock_list:
    ticker = yf.Ticker(symbol)
    hist = ticker.history(period="1y")
    # 处理...

# ✅ 高效：使用 download 批量下载
data = yf.download(
    stock_list,
    period="1y",
    threads=True,  # 启用多线程
    progress=False
)
print(data['Close'].head())

# ✅ 高效：使用 Tickers 批量获取
tickers = yf.Tickers("AAPL MSFT GOOGL AMZN META")
for ticker in tickers.tickers:
    info = ticker.info
    print(f"{info['symbol']}: ${info['currentPrice']}")
```

#### 数据类型优化

```python
# ❌ 低效：逐行处理
for idx, row in hist.iterrows():
    # 处理每行数据
    pass

# ✅ 高效：向量化操作
hist['Returns'] = hist['Close'].pct_change()
hist['MA20'] = hist['Close'].rolling(window=20).mean()
hist['Signal'] = (hist['Close'] > hist['MA20']).astype(int)

# ✅ 高效：使用 apply
hist['Price_Range'] = hist.apply(
    lambda x: (x['High'] - x['Low']) / x['Low'] * 100, 
    axis=1
)
```

#### 内存优化

```python
import yfinance as yf
import pandas as pd

# ❌ 低效：大数据量时保留所有列
data = yf.download("AAPL", period="10y")

# ✅ 高效：只选择需要的列
data = yf.download("AAPL", period="10y")
data = data[['Open', 'High', 'Low', 'Close', 'Volume']]

# ✅ 高效：使用适当的 dtype
data['Volume'] = data['Volume'].astype('int32')

# ✅ 高效：分块处理
for chunk in pd.read_csv('large_file.csv', chunksize=10000):
    # 处理每个 chunk
    pass
```

### 8. 合规使用

#### 使用规范

✅ **正确做法**：
- 用于个人学习、研究、量化回测
- 遵守 Yahoo 服务条款
- 标注数据来源
- 尊重数据版权

❌ **错误做法**：
- 用于商业营利（需遵守 Yahoo 条款）
- 未经授权大量分发数据
- 违反相关法律法规
- 恶意请求造成服务器负担

#### 数据引用格式

```
数据来源：Yahoo Finance (via yFinance)
获取日期：[具体日期]
股票代码：[具体代码]
数据范围：[具体时间范围]
免责声明：数据仅供参考，不构成投资建议
```

## 数据分析示例

### 示例1：趋势分析

```python
import yfinance as yf
import pandas as pd
import numpy as np

# 获取数据
ticker = yf.Ticker("AAPL")
hist = ticker.history(period="2y")

# 数据处理
hist['MA20'] = hist['Close'].rolling(window=20).mean()
hist['MA50'] = hist['Close'].rolling(window=50).mean()
hist['MA200'] = hist['Close'].rolling(window=200).mean()
hist['Returns'] = hist['Close'].pct_change()

# 分析
print("=== 趋势分析报告 ===")
print(f"分析期间: {hist.index.min()} 至 {hist.index.max()}")
print(f"最新价格: ${hist['Close'].iloc[-1]:.2f}")
print(f"MA20: ${hist['MA20'].iloc[-1]:.2f}")
print(f"MA50: ${hist['MA50'].iloc[-1]:.2f}")
print(f"MA200: ${hist['MA200'].iloc[-1]:.2f}")

# 趋势判断
if hist['Close'].iloc[-1] > hist['MA200'].iloc[-1]:
    print("长期趋势: 上升")
elif hist['Close'].iloc[-1] < hist['MA200'].iloc[-1]:
    print("长期趋势: 下降")
else:
    print("长期趋势: 震荡")

# 动量指标
print(f"\n动量指标:")
print(f"20日收益率: {hist['Returns'].tail(20).sum()*100:.2f}%")
print(f"20日波动率: {hist['Returns'].tail(20).std()*100:.2f}%")
```

### 示例2：均线策略回测

```python
import yfinance as yf
import pandas as pd

def backtest_ma_strategy(ticker_symbol, short_ma=20, long_ma=50, 
                        start="2020-01-01", end="2024-12-31"):
    """均线交叉策略回测"""
    
    # 获取数据
    ticker = yf.Ticker(ticker_symbol)
    data = ticker.history(start=start, end=end)
    
    # 计算均线
    data['MA_short'] = data['Close'].rolling(window=short_ma).mean()
    data['MA_long'] = data['Close'].rolling(window=long_ma).mean()
    
    # 生成信号
    data['Signal'] = 0
    data.loc[data['MA_short'] > data['MA_long'], 'Signal'] = 1
    data.loc[data['MA_short'] <= data['MA_long'], 'Signal'] = -1
    
    # 持仓信号
    data['Position'] = data['Signal'].shift(1)
    
    # 计算收益
    data['Returns'] = data['Close'].pct_change()
    data['Strategy_Returns'] = data['Position'] * data['Returns']
    
    # 累计收益
    data['Buy_Hold'] = (1 + data['Returns']).cumprod()
    data['Strategy'] = (1 + data['Strategy_Returns']).cumprod()
    
    # 回测结果
    print(f"\n=== 均线策略回测 ({short_ma}/{long_ma}) ===")
    print(f"买入持有收益率: {(data['Buy_Hold'].iloc[-1] - 1)*100:.2f}%")
    print(f"策略收益率: {(data['Strategy'].iloc[-1] - 1)*100:.2f}%")
    print(f"策略超额收益: {(data['Strategy'].iloc[-1] - data['Buy_Hold'].iloc[-1])*100:.2f}%")
    
    return data

# 使用
result = backtest_ma_strategy("AAPL")
```

## 注意事项

### 数据限制

1. **分钟数据保存期限**：1分钟数据仅保存7天
2. **数据延迟**：实时数据可能有15分钟延迟
3. **A股数据**：不如美股完整，建议用 baostockdata
4. **信息获取失败**：info 可能因网络问题失败

### 数据质量

1. **复权数据**：使用 `auto_adjust=True` 自动复权
2. **分红数据**：`actions=True` 包含分红和拆股
3. **历史调整**：财务报表可能有调整

### 性能建议

1. **批量查询**：使用 `yf.download()` 或 `yf.Tickers()`
2. **缓存使用**：对频繁使用的数据进行缓存
3. **数据类型**：及时转换数据类型
4. **请求限制**：合理控制请求频率
