# Broker Manager - 券商交易管理

统一券商交易管理系统，支持富途牛牛、OKX、Binance三大券商/交易所的交易接口。

## 支持的券商/交易所

| 券商/交易所 | 类型 | 支持功能 |
|-----------|------|---------|
| 富途牛牛 | 港股/美股/A股 | 完整交易功能 |
| OKX | 加密货币 | 现货/合约交易 |
| Binance | 加密货币 | 现货/合约交易 |

---

## 核心功能函数

### 1. `get_account_list()` - 获取账户列表

获取所有已配置的券商账户列表。

```python
from broker_manager import BrokerManager

# 初始化
manager = BrokerManager()

# 获取账户列表
accounts = manager.get_account_list()

# 返回数据示例
for account in accounts:
    print(f"券商: {account['broker']}, 账户ID: {account['account_id']}, 状态: {account['status']}")
```

**返回数据字段**：
- `broker`: 券商名称 (futu/okx/binance)
- `account_id`: 账户ID
- `status`: 账户状态 (normal/locked/disconnected)
- `account_type`: 账户类型 (cash/margin)
- `currency`: 计价货币

---

### 2. `get_account_info()` - 获取账户信息

获取指定账户的详细信息（余额、可用资金、持仓等）。

```python
# 获取账户信息
account_info = manager.get_account_info(
    broker="futu",
    account_id="12345678"
)

# 返回示例
print(f"总资产: {account_info['total_assets']}")
print(f"可用资金: {account_info['available_funds']}")
print(f"持仓市值: {account_info['market_value']}")
```

**富途参数**：
```python
# 富途账户信息
account_info = manager.get_account_info(
    broker="futu",
    market="HK"  # 市场：HK/US/CN
)
```

**OKX/Binance参数**：
```python
# OKX账户信息
account_info = manager.get_account_info(
    broker="okx",
    account_type="SPOT"  # SPOT/ SWAP
)
```

---

### 3. `get_positions()` - 获取当前持仓

获取当前账户的持仓明细。

```python
# 获取持仓
positions = manager.get_positions(
    broker="futu",
    account_id="12345678"
)

# 返回示例
for pos in positions:
    print(f"代码: {pos['symbol']}, 数量: {pos['quantity']}, 浮盈: {pos['unrealized_pnl']}")
```

**持仓数据字段**：
- `symbol`: 标的代码
- `quantity`: 持仓数量
- `available`: 可用数量
- `cost_price`: 成本价
- `market_price`: 现价
- `unrealized_pnl`: 未实现盈亏
- `pnl_ratio`: 盈亏比例
- `market_value`: 市值

---

### 4. `place_order()` - 下单

创建新订单。

```python
# 限价单买入
order = manager.place_order(
    broker="futu",
    account_id="12345678",
    symbol="HK.00700",  # 腾讯
    side="buy",
    order_type="limit",
    price=350.0,
    quantity=100
)

# 市价单卖出
market_order = manager.place_order(
    broker="binance",
    symbol="BTCUSDT",
    side="sell",
    order_type="market",
    quantity=0.01
)
```

**参数说明**：
| 参数 | 必填 | 说明 |
|------|------|------|
| `broker` | 是 | 券商名称 |
| `account_id` | 否 | 账户ID |
| `symbol` | 是 | 标的代码 |
| `side` | 是 | 买卖方向 buy/sell |
| `order_type` | 是 | 订单类型 limit/market |
| `price` | 限价单必填 | 委托价格 |
| `quantity` | 是 | 委托数量 |

---

### 5. `modify_order()` - 修改订单

修改未成交的订单。

```python
# 修改订单
result = manager.modify_order(
    broker="futu",
    account_id="12345678",
    order_id="123456789",
    price=345.0,  # 新价格
    quantity=200  # 新数量
)
```

**注意**：
- 仅可修改未成交订单
- 部分成交后不可修改

---

### 6. `order_list_query()` - 当日委托查询

查询当日委托订单。

```python
# 查询当日订单
orders = manager.order_list_query(
    broker="futu",
    account_id="12345678",
    symbol="HK.00700"  # 可选，筛选标的
)

# 返回示例
for order in orders:
    print(f"订单号: {order['order_id']}, 状态: {order['status']}, 成交: {order['filled_qty']}")
```

**订单状态**：
- `submitted`: 已报单
- `filled`: 完全成交
- `partially_filled`: 部分成交
- `cancelled`: 已撤销
- `rejected`: 被拒绝
- `expired`: 过期

