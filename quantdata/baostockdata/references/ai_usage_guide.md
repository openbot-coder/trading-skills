# AI 使用指南

## 数据查询最佳实践

### 1. 基础使用流程

Baostock 数据查询的标准流程：

```python
import baostock as bs
import pandas as pd

# Step 1: 登录系统
bs.login()

# Step 2: 执行查询
rs = bs.query_history_k_data_plus(
    code="sh.600000",
    fields="date,code,open,high,low,close,volume,amount",
    start_date="2023-01-01",
    end_date="2023-12-31",
    frequency="d",
    adjustflag="2"
)

# Step 3: 转换为 DataFrame
data_list = []
while (rs.error_code == '0') & rs.next():
    data_list.append(rs.get_row_data())

df = pd.DataFrame(data_list, columns=rs.fields)

# Step 4: 数据类型转换
numeric_cols = ['open', 'high', 'low', 'close', 'volume', 'amount']
for col in numeric_cols:
    df[col] = pd.to_numeric(df[col], errors='coerce')

# Step 5: 登出系统
bs.logout()
```

### 2. 数据解析规范

#### 返回值结构

```python
# rs.error_code: '0' 表示成功
# rs.error_msg: 错误信息
# rs.fields: 返回的字段列表
# rs.next(): 是否有下一条数据
# rs.get_row_data(): 获取当前行数据
```

#### 数据类型转换

```python
# 数值型字段
df['close'] = pd.to_numeric(df['close'], errors='coerce')

# 日期型字段
df['date'] = pd.to_datetime(df['date'])

# 检查数据类型
print(df.dtypes)
```

### 3. 错误处理模式

#### 基础错误处理

```python
def query_with_error_handling(code, start_date, end_date):
    """带错误处理的查询函数"""
    
    try:
        # 登录
        lg = bs.login()
        if lg.error_code != '0':
            print(f"登录失败: {lg.error_msg}")
            return None
        
        # 查询
        rs = bs.query_history_k_data_plus(
            code=code,
            fields="date,code,open,high,low,close,volume",
            start_date=start_date,
            end_date=end_date,
            frequency="d"
        )
        
        if rs.error_code != '0':
            print(f"查询失败: {rs.error_msg}")
            return None
        
        # 提取数据
        data_list = []
        while rs.next():
            data_list.append(rs.get_row_data())
        
        df = pd.DataFrame(data_list, columns=rs.fields)
        
        if df.empty:
            print(f"未获取到 {code} 在 {start_date} 至 {end_date} 的数据")
            return None
        
        return df
        
    except Exception as e:
        print(f"异常: {str(e)}")
        return None
    
    finally:
        bs.logout()
```

#### 批量查询错误处理

```python
def batch_query(codes, start_date, end_date):
    """批量查询多只股票"""
    
    all_data = []
    failed_stocks = []
    
    bs.login()
    
    for code in codes:
        try:
            rs = bs.query_history_k_data_plus(
                code,
                "date,code,open,high,low,close,volume,amount",
                start_date,
                end_date,
                frequency="d"
            )
            
            if rs.error_code == '0':
                data_list = []
                while rs.next():
                    data_list.append(rs.get_row_data())
                
                if data_list:
                    df = pd.DataFrame(data_list, columns=rs.fields)
                    all_data.append(df)
                else:
                    failed_stocks.append((code, "空数据集"))
            else:
                failed_stocks.append((code, rs.error_msg))
                
        except Exception as e:
            failed_stocks.append((code, str(e)))
    
    bs.logout()
    
    # 合并结果
    if all_data:
        result = pd.concat(all_data, ignore_index=True)
    else:
        result = pd.DataFrame()
    
    # 输出失败信息
    if failed_stocks:
        print(f"失败股票数: {len(failed_stocks)}")
        for code, reason in failed_stocks[:5]:  # 只显示前5个
            print(f"  {code}: {reason}")
    
    return result, failed_stocks
```

### 4. 数据验证

#### 完整性检查

```python
def validate_data(df, expected_cols):
    """验证数据完整性"""
    
    checks = {
        'columns': list(df.columns),
        'expected': expected_cols,
        'row_count': len(df),
        'null_counts': df.isnull().sum(),
        'date_range': (df['date'].min(), df['date'].max()) if 'date' in df.columns else None
    }
    
    # 检查必要字段
    missing_cols = set(expected_cols) - set(df.columns)
    if missing_cols:
        print(f"缺少字段: {missing_cols}")
    
    # 检查空值
    if df.isnull().any().any():
        print(f"存在空值:\n{df.isnull().sum()}")
    
    # 检查日期连续性
    if 'date' in df.columns:
        df_sorted = df.sort_values('date')
        date_diffs = pd.to_datetime(df_sorted['date']).diff()
        gaps = date_diffs[date_diffs > pd.Timedelta(days=7)]
        if len(gaps) > 0:
            print(f"存在大于7天的数据缺口: {len(gaps)} 处")
    
    return checks
```

#### 数据合理性检查

