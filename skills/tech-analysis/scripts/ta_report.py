#!/usr/bin/env python3
"""技术分析综合报告生成器。

整合 7 大技术分析引擎，对指定标的生成综合技术面报告。
支持加密货币、A股、美股、期货等多市场。

数据来源:
  --csv FILE         从本地 CSV 文件加载 (推荐，离线可用)
  --exchange ccxt    通过 ccxt 在线获取 (加密货币)
  --exchange akshare 通过 akshare 在线获取 (A股)
  --exchange yfinance 通过 yfinance 在线获取 (美股)

CSV 数据准备 (以 CCXT 为例):
  python ccxt_data.py kline BTC/USDT -e okx -t 1d -l 200 > btc_usdt.csv
  python ta_report.py --csv btc_usdt.csv BTC/USDT

引擎列表:
1. K线形态 (candlestick)  — 15 种经典蜡烛图形态
2. 缠论 (chanlun)         — 分型→笔→中枢→买卖点
3. 艾略特波浪 (elliott-wave) — 5 浪推动 + 3 浪调整
4. 谐波形态 (harmonic)     — Gartley/Bat/Butterfly/Crab XABCD 五点形态
5. 一目均衡 (ichimoku)     — 五线系统 + 云带过滤
6. SMC/ICT (smc)          — BOS/ChoCH 结构突破 + FVG 缺口
7. 基础指标 (technical-basic) — EMA/RSI/BB/ADX/OBV 投票

信号约定: 1=做多, -1=做空, 0=观望
"""

import argparse
import os
import sys
from typing import Dict, List, Optional

import numpy as np
import pandas as pd

# 本地引擎目录（engines/ 与 scripts/ 同级）
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
ENGINES_DIR = os.path.join(os.path.dirname(SCRIPT_DIR), "engines")
sys.path.insert(0, ENGINES_DIR)

ENGINE_NAMES = [
    "candlestick", "chanlun", "elliott_wave", "harmonic",
    "ichimoku", "smc", "technical_basic",
]

ENGINE_DESCRIPTIONS = {
    "candlestick": "K线形态",
    "chanlun": "缠论",
    "elliott_wave": "艾略特波浪",
    "harmonic": "谐波形态",
    "ichimoku": "一目均衡",
    "smc": "SMC/ICT",
    "technical_basic": "基础指标",
}


def load_engines(names: Optional[List[str]] = None) -> Dict[str, object]:
    """动态加载信号引擎"""
    if names is None:
        names = ENGINE_NAMES

    engines = {}
    for name in names:
        try:
            mod = __import__(name)
            engines[name] = mod.SignalEngine()
        except Exception as e:
            print(f"⚠ 加载引擎 {name} 失败: {e}", file=sys.stderr)
    return engines


def run_engines(engines: Dict[str, object], data_map: Dict[str, pd.DataFrame]) -> Dict[str, Dict[str, pd.Series]]:
    """对每个标的运行所有引擎"""
    results = {}
    for engine_name, engine in engines.items():
        try:
            signals = engine.generate(data_map)
            results[engine_name] = signals
        except Exception as e:
            print(f"⚠ 引擎 {engine_name} 运行失败: {e}", file=sys.stderr)
    return results


def compute_key_levels(df: pd.DataFrame) -> dict:
    """计算关键价位"""
    c = df["close"]
    return {
        "price": float(c.iloc[-1]),
        "high_7d": float(df["high"].tail(7).max()),
        "low_7d": float(df["low"].tail(7).min()),
        "high_30d": float(df["high"].tail(30).max()),
        "low_30d": float(df["low"].tail(30).min()),
        "pct_chg_7d": float((c.iloc[-1] / c.iloc[-8] - 1) * 100) if len(c) > 7 else 0,
        "pct_chg_30d": float((c.iloc[-1] / c.iloc[-31] - 1) * 100) if len(c) > 30 else 0,
    }


