# QuantData 数据路由表

本文档定义了 QuantData 量化数据源路由中心的数据路由规则。

## 路由决策逻辑

QuantData 根据以下规则自动路由数据请求：

1. **识别市场**：根据股票代码前缀识别市场（sh/sz/hk/us等）
2. **识别数据类型**：根据查询意图识别数据类型（行情/K线/财务等）
3. **选择数据源**：根据市场+数据类型选择最优的子技能
4. **执行查询**：调用对应子技能获取数据（自动重试3次）
5. **格式化返回**：将数据转换为统一格式返回

## 自动重试机制

QuantData 内置**智能重试机制**，确保数据获取的可靠性：

### 重试策略

```
重试配置：
- 最大重试次数：3次
- 重试间隔：1秒 → 2秒 → 4秒（指数退避）
- 超时时间：30秒
- 自动降级：主数据源失败时自动切换备选数据源
```

### 重试触发条件

- **网络错误**：网络连接失败、DNS解析失败
- **请求超时**：超过30秒未响应
- **服务端错误**：HTTP 5xx 错误（服务器内部错误）
- **限流错误**：HTTP 429 错误（请求过于频繁）

### 重试流程图

```
请求发送
    ↓
[1] 首次尝试
    ↓
成功？ → 返回数据
    ↓ 否
等待 1秒
    ↓
[2] 第2次尝试
    ↓
成功？ → 返回数据
    ↓ 否
等待 2秒
    ↓
[3] 第3次尝试
    ↓
成功？ → 返回数据
    ↓ 否
切换备选数据源
    ↓
返回错误信息
```

### 重试代码示例

```python
def query_with_retry(ticker, max_retries=3):
    """带重试机制的数据查询"""
    
    for attempt in range(max_retries):
        try:
            # 计算重试间隔（指数退避）
            if attempt > 0:
                wait_time = 2 ** attempt  # 1, 2, 4秒
                time.sleep(wait_time)
            
            # 尝试获取数据
            data = query_data_source(ticker)
            
            if data:
                return {
                    'success': True,
                    'data': data,
                    'attempts': attempt + 1
                }
                
        except (NetworkError, TimeoutError, ServerError) as e:
            if attempt == max_retries - 1:
                # 最后一次尝试也失败
                return {
                    'success': False,
                    'error': str(e),
                    'attempts': attempt + 1,
                    'fallback': '切换备选数据源'
                }
            continue
        except RateLimitError:
            if attempt == max_retries - 1:
                return {
                    'success': False,
                    'error': '请求过于频繁',
                    'attempts': attempt + 1,
                    'fallback': '切换备选数据源'
                }
            continue
    
    return {
        'success': False,
        'error': '重试次数耗尽',
        'attempts': max_retries
    }
```

### 重试状态码处理

| HTTP状态码 | 错误类型 | 重试策略 | 说明 |
|-----------|---------|---------|------|
| 200 | 成功 | 不重试 | 请求成功 |
| 400 | 客户端错误 | 不重试 | 请求参数错误 |
| 401 | 认证错误 | 不重试 | 需要认证 |
| 403 | 权限错误 | 不重试 | 无权限访问 |
| 404 | 资源不存在 | 不重试 | 数据不存在 |
| 429 | 限流 | 重试3次 | 等待后重试 |
| 500 | 服务器错误 | 重试3次 | 服务器问题 |
| 502 | 网关错误 | 重试3次 | 临时错误 |
| 503 | 服务不可用 | 重试3次 | 临时不可用 |
| 504 | 网关超时 | 重试3次 | 超时错误 |

## 路由规则表

### 一级路由：按市场类型

