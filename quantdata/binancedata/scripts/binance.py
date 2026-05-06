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

import argparse
import sys
from datetime import datetime

try:
    import requests
except ImportError:
    print("请先安装: pip install requests")
    sys.exit(1)


API_BASE = "https://api.binance.com"


def ticker(symbols):
    """获取最新价格"""
    if not isinstance(symbols, list):
        symbols = [symbols]

    for symbol in symbols:
        try:
            url = f"{API_BASE}/api/v3/ticker/24hr"
            params = {"symbol": symbol}
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()

            print("\n" + "="*80)
            print(f"  {symbol}")
            print("="*80)
            print(f"    最新价格: {data.get('lastPrice')}")
            print(f"    24h开盘: {data.get('openPrice')}")
            print(f"    24h最高: {data.get('highPrice')}")
            print(f"    24h最低: {data.get('lowPrice')}")
            print(f"    24h成交量: {data.get('volume')}")
            print(f"    24h成交额: {data.get('quoteVolume')}")
            print(f"    24h涨跌: {data.get('priceChangePercent')}%")
            print("="*80)
        except Exception as e:
            print(f"查询 {symbol} 失败: {e}")


def kline(symbol, interval="1d", limit=100):
    """获取K线数据"""
    try:
        url = f"{API_BASE}/api/v3/klines"
        params = {"symbol": symbol, "interval": interval, "limit": limit}
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        klines = response.json()

        print("\n" + "="*110)
        print(f"{symbol} K线数据 | {interval}")
        print("="*110)
        print(f"{'时间':<18}{'开盘':>12}{'最高':>12}{'最低':>12}{'收盘':>12}{'成交量':>16}{'成交额':>18}")
        print("-"*110)

        for kline in klines:
            ts = kline[0]
            dt = datetime.fromtimestamp(ts/1000).strftime("%Y-%m-%d %H:%M")
            open_p = kline[1]
            high = kline[2]
            low = kline[3]
            close = kline[4]
            vol = kline[5]
            quote_vol = kline[7]

            emoji = "📈" if float(close) > float(open_p) else "📉" if float(close) < float(open_p) else ""

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
    except Exception as e:
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

    # 最新价格
    ticker_parser = subparsers.add_parser("ticker", help="获取最新价格")
    ticker_parser.add_argument("symbols", nargs="+", help="交易对代码 (如: BTCUSDT, ETHUSDT)")

    # K线
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