def aggregate_signal(results: Dict[str, Dict[str, pd.Series]],
                     symbol: str) -> tuple:
    """聚合所有引擎的最新信号"""
    votes = []
    details = []
    for engine_name, signals in results.items():
        if symbol in signals:
            sig = signals[symbol].iloc[-1]
            votes.append(int(sig))
            label = "做多 🟢" if sig == 1 else ("做空 🔴" if sig == -1 else "观望 ⚪")
            details.append((ENGINE_DESCRIPTIONS.get(engine_name, engine_name), label, sig))

    if not votes:
        return 0, []

    score = sum(votes)
    final = 1 if score > 0 else (-1 if score < 0 else 0)
    return final, details


def format_report(symbol: str, exchange: str, timeframe: str,
                  results: Dict[str, Dict[str, pd.Series]],
                  levels: dict) -> str:
    """格式化分析报告"""
    price = levels["price"]
    chg7 = levels["pct_chg_7d"]
    chg30 = levels["pct_chg_30d"]

    final, details = aggregate_signal(results, symbol)

    lines = []
    lines.append(f"📊 技术分析报告 | {symbol} ({exchange.upper()})")
    lines.append(f"⏰ 周期: {timeframe} | 💰 价格: {price:,.2f}")
    lines.append(f"📈 7日: {chg7:+.2f}% | 30日: {chg30:+.2f}%")
    lines.append("")

    # 关键价位
    lines.append("📍 关键价位:")
    lines.append(f"  7日区间: {levels['low_7d']:,.2f} ~ {levels['high_7d']:,.2f}")
    lines.append(f" 30日区间: {levels['low_30d']:,.2f} ~ {levels['high_30d']:,.2f}")
    lines.append("")

    # 各引擎信号
    lines.append("🔬 引擎信号:")
    for name, label, _ in details:
        lines.append(f"  {name}: {label}")

    # 综合判定
    lines.append("")
    if final == 1:
        lines.append("✅ 综合判定: 偏多 — 多数引擎看涨")
    elif final == -1:
        lines.append("❌ 综合判定: 偏空 — 多数引擎看跌")
    else:
        lines.append("⚪ 综合判定: 中性 — 信号分歧或无明确方向")

    lines.append("")
    lines.append("⚠ 以上为技术面参考，不构成投资建议。")

    return "\n".join(lines)


# ── 数据获取 ──

# CSV 列名映射：支持多种常见格式自动识别
CSV_COLUMN_MAP = {
    # 英文标准
    "date": "timestamp", "time": "timestamp", "datetime": "timestamp",
    "open": "open", "high": "high", "low": "low", "close": "close",
    "vol": "volume", "volume": "volume",
    # 中文 (Baostock / akshare / 东方财富 常见列名)
    "日期": "timestamp", "时间": "timestamp", "date": "timestamp",
    "开盘": "open", "开盘价": "open", "开盘价格": "open",
    "最高": "high", "最高价": "high", "最高价格": "high",
    "最低": "low", "最低价": "low", "最低价格": "low",
    "收盘": "close", "收盘价": "close", "收盘价格": "close",
    "成交量": "volume", "成交额": "amount",
    "昨收": "preclose", "昨收价": "preclose", "昨结": "preclose",
    "涨跌额": "change", "涨跌幅": "pct_chg",
    "换手率": "turnover",
    # ccxt_data.py 输出格式
    "timestamp,open,high,low,close,volume": None,  # 已是标准格式，跳过
}