| 证券市场 | 代码前缀 | 代码示例 | 优先数据源 | 备选数据源 | 说明 |
|---------|---------|---------|----------|-----------|------|
| **上海证券市场** | sh. / SH. | sh.600000 | westockdata ⭐ | crawldata / baostockdata | 沪市主板、科创板 |
| **深圳证券市场** | sz. / SZ. | sz.000001 | westockdata ⭐ | crawldata / baostockdata | 深市主板、创业板 |
| **北京证券交易所** | bj. / BJ. | bj.430047 | westockdata | baostockdata | 北交所 |
| **香港证券市场** | hk. / HK. / .HK | 0700.HK | westockdata | yfinancedata | 港股主板、窝轮、牛熊证 |
| **美国证券市场** | us. / US. / 纯字母 | AAPL | yfinancedata ⭐ | westockdata | 美股（NYSE、NASDAQ、AMEX） |
| **美国ETF/指数** | ^ / 特殊代码 | SPY, ^GSPC | yfinancedata ⭐ | --- | 美股ETF、指数 |
| **全球指数** | ^ / 特殊代码 | ^N225, ^FTSE | yfinancedata | --- | 全球主要指数 |
| **国际期货市场** | hf_ / HF_ | hf_GC | crawldata ⭐ | yfinancedata | 黄金/原油/白银等国际期货 |
| **外汇市场** | XXXYYY=X | EURUSD=X | yfinancedata | --- | 货币对 |
| **加密货币** | XXX-YYY | BTC-USD | coingeckodata ⭐ | yfinancedata / okxdata / binancedata | 主流加密货币 |
| **OKX交易所** | OKX交易对 | BTC-USDT-SWAP | okxdata ⭐ | binancedata / yfinancedata | OKX永续合约 |
| **币安交易所** | Binance | BTCUSDT | binancedata ⭐ | okxdata / yfinancedata | 币安USDT交易对 |
| **期货市场** | XXX=F | CL=F | yfinancedata / okxdata / binancedata | 商品期货 |
| **上海期货交易所** | sf. / SF. | 待扩展 | --- | --- | 期货（待支持） |
| **大连商品交易所** | df. / DF. | 待扩展 | --- | --- | 商品期货（待支持） |
| **郑州商品交易所** | zf. / ZF. | 待扩展 | --- | --- | 商品期货（待支持） |

---

### 二级路由：按证券类型

#### 1. 股票 (Stock)

| 证券市场 | 数据类型 | crawldata | westockdata | baostockdata | yfinancedata | 说明 |
|---------|---------|----------|-------------|--------------|----------|------|
| 上海 | 实时价格 | ✅ 支持 | ✅ **支持 ⭐** | ❌ 不支持 | ❌ 不支持 | westockdata优先，全字段 |
| 上海 | K线数据 | ✅ 支持 | ✅ **支持 ⭐** | ✅ 支持 | ❌ 不支持 | westockdata优先，支持日K/周K/月K |
| 上海 | 分钟数据 | ✅ 支持 | ✅ **支持 ⭐** | ✅ 支持 | ❌ 不支持 | westockdata实时，crawldata支持5分钟K |
| 上海 | 财务报表 | ❌ 不支持 | ✅ 支持 | ✅ 支持 | ❌ 不支持 | 均支持 |
| 上海 | 资金流向 | ❌ 不支持 | ✅ 支持 | ❌ 不支持 | ❌ 不支持 | 仅westockdata |
| 上海 | 技术指标 | ❌ 不支持 | ✅ 支持 | ❌ 不支持 | ❌ 不支持 | 仅westockdata |
| 上海 | 分红数据 | ❌ 不支持 | ✅ 支持 | ✅ 支持 | ❌ 不支持 | 均支持 |
| 深圳 | 实时价格 | ✅ 支持 | ✅ **支持 ⭐** | ❌ 不支持 | ❌ 不支持 | westockdata优先，全字段 |
| 深圳 | K线数据 | ✅ 支持 | ✅ **支持 ⭐** | ✅ 支持 | ❌ 不支持 | westockdata优先，支持日K/周K/月K |
| 深圳 | 分钟数据 | ✅ 支持 | ✅ **支持 ⭐** | ✅ 支持 | ❌ 不支持 | westockdata实时，crawldata支持5分钟K |
| 深圳 | 财务报表 | ❌ 不支持 | ✅ 支持 | ✅ 支持 | ❌ 不支持 | 均支持 |
| 深圳 | 资金流向 | ❌ 不支持 | ✅ 支持 | ❌ 不支持 | ❌ 不支持 | 仅westockdata |
| 深圳 | 技术指标 | ❌ 不支持 | ✅ 支持 | ❌ 不支持 | ❌ 不支持 | 仅westockdata |
| 深圳 | 分红数据 | ❌ 不支持 | ✅ 支持 | ✅ 支持 | ❌ 不支持 | 均支持 |
| 北京 | 实时价格 | ❌ 不支持 | ✅ 支持 | ✅ 支持 | ❌ 不支持 | 均支持 |
| 北京 | K线数据 | ❌ 不支持 | ✅ 支持 | ✅ 支持 | ❌ 不支持 | baostockdata历史更长 |
| 北京 | 分钟数据 | ❌ 不支持 | ✅ 支持 | ❌ 不支持 | ❌ 不支持 | 仅westockdata |
| 北京 | 财务报表 | ❌ 不支持 | ✅ 支持 | ✅ 支持 | ❌ 不支持 | 均支持 |
| 香港 | 实时价格 | ❌ 不支持 | ✅ 支持 | ❌ 不支持 | ✅ 支持 | yfinancedata优先 |
| 香港 | K线数据 | ❌ 不支持 | ✅ 支持 | ❌ 不支持 | ✅ 支持 | yfinancedata优先 |
| 香港 | 分钟数据 | ❌ 不支持 | ✅ 支持 | ❌ 不支持 | ✅ 支持 | yfinancedata优先 |
| 香港 | 财务报表 | ❌ 不支持 | ✅ 支持 | ❌ 不支持 | ✅ 支持 | yfinancedata优先 |
| 香港 | 资金流向 | ❌ 不支持 | ✅ 支持 | ❌ 不支持 | ❌ 不支持 | 仅westockdata |
| **美国** | **实时价格** | ❌ 不支持 | ❌ 不支持 | ❌ 不支持 | ✅ **支持 ⭐** | **yfinancedata专用** |
| **美国** | **K线数据** | ❌ 不支持 | ❌ 不支持 | ❌ 不支持 | ✅ **支持 ⭐** | **yfinancedata专用，20年+历史** |
| **美国** | **分钟数据** | ❌ 不支持 | ❌ 不支持 | ❌ 不支持 | ✅ **支持 ⭐** | **yfinancedata专用** |
| **美国** | **财务报表** | ❌ 不支持 | ❌ 不支持 | ❌ 不支持 | ✅ **支持 ⭐** | **yfinancedata专用，10年+历史** |
| **美国** | **期权数据** | ❌ 不支持 | ❌ 不支持 | ❌ 不支持 | ✅ **支持 ⭐** | **yfinancedata专用** |
| **美国** | **分析师预期** | ❌ 不支持 | ❌ 不支持 | ❌ 不支持 | ✅ **支持 ⭐** | **yfinancedata专用** |
| **美国** | **机构持仓** | ❌ 不支持 | ❌ 不支持 | ❌ 不支持 | ✅ **支持 ⭐** | **yfinancedata专用，13F报告** |

