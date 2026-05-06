#!/usr/bin/env python3
"""
获取Binance交易对行情

使用方式:
    python get_ticker.py BTCUSDT
    python get_ticker.py BTCUSDT ETHUSDT
"""

import argparse
import sys

try:
    import requests
except ImportError:
    print("请先安装: pip install requests")
    sys.exit(1)


def get_ticker(symbol: str):
    """获取行情"""
    url = "https://api.binance.com/api/v3/ticker/24hr"
    params = {"symbol": symbol}

    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        print(f"请求失败: {e}")
        return None


def format_data(data):
    """格式化输出"""
    if not data:
        print("获取数据失败")
        return

    print(f"\n{'='*60}")
    print(f"交易对: {data.get('symbol')}")
    print(f"{'='*60}")
    print(f"最新价格: {data.get('lastPrice')}")
    print(f"24h最高: {data.get('highPrice')}")
    print(f"24h最低: {data.get('lowPrice')}")
    print(f"24h开盘: {data.get('openPrice')}")
    print(f"24h成交量: {data.get('volume')}")
    print(f"24h成交额: {data.get('quoteVolume')}")
    print(f"24h涨跌幅: {data.get('priceChangePercent')}%")


def main():
    parser = argparse.ArgumentParser(
        description="获取Binance交易对行情",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
    python get_ticker.py BTCUSDT
    python get_ticker.py BTCUSDT ETHUSDT
"""
    )
    parser.add_argument(
        "symbols",
        nargs="+",
        help="交易对代码 (例如: BTCUSDT, ETHUSDT)",
    )
    args = parser.parse_args()

    for symbol in args.symbols:
        data = get_ticker(symbol)
        format_data(data)


if __name__ == "__main__":
    main()