```python
def sanity_check(df):
    """数据合理性检查"""
    
    issues = []
    
    # 价格检查
    if 'close' in df.columns:
        if (df['close'] <= 0).any():
            issues.append("存在非正价格")
        
        if 'high' in df.columns:
            if (df['high'] < df['low']).any():
                issues.append("存在最高价<最低价")
            
            if (df['close'] > df['high']).any():
                issues.append("存在收盘价>最高价")
    
    # 成交量检查
    if 'volume' in df.columns:
        if (df['volume'] < 0).any():
            issues.append("存在负成交量")
    
    # 涨跌幅检查
    if 'pctChg' in df.columns:
        pct = pd.to_numeric(df['pctChg'], errors='coerce')
        if ((pct > 20) | (pct < -20)).any():
            issues.append("存在涨跌幅超过20%的异常数据")
    
    if issues:
        print("数据问题:")
        for issue in issues:
            print(f"  - {issue}")
    else:
        print("数据通过合理性检查")
    
    return len(issues) == 0
```

### 5. 数据处理模板

#### 日线数据处理

```python
def process_daily_data(df):
    """处理日线数据"""
    
    # 类型转换
    numeric_cols = ['open', 'high', 'low', 'close', 'volume', 'amount']
    for col in numeric_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')
    
    # 日期处理
    df['date'] = pd.to_datetime(df['date'])
    df = df.sort_values('date')
    
    # 计算收益率
    if 'close' in df.columns:
        df['returns'] = df['close'].pct_change()
        df['log_returns'] = np.log(df['close'] / df['close'].shift(1))
    
    # 计算移动平均
    for window in [5, 10, 20, 60]:
        if 'close' in df.columns:
            df[f'MA{window}'] = df['close'].rolling(window=window).mean()
    
    # 计算波动率
    if 'returns' in df.columns:
        df['volatility_20'] = df['returns'].rolling(window=20).std()
    
    return df
```

#### 分钟数据处理

```python
def process_minute_data(df):
    """处理分钟数据"""
    
    # 类型转换
    numeric_cols = ['open', 'high', 'low', 'close', 'volume']
    for col in numeric_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')
    
    # 时间处理
    df['datetime'] = pd.to_datetime(df['date'] + ' ' + df['time'])
    df = df.sort_values('datetime')
    
    # 转换为百分比收益率
    if 'close' in df.columns:
        df['returns'] = df['close'].pct_change()
    
    return df
```

### 6. 数据缓存策略

```python
import os
import pickle
from datetime import datetime, timedelta

def get_cached_data(code, start_date, end_date, cache_dir='cache'):
    """带缓存的数据获取"""
    
    # 生成缓存文件名
    cache_file = os.path.join(
        cache_dir, 
        f"{code.replace('.', '_')}_{start_date}_{end_date}.pkl"
    )
    
    # 检查缓存
    if os.path.exists(cache_file):
        file_time = datetime.fromtimestamp(os.path.getmtime(cache_file))
        if datetime.now() - file_time < timedelta(hours=24):
            print(f"使用缓存: {cache_file}")
            with open(cache_file, 'rb') as f:
                return pickle.load(f)
    
    # 获取新数据
    bs.login()
    rs = bs.query_history_k_data_plus(
        code,
        "date,code,open,high,low,close,volume,amount",
        start_date,
        end_date,
        frequency="d"
    )
    
    data_list = []
    while (rs.error_code == '0') & rs.next():
        data_list.append(rs.get_row_data())
    
    df = pd.DataFrame(data_list, columns=rs.fields)
    bs.logout()
    
    # 保存缓存
    os.makedirs(cache_dir, exist_ok=True)
    with open(cache_file, 'wb') as f:
        pickle.dump(df, f)
    
    print(f"新数据已缓存: {cache_file}")
    return df
```

### 7. 性能优化技巧

#### 批量查询优化

```python
# ❌ 低效：逐个查询
for code in stock_list:
    rs = bs.query_history_k_data_plus(code, ...)
    df = rs.get_data()
    # 处理...

# ✅ 高效：减少登录登出次数
bs.login()
for code in stock_list:
    rs = bs.query_history_k_data_plus(code, ...)
    # 处理...
bs.logout()
```

#### 数据类型优化

```python
# ❌ 低效：逐行处理
data_list = []
while rs.next():
    data_list.append(rs.get_row_data())

# ✅ 高效：批量处理
data_list = []
while rs.next():
    data_list.append(rs.get_row_data())

df = pd.DataFrame(data_list, columns=rs.fields)

# 一次性转换类型
numeric_cols = ['open', 'high', 'low', 'close', 'volume', 'amount']
for col in numeric_cols:
    if col in df.columns:
        df[col] = pd.to_numeric(df[col], errors='coerce')
```

#### 内存优化

```python
# ❌ 低效：大数据量时代码冗余
all_data = []
for code in codes:
    rs = bs.query_history_k_data_plus(...)
    data_list = []
    while rs.next():
        data_list.append(rs.get_row_data())
    all_data.extend(data_list)  # 逐步扩展

# ✅ 高效：使用生成器和 chunk
def generate_data(code, start_date, end_date):
    bs.login()
    rs = bs.query_history_k_data_plus(code, ...)
    while rs.next():
        yield rs.get_row_data()
    bs.logout()

# 迭代获取
for code in codes:
    for row in generate_data(code, start_date, end_date):
        # 处理单行数据
        pass
```