#### 2. 指数 (Index)

| 证券市场 | 数据类型 | crawldata | westockdata | baostockdata | yfinancedata | 说明 |
|---------|---------|----------|-------------|--------------|----------|------|
| 上海 | 实时行情 | ✅ 支持 | ✅ **支持 ⭐** | ❌ 不支持 | ❌ 不支持 | westockdata优先，全字段 |
| 上海 | K线数据 | ✅ 支持 | ✅ 支持 | ✅ 支持 | ❌ 不支持 | 均支持 |
| 深圳 | 实时行情 | ✅ 支持 | ✅ **支持 ⭐** | ❌ 不支持 | ❌ 不支持 | westockdata优先，全字段 |
| 深圳 | K线数据 | ✅ 支持 | ✅ 支持 | ✅ 支持 | ❌ 不支持 | 均支持 |
| 香港 | 实时行情 | ❌ 不支持 | ✅ 支持 | ❌ 不支持 | ✅ 支持 | yfinancedata优先 |
| 香港 | K线数据 | ❌ 不支持 | ✅ 支持 | ❌ 不支持 | ✅ 支持 | yfinancedata优先 |
| **美国** | **实时行情** | ❌ 不支持 | ❌ 不支持 | ❌ 不支持 | ✅ **支持 ⭐** | **yfinancedata专用** |
| **美国** | **K线数据** | ❌ 不支持 | ❌ 不支持 | ❌ 不支持 | ✅ **支持 ⭐** | **yfinancedata专用，全球指数** |
| **全球指数** | **实时行情** | ❌ 不支持 | ❌ 不支持 | ❌ 不支持 | ✅ **支持 ⭐** | **yfinancedata专用** |

#### 2.5. 期货 (Futures)