def load_csv(filepath: str) -> pd.DataFrame:
    """从本地 CSV 文件加载 OHLCV 数据。

    自动识别:
      - 有/无表头
      - 英文/中文列名
      - ccxt_data.py / baostock.py / akshare 输出格式
      - 日期索引或普通列
    """
    if not os.path.isfile(filepath):
        raise FileNotFoundError(f"CSV 文件不存在: {filepath}")

    # 尝试多种编码
    for enc in ("utf-8", "utf-8-sig", "gbk", "gb2312", "latin-1"):
        try:
            df = pd.read_csv(filepath, encoding=enc, nrows=5)
            break
        except (UnicodeDecodeError, pd.errors.ParserError):
            continue
    else:
        raise ValueError(f"无法解码 CSV 文件: {filepath}")

    # 重新读取全部数据
    df = pd.read_csv(filepath, encoding=enc)

    # 标准化列名
    col_map = {}
    for col in df.columns:
        normalized = col.strip().lower()
        if normalized in CSV_COLUMN_MAP and CSV_COLUMN_MAP[normalized] is not None:
            col_map[col] = CSV_COLUMN_MAP[normalized]
    df.rename(columns=col_map, inplace=True)

    # 如果没有 timestamp 列，尝试用第一列
    if "timestamp" not in df.columns:
        first_col = df.columns[0]
        # 尝试解析为日期
        try:
            pd.to_datetime(df[first_col].head(3))
            df.rename(columns={first_col: "timestamp"}, inplace=True)
        except (ValueError, TypeError):
            pass

    # 设置索引
    if "timestamp" in df.columns:
        df["timestamp"] = pd.to_datetime(df["timestamp"], errors="coerce")
        df.dropna(subset=["timestamp"], inplace=True)
        df.set_index("timestamp", inplace=True)
        df.sort_index(inplace=True)

    # 确保有必要列
    required = ["open", "high", "low", "close"]
    missing = [c for c in required if c not in df.columns]
    if missing:
        raise ValueError(f"CSV 缺少必要列: {missing}。现有列: {list(df.columns)}")

    # volume 可选
    if "volume" not in df.columns:
        df["volume"] = 0.0

    # 清洗数值
    for col in ["open", "high", "low", "close", "volume"]:
        df[col] = pd.to_numeric(df[col], errors="coerce")
    df.dropna(subset=["open", "high", "low", "close"], inplace=True)

    return df[["open", "high", "low", "close", "volume"]]


def fetch_data(symbol: str, exchange: str = "binance", timeframe: str = "1d",
               limit: int = 200, proxy: str = None) -> pd.DataFrame:
    """获取 OHLCV 数据"""
    symbol_upper = symbol.upper().replace("-", "/")

    # 加密货币通过 ccxt
    if exchange in ("binance", "okx", "bybit", "gate", "htx", "kucoin", "bitget"):
        try:
            import ccxt
            config = {"enableRateLimit": True}
            if proxy:
                config["proxies"] = {"http": proxy, "https": proxy}
            ex_class = getattr(ccxt, exchange)
            ex = ex_class(config)
            ohlcv = ex.fetch_ohlcv(symbol_upper, timeframe=timeframe, limit=limit)
            df = pd.DataFrame(ohlcv, columns=["timestamp", "open", "high", "low", "close", "volume"])
            df["timestamp"] = pd.to_datetime(df["timestamp"], unit="ms")
            df.set_index("timestamp", inplace=True)
            return df
        except Exception as e:
            print(f"ccxt 获取失败: {e}", file=sys.stderr)

    # CoinGecko 作为加密货币 fallback
    if exchange in ("binance", "okx", "coingecko") and "/" in symbol_upper:
        try:
            import requests
            coin_id = symbol_upper.split("/")[0].lower()
            url = f"https://api.coingecko.com/api/v3/coins/{coin_id}/ohlc"
            params = {"vs_currency": "usd", "days": limit}
            resp = requests.get(url, params=params, timeout=15)
            resp.raise_for_status()
            data = resp.json()
            df = pd.DataFrame(data, columns=["timestamp", "open", "high", "low", "close"])
            df["timestamp"] = pd.to_datetime(df["timestamp"], unit="ms")
            df.set_index("timestamp", inplace=True)
            df["volume"] = 0.0
            return df.tail(limit)
        except Exception as e:
            print(f"CoinGecko 获取失败: {e}", file=sys.stderr)

    # A股通过 akshare
    if exchange == "akshare":
        try:
            import akshare as ak
            code = symbol.split(".")[0] if "." in symbol else symbol
            df = ak.stock_zh_a_hist(symbol=code, period="daily", adjust="qfq")
            df = df.rename(columns={
                "日期": "timestamp", "开盘": "open", "最高": "high",
                "最低": "low", "收盘": "close", "成交量": "volume"
            })
            df["timestamp"] = pd.to_datetime(df["timestamp"])
            df.set_index("timestamp", inplace=True)
            return df[["open", "high", "low", "close", "volume"]].tail(limit)
        except Exception as e:
            print(f"akshare 获取失败: {e}", file=sys.stderr)

    # 美股通过 yfinance
    if exchange == "yfinance":
        try:
            import yfinance as yf
            ticker = yf.Ticker(symbol)
            df = ticker.history(period="6mo", interval=timeframe)
            df = df.rename(columns={
                "Open": "open", "High": "high", "Low": "low",
                "Close": "close", "Volume": "volume"
            })
            return df[["open", "high", "low", "close", "volume"]].tail(limit)
        except Exception as e:
            print(f"yfinance 获取失败: {e}", file=sys.stderr)

    raise RuntimeError(f"无法从 {exchange} 获取 {symbol} 的数据")