### 8. 合规使用

#### 使用规范

✅ **正确做法**：
- 用于个人学习、研究、量化回测
- 遵守数据使用条款
- 标注数据来源
- 尊重数据版权

❌ **错误做法**：
- 用于商业营利
- 未经授权二次分发数据
- 违反相关法律法规
- 恶意请求造成服务器负担

#### 数据引用格式

```
数据来源：Baostock (http://baostock.com)
获取日期：[具体日期]
数据范围：[具体股票和时间范围]
```

## 数据分析示例

### 示例1：趋势分析

```python
import baostock as bs
import pandas as pd
import numpy as np

bs.login()

# 获取数据
rs = bs.query_history_k_data_plus(
    "sh.600000",
    "date,code,open,high,low,close,volume,pctChg",
    start_date="2023-01-01",
    end_date="2024-12-31"
)

data_list = []
while (rs.error_code == '0') & rs.next():
    data_list.append(rs.get_row_data())

df = pd.DataFrame(data_list, columns=rs.fields)

# 类型转换
numeric_cols = ['open', 'high', 'low', 'close', 'volume', 'pctChg']
for col in numeric_cols:
    df[col] = pd.to_numeric(df[col], errors='coerce')

df['date'] = pd.to_datetime(df['date'])
df = df.sort_values('date')

# 计算指标
df['MA5'] = df['close'].rolling(window=5).mean()
df['MA20'] = df['close'].rolling(window=20).mean()
df['returns'] = df['close'].pct_change()

bs.logout()

# 分析结果
print("=== 趋势分析报告 ===")
print(f"分析期间: {df['date'].min()} 至 {df['date'].max()}")
print(f"总交易日: {len(df)}")
print(f"区间涨跌幅: {((df['close'].iloc[-1] / df['close'].iloc[0]) - 1) * 100:.2f}%")
print(f"平均日收益率: {df['returns'].mean() * 100:.4f}%")
print(f"收益率标准差: {df['returns'].std() * 100:.4f}%")
print(f"最大日涨幅: {df['pctChg'].max():.2f}%")
print(f"最大日跌幅: {df['pctChg'].min():.2f}%")
```

### 示例2：均线策略回测

```python
def backtest_ma_strategy(code, short_ma=5, long_ma=20, start_date="2020-01-01", end_date="2024-12-31"):
    """均线交叉策略回测"""
    
    bs.login()
    
    # 获取数据
    rs = bs.query_history_k_data_plus(
        code,
        "date,code,close",
        start_date,
        end_date,
        frequency="d"
    )
    
    data_list = []
    while (rs.error_code == '0') & rs.next():
        data_list.append(rs.get_row_data())
    
    df = pd.DataFrame(data_list, columns=rs.fields)
    df['close'] = pd.to_numeric(df['close'], errors='coerce')
    df['date'] = pd.to_datetime(df['date'])
    df = df.sort_values('date')
    
    # 计算均线
    df['MA_short'] = df['close'].rolling(window=short_ma).mean()
    df['MA_long'] = df['close'].rolling(window=long_ma).mean()
    
    # 生成信号
    df['signal'] = 0
    df.loc[df['MA_short'] > df['MA_long'], 'signal'] = 1  # 金叉
    df.loc[df['MA_short'] <= df['MA_long'], 'signal'] = -1  # 死叉
    
    # 计算持仓
    df['position'] = df['signal'].shift(1)  # 信号次日执行
    df['returns'] = df['close'].pct_change()
    df['strategy_returns'] = df['position'] * df['returns']
    
    # 计算累计收益
    df['cum_returns'] = (1 + df['returns']).cumprod()
    df['cum_strategy'] = (1 + df['strategy_returns']).cumprod()
    
    bs.logout()
    
    # 回测结果
    print(f"\n=== 均线策略回测 ({short_ma}/{long_ma}) ===")
    print(f"买入持有收益率: {(df['cum_returns'].iloc[-1] - 1) * 100:.2f}%")
    print(f"策略收益率: {(df['cum_strategy'].iloc[-1] - 1) * 100:.2f}%")
    
    return df
```

## 注意事项

### 数据限制

1. **登录超时**：长时间无操作需要重新登录
2. **单次查询量**：避免一次查询过多数据（如30年的分钟数据）
3. **日期格式**：必须使用 `YYYY-MM-DD` 格式
4. **复权选择**：根据分析目的选择合适的复权方式

### 数据质量

1. **停牌日**：停牌期间无交易数据
2. **ST股票**：特别处理的股票可能有异常波动
3. **新股**：新股上市首日可能有较大波动
4. **退市**：退市股票数据可能不完整

### 性能建议

1. **批量查询**：多次查询时减少登录登出次数
2. **缓存使用**：对频繁使用的数据进行缓存
3. **数据类型**：及时转换数据类型，避免类型推断
4. **内存管理**：处理大数据时注意内存使用