| 证券市场 | 数据类型 | crawldata | yfinancedata | okxdata | binancedata | 说明 |
|---------|---------|----------|--------------|----------|----------|------|
| **国际期货** | **实时价格** | ✅ **支持 ⭐** | ✅ 支持 | ⚠️ 支持 | ⚠️ 支持 | crawldata优先，黄金/原油/白银 |
| **国际期货** | K线数据 | ✅ 支持 | ✅ 支持 | ✅ 支持 | ✅ 支持 | yfinancedata优先 |

#### 3. 基金 (ETF/Fund)

| 证券市场 | 数据类型 | westockdata | baostockdata | yfinancedata | 说明 |
|---------|---------|-------------|--------------|----------|------|
| 上海 | 实时行情 | ✅ 支持 | ❌ 不支持 | ❌ 不支持 | 仅westockdata |
| 上海 | K线数据 | ✅ 支持 | ❌ 不支持 | ❌ 不支持 | 仅westockdata |
| 上海 | 持仓明细 | ✅ 支持 | ❌ 不支持 | ❌ 不支持 | 仅westockdata |
| 深圳 | 实时行情 | ✅ 支持 | ❌ 不支持 | ❌ 不支持 | 仅westockdata |
| 深圳 | K线数据 | ✅ 支持 | ❌ 不支持 | ❌ 不支持 | 仅westockdata |
| 深圳 | 持仓明细 | ✅ 支持 | ❌ 不支持 | ❌ 不支持 | 仅westockdata |
| 香港 | 实时行情 | ✅ 支持 | ❌ 不支持 | ✅ 支持 | yfinancedata优先 |
| 香港 | K线数据 | ✅ 支持 | ❌ 不支持 | ✅ 支持 | yfinancedata优先 |
| **美国ETF** | **实时行情** | ❌ 不支持 | ❌ 不支持 | ✅ **支持 ⭐** | **yfinancedata专用** |
| **美国ETF** | **K线数据** | ❌ 不支持 | ❌ 不支持 | ✅ **支持 ⭐** | **yfinancedata专用** |

#### 4. 其他资产类别 (yfinancedata专属)

| 资产类型 | 数据类型 | yfinancedata | 说明 |
|---------|---------|----------|------|
| **外汇** | 实时行情 | ✅ 支持 ⭐ | 货币对（EUR/USD等） |
| **外汇** | K线数据 | ✅ 支持 ⭐ | 历史数据 |
| **加密货币** | 实时行情 | ✅ 支持 ⭐ | BTC、ETH等 |
| **加密货币** | K线数据 | ✅ 支持 ⭐ | 历史数据 |
| **期货** | 实时行情 | ✅ 支持 ⭐ | 黄金、原油等 |
| **期货** | K线数据 | ✅ 支持 ⭐ | 历史数据 |

---

### 三级路由：按数据类型详细路由

#### A. 行情数据 (Quote)

| 数据类型 | 详细描述 | 路由目标 | 适用市场 |
|---------|---------|---------|---------|
| **实时价格** | 实时行情快照 | `westockdata` / `crawldata` / `yfinancedata` | A股、港股、美股、国际期货 |
| **当日行情** | 当日完整行情 | `westockdata` / `crawldata` / `yfinancedata` | A股、港股、美股、国际期货 |
| **盘口数据** | 买卖盘口 | `westockdata` / `crawldata` | A股、港股 |

#### B. K线数据 (Kline)

| 数据类型 | 详细描述 | 优先数据源 | 备选数据源 | 说明 |
|---------|---------|-----------|-----------|------|
| **日K线** | 日线数据 | `westockdata` | `crawldata` / `baostockdata` / `yfinancedata` | westockdata优先 |
| **周K线** | 周线数据 | `westockdata` | `crawldata` / `baostockdata` / `yfinancedata` | westockdata优先 |
| **月K线** | 月线数据 | `westockdata` | `crawldata` / `baostockdata` / `yfinancedata` | westockdata优先 |
| **5分钟K线** | 5分钟数据 | `westockdata` | `crawldata` / `yfinancedata` | westockdata实时性好 |
| **15分钟K线** | 15分钟数据 | `westockdata` | `yfinancedata` | westockdata实时性好 |
| **30分钟K线** | 30分钟数据 | `westockdata` | `yfinancedata` | westockdata实时性好 |
| **60分钟K线** | 60分钟数据 | `westockdata` | `yfinancedata` | westockdata实时性好 |
| **分时数据** | 盘中分时 | `westockdata` | --- | 仅westockdata支持 |
| **复权数据** | 前/后复权 | `baostockdata` | `westockdata` / `yfinancedata` | 均支持 |

