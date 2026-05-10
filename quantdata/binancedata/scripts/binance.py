#!/usr/bin/env python3
"""
Binance 交易行情查询脚本

使用方式:
    # 最新价格
    python binance.py ticker BTCUSDT

    # K线历史
    python binance.py kline BTCUSDT --interval 1d --limit 100

所有命令都可以用 --help 查看详细用法
"""

import os
import time
import logging
import argparse
from functools import wraps
from datetime import datetime
from typing import Optional

try:
    import requests
except ImportError:
    print("请先安装: pip install requests")
    exit(1)

API_BASE = os.getenv("BINANCE_API_BASE", "https://api.binance.com")
DEFAULT_TIMEOUT = 10

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def retry(max_attempts: int = 3, delay: float = 1.0):
    """重试装饰器"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            last_exception = None
            for attempt in range(max_attempts):
                try:
                    return func(*args, **kwargs)
                except requests.RequestException as e:
                    last_exception = e
                    if attempt < max_attempts - 1:
                        logger.warning(f"请求失败 (尝试 {attempt + 1}/{max_attempts}): {e}")
                        time.sleep(delay)
                    else:
                        logger.error(f"请求最终失败: {e}")
            raise last_exception
        return wrapper
    return decorator


def format_price(price_str: Optional[str], decimals: int = 2) -> str:
    """格式化价格"""
    if not price_str:
        return "N/A"
    try:
        return f"{float(price_str):,.{decimals}f}"
    except (ValueError, TypeError):
        return price_str


def format_volume(vol_str: Optional[str]) -> str:
    """格式化成交量"""
    if not vol_str:
        return "N/A"
    try:
        return f"{float(vol_str):,.0f}"
    except (ValueError, TypeError):
        return vol_str


@retry(max_attempts=3, delay=1.0)
def _fetch_ticker(symbol: str) -> dict:
    """获取 ticker 数据（带重试）"""
    url = f"{API_BASE}/api/v3/ticker/24hr"
    params = {"symbol": symbol}
    response = requests.get(url, params=params, timeout=DEFAULT_TIMEOUT)
    response.raise_for_status()
    return response.json()


def ticker(symbols):
    """获取最新价格"""
    if not isinstance(symbols, list):
        symbols = [symbols]

    for symbol in symbols:
        try:
            data = _fetch_ticker(symbol)

            print("\n" + "="*80)
            print(f"  {symbol}")
            print("="*80)
            print(f"    最新价格: {format_price(data.get('lastPrice'))}")
            print(f"    24h开盘: {format_price(data.get('openPrice'))}")
            print(f"    24h最高: {format_price(data.get('highPrice'))}")
            print(f"    24h最低: {format_price(data.get('lowPrice'))}")
            print(f"    24h成交量: {format_volume(data.get('volume'))}")
            print(f"    24h成交额: {format_volume(data.get('quoteVolume'))}")
            pct_chg = data.get('priceChangePercent')
            if pct_chg:
                try:
                    pct = float(pct_chg)
                    emoji = "↑" if pct > 0 else "↓" if pct < 0 else ""
                    print(f"    24h涨跌: {pct:+.2f}% {emoji}")
                except (ValueError, TypeError):
                    print(f"    24h涨跌: {pct_chg}%")
            print("="*80)
        except requests.RequestException as e:
            print(f"查询 {symbol} 失败: {e}")


@retry(max_attempts=3, delay=1.0)
def _fetch_klines(symbol: str, interval: str, limit: int) -> list:
    """获取 K线数据（带重试）"""
    url = f"{API_BASE}/api/v3/klines"
    params = {"symbol": symbol, "interval": interval, "limit": limit}
    response = requests.get(url, params=params, timeout=DEFAULT_TIMEOUT)
    response.raise_for_status()
    return response.json()


def kline(symbol, interval="1d", limit=100):
    """获取K线数据"""
    try:
        klines = _fetch_klines(symbol, interval, limit)

        print("\n" + "="*110)
        print(f"{symbol} K线数据 | {interval}")
        print("="*110)
        print(f"{'时间':<18}{'开盘':>12}{'最高':>12}{'最低':>12}{'收盘':>12}{'成交量':>16}{'成交额':>18}")
        print("-"*110)

        for candle in klines:
            ts = candle[0]
            dt = datetime.fromtimestamp(ts/1000).strftime("%Y-%m-%d %H:%M")
            open_p = candle[1]
            high = candle[2]
            low = candle[3]
            close = candle[4]
            vol = candle[5]
            quote_vol = candle[7]

            emoji = "↑" if float(close) > float(open_p) else "↓" if float(close) < float(open_p) else ""

            print(
                f"{dt:<18}"
                f"{open_p:>12}"
                f"{high:>12}"
                f"{low:>12}"
                f"{close:>12}"
                f"{vol:>16}"
                f"{quote_vol:>18} {emoji}"
            )

        print("-"*110)
        print(f"共 {len(klines)} 条数据")
        print("="*110)
    except requests.RequestException as e:
        print(f"查询失败: {e}")


def main():
    parser = argparse.ArgumentParser(
        description="Binance 交易行情查询",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
    # 最新价格
    python binance.py ticker BTCUSDT
    python binance.py ticker BTCUSDT ETHUSDT

    # K线历史
    python binance.py kline BTCUSDT --interval 1d --limit 100
        """
    )
    subparsers = parser.add_subparsers(title="命令", dest="command")

    ticker_parser = subparsers.add_parser("ticker", help="获取最新价格")
    ticker_parser.add_argument("symbols", nargs="+", help="交易对代码 (如: BTCUSDT, ETHUSDT)")

    kline_parser = subparsers.add_parser("kline", help="获取K线数据")
    kline_parser.add_argument("symbol", help="交易对代码")
    kline_parser.add_argument("--interval", default="1d", help="时间周期 (1m,3m,5m,15m,30m,1h,2h,4h,6h,12h,1d,1w,1M)")
    kline_parser.add_argument("--limit", type=int, default=100, help="数据条数 (1-1000)")

    args = parser.parse_args()

    if args.command == "ticker":
        ticker(args.symbols)
    elif args.command == "kline":
        kline(args.symbol, interval=args.interval, limit=args.limit)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
