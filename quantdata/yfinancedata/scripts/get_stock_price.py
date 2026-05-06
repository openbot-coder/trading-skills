#!/usr/bin/env python3
"""
获取股票实时价格

使用方式:
    python get_stock_price.py AAPL        # 获取苹果股价
    python get_stock_price.py AAPL MSFT  # 获取多只股票
"""

import argparse
import sys

try:
    import yfinance as yf
except ImportError:
    print("请先安装: pip install yfinance")
    sys.exit(1)


def get_stock_price(symbol: str):
    """获取单只股票信息"""
    try:
        ticker = yf.Ticker(symbol)
        info = ticker.info

        return {
            "symbol": symbol,
            "name": info.get("longName", symbol),
            "current_price": info.get("currentPrice"),
            "previous_close": info.get("previousClose"),
            "change": info.get("change"),
            "change_percent": info.get("changePercent"),
            "market_cap": info.get("marketCap"),
            "volume": info.get("volume"),
        }
    except Exception as e:
        print(f"获取 {symbol} 失败: {e}")
        return None


def format_data(data: dict):
    """格式化输出"""
    print(f"\n{'='*60}")
    print(f"股票: {data['name']} ({data['symbol']})")
    print(f"{'='*60}")

    if data["current_price"]:
        print(f"当前价格: ${data['current_price']:,.2f}")

    if data["previous_close"]:
        print(f"昨收: ${data['previous_close']:,.2f}")

    if data["change"] and data["change_percent"]:
        emoji = "📈" if data["change"] > 0 else "📉"
        print(f"涨跌: ${data['change']:,.2f} ({data['change_percent']:+.2f}%) {emoji}")

    if data["market_cap"]:
        print(f"市值: ${data['market_cap']:,.0f}")

    if data["volume"]:
        print(f"成交量: {data['volume']:,.0f}")


def main():
    parser = argparse.ArgumentParser(
        description="获取股票实时价格",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
    python get_stock_price.py AAPL        # 获取苹果股价
    python get_stock_price.py AAPL MSFT  # 获取多只股票
    python get_stock_price.py 0700.HK    # 获取港股腾讯
"""
    )
    parser.add_argument(
        "symbols",
        nargs="+",
        help="股票代码 (例如: AAPL, MSFT, 0700.HK)",
    )
    args = parser.parse_args()

    for symbol in args.symbols:
        data = get_stock_price(symbol)
        if data:
            format_data(data)


if __name__ == "__main__":
    main()
