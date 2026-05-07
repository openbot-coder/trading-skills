# Trading Skills - 交易技能库

一个完整的量化交易技能库，提供多市场数据查询和交易管理功能。

## 📚 目录

- [项目简介](#项目简介)
- [功能特性](#功能特性)
- [项目结构](#项目结构)
- [快速开始](#快速开始)
- [子技能说明](#子技能说明)
- [贡献指南](#贡献指南)

## 项目简介

Trading Skills 是一个基于 Agent Skills 规范构建的量化交易工具集，旨在提供统一的数据查询和交易管理接口，支持多个市场和交易所。

## 功能特性

### 🔌 数据源

| 市场 | 数据源 | 状态 |
|------|--------|------|
| **A股** | Baostock / 富途牛牛 / Westock | ✅ |
| **港股** | 富途牛牛 / Westock | ✅ |
| **美股** | Yahoo Finance / 富途牛牛 / Westock | ✅ |
| **加密货币** | CoinGecko / OKX / Binance | ✅ |

### 📊 数据类型

- 实时行情 / K线 / 分时数据
- 财务报表 / 基本面数据
- 资金流向 / 技术指标
- 期权 / 期货 / 衍生品
- 宏观经济数据

### 💼 交易管理

- 多账户管理
- 实时持仓查询
- 订单管理（下单/撤单/改单）
- 成交记录查询
- 历史订单查询

## 项目结构

```
trading-skills/
├── quantdata/                 # 量化数据路由中心
│   ├── SKILL.md              # 主技能文档
│   ├── ROUNTING.md           # 数据路由规则
│   ├── README_SCRIPTS.md     # CLI 脚本使用说明
│   ├── westockdata/          # Westock 数据源
│   ├── baostockdata/         # Baostock A股数据源
│   ├── yfinancedata/         # Yahoo Finance 数据源
│   ├── futuopendata/         # 富途 OpenAPI
│   ├── coingeckodata/        # CoinGecko 加密货币
│   ├── okxdata/              # OKX 交易所
│   └── binancedata/          # Binance 交易所
└── broker-manager/           # 券商管理中心
    └── SKILL.md              # 交易管理技能文档
```

## 快速开始

### 前置要求

```bash
# 基础依赖
pip install requests

# 可选依赖
pip install yfinance pandas    # Yahoo Finance
pip install baostock          # A股数据
```

### 基础使用

#### 1. 查询股票价格

```bash
# Yahoo Finance
python quantdata/yfinancedata/scripts/yfinance.py price AAPL

# 富途牛牛 (需要安装OpenAPI)
python quantdata/futuopendata/futuapi/scripts/quote/get_stock_quote.py
```

#### 2. 查询加密货币

```bash
# CoinGecko
python quantdata/coingeckodata/scripts/coingecko.py price bitcoin

# OKX
python quantdata/okxdata/scripts/okx.py ticker BTC-USDT

# Binance
python quantdata/binancedata/scripts/binance.py ticker BTCUSDT
```

#### 3. 查询A股数据

```bash
# Baostock
python quantdata/baostockdata/scripts/baostock.py kline sh.600000
```

### 综合示例

```bash
# 查询 AAPL 股票信息
python quantdata/yfinancedata/scripts/yfinance.py info AAPL

# 查询 BTC 价格和市值排行
python quantdata/coingeckodata/scripts/coingecko.py top --top 10

# 完整文档
# quantdata/README_SCRIPTS.md
```

## 子技能说明

### quantdata - 量化数据路由中心

量化数据查询的统一入口，自动路由到合适的数据源。

**特性：**
- 智能数据路由
- 多数据源自动切换
- 统一数据格式
- 内置重试机制

**详细文档：** [quantdata/SKILL.md](quantdata/SKILL.md)

### broker-manager - 券商管理中心

多券商交易管理，支持富途牛牛/OKX/Binance。

**功能：**
- 账户信息查询
- 实时持仓
- 订单管理
- 成交记录
- 历史数据

**详细文档：** [broker-manager/SKILL.md](broker-manager/SKILL.md)

### 子技能列表

| 子技能 | 路径 | 市场 | 说明 |
|--------|------|------|------|
| **westockdata** | [quantdata/westockdata/](quantdata/westockdata/) | A股/港股/美股 | 腾讯自选股数据 |
| **baostockdata** | [quantdata/baostockdata/](quantdata/baostockdata/) | A股 | 开源A股数据接口 |
| **yfinancedata** | [quantdata/yfinancedata/](quantdata/yfinancedata/) | 美股/全球 | Yahoo Finance数据 |
| **futuopendata** | [quantdata/futuopendata/](quantdata/futuopendata/) | 港股/美股/A股 | 富途OpenAPI |
| **coingeckodata** | [quantdata/coingeckodata/](quantdata/coingeckodata/) | 加密货币 | 免费加密货币API |
| **okxdata** | [quantdata/okxdata/](quantdata/okxdata/) | 加密货币 | OKX交易所 |
| **binancedata** | [quantdata/binancedata/](quantdata/binancedata/) | 加密货币 | Binance交易所 |

## 贡献指南

欢迎提交 Issue 和 Pull Request！

### 新增数据源

1. 在 `quantdata/` 下创建新的技能目录
2. 编写符合规范的 `SKILL.md`
3. 在 `quantdata/ROUNTING.md` 中添加路由规则
4. 在 `quantdata/SKILL.md` 中更新子技能列表
5. 提供示例 CLI 脚本

### 代码规范

- 遵循 Agent Skills 规范
- 提供清晰的文档
- 包含使用示例
- 添加错误处理和重试机制

## ⚠️ 免责声明

本项目仅供学习和研究使用，不构成任何投资建议。使用本工具产生的任何投资损失，项目作者不承担责任。请谨慎投资！

## 📄 许可证

详见项目文件。

## 📞 联系我们

如有问题或建议，欢迎提交 Issue。

---

**Happy Trading!** 🎉