# ── CLI ──

def main():
    parser = argparse.ArgumentParser(
        description="技术分析综合报告",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
数据来源示例:
  # 从本地 CSV 分析 (推荐，离线可用)
  %(prog)s --csv data.csv BTC/USDT
  %(prog)s --csv 002050.csv 002050

  # 先下载 CSV 再分析 (CCXT 加密货币)
  ccxt_data.py kline BTC/USDT -e okx -t 1d -l 200 > btc.csv
  %(prog)s --csv btc.csv BTC/USDT

  # 先下载 CSV 再分析 (Baostock A股)
  baostock.py kline sz.002050 --start 2025-01-01 > 002050.csv
  %(prog)s --csv 002050.csv 002050

  # 在线获取 (需网络)
  %(prog)s BTC/USDT -e okx
  %(prog)s 002050 -e akshare
  %(prog)s AAPL -e yfinance
        """)
    parser.add_argument("symbol", nargs="?", help="标的代码，如 BTC/USDT, 002050, AAPL")
    parser.add_argument("--csv", "-c", metavar="FILE",
                        help="从本地 CSV 文件加载数据 (支持中英文列名自动识别)")
    parser.add_argument("--exchange", "-e", default="binance",
                        help="交易所: binance/okx/bybit/akshare/yfinance (默认 binance)")
    parser.add_argument("--timeframe", "-t", default="1d",
                        help="K线周期: 1m/5m/15m/1h/4h/1d/1w (默认 1d)")
    parser.add_argument("--limit", "-n", type=int, default=200,
                        help="K线数量 (默认 200)")
    parser.add_argument("--engines", nargs="*",
                        help="指定引擎，默认全部。可选: candlestick chanlun elliott_wave harmonic ichimoku smc technical_basic")
    parser.add_argument("--list-engines", action="store_true",
                        help="列出所有可用引擎")
    parser.add_argument("--proxy", "-p", default=None,
                        help="HTTP(S) 代理，如 http://127.0.0.1:7890")
    args = parser.parse_args()

    if args.list_engines:
        print("可用引擎:")
        for name in ENGINE_NAMES:
            desc = ENGINE_DESCRIPTIONS[name]
            print(f"  {name:20s} {desc}")
        return

    if not args.symbol:
        parser.error("请提供标的代码，如 BTC/USDT")

    # 加载引擎
    engines = load_engines(args.engines)
    if not engines:
        print("❌ 无可用引擎", file=sys.stderr)
        sys.exit(1)

    # 数据获取：优先 CSV，否则在线获取
    if args.csv:
        print(f"📂 从 CSV 加载: {args.csv}")
        df = load_csv(args.csv)
        print(f"✅ 加载 {len(df)} 根K线 | {df.index[0]} ~ {df.index[-1]}")
    else:
        print(f"⏳ 获取 {args.symbol} 数据 ({args.exchange}, {args.timeframe})...")
        df = fetch_data(args.symbol, args.exchange, args.timeframe, args.limit, proxy=args.proxy)
        print(f"✅ 获取 {len(df)} 根K线")

    data_map = {args.symbol: df}
    print(f"⏳ 运行 {len(engines)} 个引擎...")
    results = run_engines(engines, data_map)

    levels = compute_key_levels(df)
    report = format_report(args.symbol, args.exchange, args.timeframe, results, levels)
    print()
    print(report)


if __name__ == "__main__":
    main()