---

### 7. `history_order_list_query()` - 历史委托查询（昨天以前）

查询历史委托订单（昨天及以前的订单）。

```python
# 查询历史订单
history_orders = manager.history_order_list_query(
    broker="futu",
    account_id="12345678",
    start_date="2024-01-01",
    end_date="2024-12-31"
)
```

**注意**：
- 不同券商历史数据保留时间不同
- OKX/Binance历史订单查询时间有限制

---

### 8. `order_fee_query()` - 查询订单费用

查询订单的费用明细。

```python
# 查询订单费用
fee_info = manager.order_fee_query(
    broker="futu",
    account_id="12345678",
    order_id="123456789"
)

# 返回示例
print(f"佣金: {fee_info['commission']}")
print(f"印花税: {fee_info['stamp_tax']}")
print(f"交易费: {fee_info['trade_fee']}")
```

**费用字段**：
| 费用 | 说明 |
|------|------|
| `commission` | 佣金 |
| `stamp_tax` | 印花税（仅香港） |
| `trade_fee` | 交易费 |
| `settlement_fee` | 结算费 |
| `platform_fee` | 平台费 |

---

### 9. `deal_list_query()` - 当日成交查询

查询当日成交明细。

```python
# 查询当日成交
deals = manager.deal_list_query(
    broker="futu",
    account_id="12345678",
    symbol="HK.00700"
)

# 返回示例
for deal in deals:
    print(f"成交时间: {deal['deal_time']}, 价格: {deal['price']}, 数量: {deal['quantity']}")
```

---

### 10. `history_deal_list_query()` - 历史成交查询

查询历史成交明细（昨天以前）。

```python
# 查询历史成交
history_deals = manager.history_deal_list_query(
    broker="futu",
    account_id="12345678",
    start_date="2024-01-01",
    end_date="2024-12-31"
)
```

---

## 券商代码格式

### 富途牛牛代码格式

| 市场 | 格式 | 示例 |
|------|------|------|
| 港股 | HK.XXXX | HK.00700 |
| 美股 | US.XXXX | US.AAPL |
| A股 | SH.XXXX / SZ.XXXX | SH.600000 |

### OKX/Binance代码格式

| 类型 | 格式 | 示例 |
|------|------|------|
| 现货 | XXXXUSDT | BTCUSDT |
| 永续合约 | XXXX-USDT-SWAP | BTC-USDT-SWAP |

---

## 配置文件

```yaml
brokers:
  futu:
    api_key: "your_futu_api_key"
    host: "127.0.0.1"
    port: 11111
    paper_trading: false
    
  okx:
    api_key: "your_okx_api_key"
    secret_key: "your_okx_secret"
    passphrase: "your_passphrase"
    simulation: false
    
  binance:
    api_key: "your_binance_key"
    secret: "your_binance_secret"
    testnet: true
```

---

## 完整使用示例

```python
from broker_manager import BrokerManager

# 初始化
manager = BrokerManager()

# 1. 获取账户列表
accounts = manager.get_account_list()

# 2. 获取富途账户信息
futu_info = manager.get_account_info(broker="futu", account_id="123456")

# 3. 查看持仓
positions = manager.get_positions(broker="futu", account_id="123456")

# 4. 下单
order = manager.place_order(
    broker="futu",
    account_id="123456",
    symbol="HK.00700",
    side="buy",
    order_type="limit",
    price=350.0,
    quantity=100
)
print(f"订单创建成功: {order['order_id']}")

# 5. 查看当日订单
today_orders = manager.order_list_query(broker="futu", account_id="123456")

# 6. 查看当日成交
today_deals = manager.deal_list_query(broker="futu", account_id="123456")

# 7. 查询历史订单（昨天以前）
yesterday_orders = manager.history_order_list_query(
    broker="futu",
    account_id="123456",
    start_date="2024-01-01",
    end_date="2024-12-30"
)
```

---

## 注意事项

⚠️ **风险提示**：
- 实盘交易请先在模拟盘测试
- 建议开启IP白名单和API权限限制
- 妥善保管API Key，不要泄露

---

## 相关技能

- [quantdata](../quantdata/SKILL.md) - 行情数据管理
- [futuopendata](../quantdata/futuopendata/SKILL.md) - 富途OpenAPI
- [okxdata](../quantdata/okxdata/SKILL.md) - OKX交易API
- [binancedata](../quantdata/binancedata/SKILL.md) - Binance交易API