#### C. 财务数据 (Financial)

| 数据类型 | 详细描述 | 优先数据源 | 备选数据源 | 说明 |
|---------|---------|-----------|-----------|------|
| **利润表** | 季度/年度利润 | `baostockdata` | `westockdata` / `yfinancedata` | baostockdata更完整 |
| **资产负债表** | 资产负债 | `baostockdata` | `westockdata` / `yfinancedata` | baostockdata更完整 |
| **现金流量表** | 现金流水 | `baostockdata` | `westockdata` / `yfinancedata` | baostockdata更完整 |
| **杜邦指标** | 财务综合 | `baostockdata` | --- | 仅baostockdata |
| **估值指标** | PE/PB/PS | `baostockdata` | `westockdata` / `yfinancedata` | 均支持 |

#### D. 资金数据 (Fund Flow)

| 数据类型 | 详细描述 | 路由目标 | 适用市场 |
|---------|---------|---------|---------|
| **A股资金流向** | 主力/大单/中单/小单 | `westockdata` | 仅A股 |
| **港股资金流向** | 南向资金等 | `westockdata` | 仅港股 |
| **美股卖空数据** | 卖空比例/数量 | `westockdata` | 仅美股 |
| **融资融券** | 融资余额/融券余额 | `westockdata` | 仅A股 |
| **龙虎榜** | 营业部买卖排行 | `westockdata` | 仅A股 |
| **大宗交易** | 大宗交易明细 | `westockdata` | 仅A股 |

#### E. 技术指标 (Technical)

| 数据类型 | 详细描述 | 路由目标 | 说明 |
|---------|---------|---------|------|
| **MACD** | 指数平滑异同移动平均线 | `westockdata` | 仅westockdata |
| **RSI** | 相对强弱指数 | `westockdata` | 仅westockdata |
| **KDJ** | 随机指标 | `westockdata` | 仅westockdata |
| **布林带** | BOLL指标 | `westockdata` | 仅westockdata |
| **均线系统** | MA5/MA10/MA20等 | `westockdata` | 仅westockdata |
| **乖离率** | BIAS指标 | `westockdata` | 仅westockdata |
| **威廉指标** | WR指标 | `westockdata` | 仅westockdata |
| **筹码成本** | 筹码分布 | `westockdata` | 仅A股 |

#### F. 基本面数据 (Fundamental)

| 数据类型 | 详细描述 | 优先数据源 | 备选数据源 | 说明 |
|---------|---------|-----------|-----------|------|
| **公司简况** | 基本信息 | `westockdata` | --- | 仅westockdata |
| **股东结构** | 十大股东/流通股东 | `westockdata` | --- | 仅westockdata |
| **分红数据** | 分红历史/方案 | `westockdata` | `baostockdata` / `yfinancedata` | 均支持 |
| **业绩预告** | 业绩预告 | `westockdata` | `baostockdata` | 均支持 |
| **业绩快报** | 业绩快报 | `westockdata` | `baostockdata` | 均支持 |

#### G. 特色数据 (Special)

| 数据类型 | 详细描述 | 路由目标 | 适用市场 |
|---------|---------|---------|---------|
| **热搜股票** | 搜索热度排行 | `westockdata` | A股 |
| **热门板块** | 板块热度排行 | `westockdata` | A股 |
| **投资日历** | 经济事件/财报发布 | `westockdata` | A股 |
| **新股日历** | 新股发行/上市 | `westockdata` | A股、港股 |
| **除权除息** | 分红除权日历 | `westockdata` | A股、港股 |
| **停复牌** | 停牌复牌信息 | `westockdata` | A股 |

#### H. 宏观经济数据 (Macro)

