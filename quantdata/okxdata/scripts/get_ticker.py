#!/usr/bin/env python3
"""
获取OKX交易对行情

使用方式:
    python get_ticker.py BTC-USDT
    python get_ticker.py BTC-USDT ETH-USDT

注意: 需要配置API Key
"""

import argparse
import sys
import json

try:
    import requests
except ImportError:
    print("请先安装: pip install requests")
    sys.exit(1)


def get_ticker(symbol: str):
    """获取行情"""
    url = f"https://www.okx.com/api/v5/market/ticker"
    params = {"instId": symbol}

    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        return data
    except requests.RequestException as e:
        print(f"请求失败: {e}")
        return None


def format_data(data):
    """格式化输出"""
    if not data or data.get("code") != "0":
        print("获取数据失败")
        return

    tickers = data.get("data", [])
    if not tickers:
        print("无数据")
        return

    for ticker in tickers:
        print(f"\n{'='*60}")
        print(f"交易对: {ticker.get('instId')}")
        print(f"{'='*60}")
        print(f"最新价格: {ticker.get('last')}")
        print(f"24h最高: {ticker.get('high24h')}")
        print(f"24h最低: {ticker.get('low24h')}")
        print(f"24h成交量: {ticker.get('vol24h')}")
        print(f"24h涨跌幅: {ticker.get('sodUtc0')}")
        print(f"买一价: {ticker.get('bidPx')}")
        print(f"卖一价: {ticker.get('askPx')}")


def main():
    parser = argparse.ArgumentParser(
        description="获取OKX交易对行情",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
    python get_ticker.py BTC-USDT
    python get_ticker.py BTC-USDT ETH-USDT
"""
    )
    parser.add_argument(
        "symbols",
        nargs="+",
        help="交易对代码 (例如: BTC-USDT, ETH-USDT)",
    )
    args = parser.parse_args()

    for symbol in args.symbols:
        data = get_ticker(symbol)
        format_data(data)


if __name__ == "__main__":
    main()
