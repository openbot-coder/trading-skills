#!/usr/bin/env python3
"""
OKX 交易行情查询脚本

使用方式:
    # 最新价格
    python okx.py ticker BTC-USDT

    # K线历史
    python okx.py kline BTC-USDT --bar 1d --limit 100

所有命令都可以用 --help 查看详细用法
"""

import argparse
import sys

try:
    import requests
except ImportError:
    print("请先安装: pip install requests")
    sys.exit(1)


API_BASE = "https://www.okx.com"


def ticker(symbols):
    """获取最新价格"""
    if not isinstance(symbols, list):
        symbols = [symbols]

    for symbol in symbols:
        try:
            url = f"{API_BASE}/api/v5/market/ticker"
            params = {"instId": symbol}
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()

            if data.get("code") == "0" and data.get("data"):
                ticker_data = data["data"][0]
                print("\n" + "="*80)
                print(f"  {symbol}")
                print("="*80)
                print(f"    最新价格: {ticker_data.get('last')}")
                print(f"    24h最高: {ticker_data.get('high24h')}")
                print(f"    24h最低: {ticker_data.get('low24h')}")
                print(f"    24h成交量: {ticker_data.get('vol24h')}")
                print(f"    买一价: {ticker_data.get('bidPx')}")
                print(f"    卖一价: {ticker_data.get('askPx')}")
                print("="*80)
            else:
                print(f"查询失败: {data.get('msg')}")
        except Exception as e:
            print(f"查询 {symbol} 失败: {e}")


def kline(symbol, bar="1d", limit=100):
    """获取K线数据"""
    try:
        url = f"{API_BASE}/api/v5/market/candles"
        params = {"instId": symbol, "bar": bar, "limit": limit}
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()

        if data.get("code") == "0" and data.get("data"):
            klines = data["data"][::-1]  # 反转顺序
            print("\n" + "="*100)
            print(f"{symbol} K线数据 | {bar}")
            print("="*100)
            print(f"{'时间':<18}{'开盘':>12}{'最高':>12}{'最低':>12}{'收盘':>12}{'成交量':>16}")
            print("-"*100)

            for kline in klines:
                ts = kline[0]
                open_p = kline[1]
                high = kline[2]
                low = kline[3]
                close = kline[4]
                vol = kline[5]

                emoji = "📈" if float(close) > float(open_p) else "📉" if float(close) < float(open_p) else ""

                print(
                    f"{ts:<18}"
                    f"{open_p:>12}"
                    f"{high:>12}"
                    f"{low:>12}"
                    f"{close:>12}"
                    f"{vol:>16} {emoji}"
                )

            print("-"*100)
            print(f"共 {len(klines)} 条数据")
            print("="*100)
        else:
            print(f"查询失败: {data.get('msg')}")
    except Exception as e:
        print(f"查询失败: {e}")


def main():
    parser = argparse.ArgumentParser(
        description="OKX 交易行情查询",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
    # 最新价格
    python okx.py ticker BTC-USDT
    python okx.py ticker BTC-USDT ETH-USDT

    # K线历史
    python okx.py kline BTC-USDT --bar 1d --limit 100
        """
    )
    subparsers = parser.add_subparsers(title="命令", dest="command")

    # 最新价格
    ticker_parser = subparsers.add_parser("ticker", help="获取最新价格")
    ticker_parser.add_argument("symbols", nargs="+", help="交易对代码 (如: BTC-USDT, ETH-USDT)")

    # K线
    kline_parser = subparsers.add_parser("kline", help="获取K线数据")
    kline_parser.add_argument("symbol", help="交易对代码")
    kline_parser.add_argument("--bar", default="1d", help="时间周期 (1m,3m,5m,15m,30m,1H,2H,4H,6H,12H,1D,1W,1M,3M,6M,1Y)")
    kline_parser.add_argument("--limit", type=int, default=100, help="数据条数 (1-300)")

    args = parser.parse_args()

    if args.command == "ticker":
        ticker(args.symbols)
    elif args.command == "kline":
        kline(args.symbol, bar=args.bar, limit=args.limit)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