| 数据类型 | 详细描述 | 路由目标 | 说明 |
|---------|---------|---------|------|
| **CPI** | 消费者物价指数（同比/环比） | `macrodata ⭐` → `baostockdata` | macrodata 爬虫优先（东方财富） |
| **PPI** | 生产者物价指数 | `macrodata ⭐` → `baostockdata` | macrodata 爬虫优先 |
| **PMI** | 采购经理指数（制造业/非制造业） | `macrodata ⭐` | 东方财富/金十数据 |
| **GDP** | 国内生产总值（季度） | `macrodata ⭐` | 东方财富 |
| **LPR** | 贷款市场报价利率 | `macrodata ⭐` | 东方财富 |
| **M2/货币供应量** | M0/M1/M2 同比 | `macrodata ⭐` → `baostockdata` | macrodata 优先 |
| **社会融资规模** | 社融增量 | `macrodata ⭐` | 东方财富 |
| **工业增加值** | 规模以上工业增加值 | `macrodata ⭐` | 东方财富 |
| **外汇储备** | 国家外汇储备 | `macrodata ⭐` | 东方财富 |
| **进出口** | 海关进出口数据 | `macrodata ⭐` | 东方财富 |
| **存款利率** | 人民币存款基准利率 | `macrodata` → `baostockdata` | 双源 |
| **贷款利率** | 人民币贷款基准利率 | `macrodata` → `baostockdata` | 双源 |
| **存款准备金率** | 存款准备金率 | `macrodata` → `baostockdata` | 双源 |
| **美国非农** | 非农就业人数变化 | `macrodata ⭐` | 金十数据 |
| **美国CPI/PPI** | 美国通胀数据 | `macrodata ⭐` | 金十数据 |
| **美国失业率** | 美国失业率 | `macrodata ⭐` | 金十数据 |
| **美国ADP** | ADP就业人数 | `macrodata ⭐` | 金十数据 |
| **ISM PMI** | ISM制造业PMI | `macrodata ⭐` | 金十数据 |
| **经济日历** | 数据发布时间表 | `macrodata`（浏览器） | Trading Economics / FRED |
| **政策动态** | 央行/监管政策 | `macrodata`（浏览器） | 央行官网 / 财联社 |

---

## 路由决策算法

### 伪代码

```python
def route_request(market: str, security_type: str, data_type: str, max_retries=3) -> str:
    """
    路由决策算法（带重试）
    """
    
    # Step 1: 识别市场
    market_type = identify_market(market)  # sh/sz/hk/us/bj
    
    # Step 2: 识别数据类型
    data_category = identify_data_category(data_type)  # quote/kline/financial/fund/technical
    
    # Step 3: 查找路由规则
    skill = find_routing_rule(market_type, security_type, data_category)
    
    # Step 4-6: 尝试获取数据（带重试）
    for attempt in range(max_retries):
        try:
            # 验证数据源可用性
            if is_skill_available(skill):
                result = execute_query(skill, market_type, data_type)
                return {
                    'success': True,
                    'skill': skill,
                    'data': result,
                    'attempts': attempt + 1
                }
            else:
                # Step 5: 查找备选数据源
                backup_skill = find_backup_skill(market_type, security_type, data_category)
                if backup_skill and is_skill_available(backup_skill):
                    result = execute_query(backup_skill, market_type, data_type)
                    return {
                        'success': True,
                        'skill': backup_skill,
                        'data': result,
                        'attempts': attempt + 1,
                        'note': '使用备选数据源'
                    }
                    
        except (NetworkError, TimeoutError, ServerError) as e:
            if attempt < max_retries - 1:
                # 指数退避重试
                wait_time = 2 ** attempt
                time.sleep(wait_time)
                continue
            else:
                return {
                    'success': False,
                    'error': str(e),
                    'attempts': max_retries,
                    'fallback': '请稍后重试或检查网络连接'
                }
```

### 路由优先级规则

1. **实时数据优先**：`westockdata` 提供实时行情
2. **历史数据优先**：`baostockdata` 提供更长历史
3. **数据完整性优先**：选择数据更完整的数据源
4. **性能优先**：考虑查询速度和限制
5. **成本优先**：优先使用免费数据源

---

## 特殊路由场景

### 场景1：跨市场数据查询

**场景**：查询包含A股、港股、美股的资产组合

**路由策略**：
```
输入：用户持有[茅台, 腾讯, 苹果]
识别：
  - 茅台(600519) → 上海A股 → westockdata
  - 腾讯(00700) → 港股 → westockdata
  - 苹果(AAPL) → 美股 → yfinancedata
路由结果：全部路由到对应数据源
```

### 场景2：历史K线长周期查询

**场景**：查询某股票10年以上的日K线数据

**路由策略**：
```
输入：查询浦发银行1990-2024年日K线
识别：
  - 上海A股 → 支持
  - 日K线数据 → 支持
  - 长周期(34年) → 历史深度要求高
路由结果：
  - 优先：baostockdata（1990年至今）
  - 备选：westockdata（较短历史）
```

### 场景3：分钟线高频数据

**场景**：查询某股票日内5分钟K线

**路由策略**：
```
输入：查询招商银行今日5分钟K线
识别：
  - 上海A股 → 支持
  - 5分钟数据 → 日内高频
  - 实时性要求 → 高
路由结果：
  - 优先：westockdata（实时性好）
  - 备选：crawldata（支持5分钟K）
```

### 场景4：综合财务分析

**场景**：需要多年季度财务数据进行杜邦分析

**路由策略**：
```
输入：分析贵州茅台近5年杜邦指标
识别：
  - 财务数据 → 支持
  - 杜邦指标 → baostockdata专有
  - 多期数据 → 数据完整性要求高
路由结果：baostockdata（杜邦分析专用）
```

---

## 路由表速查

### 按数据类型速查

| 数据类型 | A股 | 港股 | 美股 | 国际期货 |
|---------|-----|------|------|---------|
| 实时行情 | westockdata | westockdata / yfinancedata | yfinancedata | crawldata |
| 日K线 | westockdata | yfinancedata | yfinancedata | yfinancedata |
| 分钟K线 | westockdata | yfinancedata | yfinancedata | yfinancedata |
| 财务报表 | baostockdata | yfinancedata | yfinancedata | - |
| 资金流向 | westockdata | westockdata | westockdata | - |
| 技术指标 | westockdata | westockdata | westockdata | - |
| 分红数据 | westockdata | westockdata | yfinancedata | - |
| 龙虎榜 | westockdata | ❌ | ❌ | - |
| 筹码成本 | westockdata | ❌ | ❌ | - |
| 股东结构 | westockdata | westockdata | yfinancedata | - |
| 宏观经济 | baostockdata | ❌ | ❌ | - |
| 期权数据 | ❌ | ❌ | yfinancedata | - |
| 分析师预期 | ❌ | ❌ | yfinancedata | - |

### 按子技能能力矩阵

| 功能 | crawldata | westockdata | baostockdata | yfinancedata |
|------|-----------|------------|--------------|------------------|
| **市场覆盖** | | | | |
| A股 | ✅ | ✅⭐ | ✅ | ⚠️ |
| 港股 | ❌ | ✅ | ❌ | ✅ |
| 美股 | ❌ | ⚠️ | ❌ | ✅⭐ |
| 国际期货 | ✅⭐ | ❌ | ❌ | ✅ |
| 外汇 | ❌ | ❌ | ❌ | ✅ |
| 加密货币 | ❌ | ❌ | ❌ | ✅ |
| **数据类型** | | | | |
| 实时行情 | ✅ | ✅⭐ | ❌ | ✅ |
| 买卖五档 | ✅ | ✅⭐ | ❌ | ✅ |
| 历史K线 | ✅ | ✅⭐ | ✅ | ✅ |
| 分钟数据 | ✅ | ✅⭐ | ✅ | ✅ |
| 财务报表 | ❌ | ✅ | ✅ | ✅ |
| 资金流向 | ❌ | ✅⭐ | ❌ | ❌ |
| 技术指标 | ❌ | ✅⭐ | ❌ | ❌ |
| 期权数据 | ❌ | ❌ | ❌ | ✅ |
| **数据深度** | | | | |
| 最早数据 | - | 较短 | 1990年⭐ | 20年+ |
| 财务历史 | - | 有限 | 2007年+ | 10年+ |
| **字段完整性** | | | | |
| 完整字段解析 | ✅ | ✅⭐ | ✅ | ✅ |
| 成交额/换手率 | ✅ | ✅⭐ | ✅ | ✅ |
| **重试机制** | | | | |
| 自动重试 | ✅ | ✅ | ✅ | ✅ |
| 最大重试次数 | 3次 | 3次 | 3次 | 3次 |

---

## 路由配置

### 子技能注册表

```yaml
skills:
  crawldata:
    path: crawldata
    enabled: true
    priority: 10
    markets: [sh, sz, futures]
    data_types: [quote, kline, tick, depth]
    retry:
      max_attempts: 3
      backoff: exponential
      initial_delay: 1s
      
  westockdata:
    path: westockdata
    enabled: true
    priority: 15
    markets: [sh, sz, bj, hk, us]
    data_types: [quote, kline, minute, financial, fund, technical]
    retry:
      max_attempts: 3
      backoff: exponential
      initial_delay: 1s
      
  baostockdata:
    path: baostockdata
    enabled: true
    priority: 5
    markets: [sh, sz, bj]
    data_types: [kline, minute, financial, dividend, macro]
    retry:
      max_attempts: 3
      backoff: exponential
      initial_delay: 1s
      
  yfinancedata:
    path: yfinancedata
    enabled: true
    priority: 8
    markets: [us, hk, global]
    data_types: [quote, kline, minute, financial, options, analyst]
    retry:
      max_attempts: 3
      backoff: exponential
      initial_delay: 1s

  macrodata:
    path: macrodata
    enabled: true
    priority: 6
    markets: [china_macro, us_macro, global_macro]
    data_types: [macro, economic_calendar, policy]
    retry:
      max_attempts: 3
      backoff: exponential
      initial_delay: 1s
```

### 路由规则优先级

```
1. 实时数据 → westockdata（A股）
2. 国际期货 → crawldata
3. 技术指标 → westockdata
4. 资金流向 → westockdata
5. 港股/美股 → yfinancedata
6. 宏观经济 → baostockdata
7. 杜邦分析 → baostockdata
8. 长周期K线 → baostockdata
9. A股K线 → westockdata（优先）
```

---

## 扩展指南

### 添加新数据源

1. 在 `quantdata/` 创建新的子技能目录
2. 编写符合规范的 SKILL.md
3. 在ROUNTING.md中添加路由规则
4. 更新子技能注册表
5. 配置重试机制

### 修改路由规则

在ROUNTING.md对应章节修改路由映射关系即可。

---

## 路由异常处理

### 重试机制配置

```yaml
retry_policy:
  max_attempts: 3          # 最大重试次数
  initial_delay: 1           # 初始延迟（秒）
  max_delay: 30              # 最大延迟（秒）
  backoff_factor: 2           # 退避因子
  retry_on:
    - network_error
    - timeout
    - server_error_5xx
    - rate_limit_429
  no_retry_on:
    - client_error_4xx
    - not_found_404
    - unauthorized_401
```

### 数据源不可用

```
场景：主数据源服务不可用
处理：
  1. 记录错误日志
  2. 尝试备用数据源
  3. 如备用也不可用，等待1秒后重试（最多3次）
  4. 返回错误信息和建议
```

### 数据缺失

```
场景：部分数据无法获取
处理：
  1. 标注缺失数据
  2. 返回可获取的数据
  3. 提供数据源说明
  4. 如整个数据源不可用，尝试重试3次后切换
```

---

## 版本历史

### v1.2.0 (2026-05-09)

- 新增：crawldata 支持K线数据（日K/周K/月K/5分钟K）
- 优化：调整优先级，westockdata 优先于 crawldata
- 更新：路由规则表中 westockdata 设为默认数据源
- 更新：子技能注册表调整优先级（westockdata 15, crawldata 10）
- 更新：K线数据路由添加 crawldata 作为备选

### v1.1.0 (2026-05-07)

- 新增：crawldata 腾讯财经爬虫数据源
- 新增：支持国际期货（黄金/原油/白银等）
- 优化：A股实时行情优先使用 crawldata
- 优化：完整字段解析（买卖五档、成交量、成交额、换手率等）
- 更新：路由规则表添加 crawldata 优先级
- 更新：子技能能力矩阵扩展

### v1.0.0 (2026-05-06)

- 初始版本
- 支持 westockdata、baostockdata 和 yfinancedata 三个数据源
- 完整的路由规则表
- 路由决策算法说明
- 特殊场景处理
- **新增：自动重试机制（3次，指数退避）**
- **新增：备选数据源自动切换**

---

## 联系方式

如有问题或建议，请联系 QuantData 开发团队。

---

**免责声明**：数据仅供参考，不构成投资建议。投资有风险，决策需谨慎。
