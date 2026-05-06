#!/usr/bin/env python3
"""
获取股票K线数据

使用方式:
    python get_kline.py AAPL                       # 获取默认K线
    python get_kline.py AAPL --period 1y          # 获取最近1年
    python get_kline.py AAPL --interval 1d --top 30  # 日线，显示最近30天
"""

import argparse
import sys
from datetime import datetime

try:
    import yfinance as yf
except ImportError:
    print("请先安装: pip install yfinance")
    sys.exit(1)


def get_kline(symbol: str, period: str = "1mo", interval: str = "1d"):
    """获取K线数据"""
    try:
        ticker = yf.Ticker(symbol)
        hist = ticker.history(period=period, interval=interval)
        return hist
    except Exception as e:
        print(f"获取 {symbol} K线失败: {e}")
        return None


def format_data(df, symbol: str, top_n: int = None):
    """格式化输出K线数据"""
    if df is None or df.empty:
        print("无数据")
        return

    # 如果指定了top_n，只显示最后n行
    if top_n and len(df) > top_n:
        df = df.tail(top_n)

    info = yf.Ticker(symbol).info
    name = info.get("longName", symbol)

    print(f"\n{'='*90}")
    print(f"K线数据: {name} ({symbol})")
    print(f"{'='*90}")
    print(f"{'日期':<12} {'开盘':>10} {'最高':>10} {'最低':>10} {'收盘':>10} {'成交量':>15}")
    print(f"{'-'*90}")

    for idx, row in df.iterrows():
        date = idx.strftime("%Y-%m-%d")
        open_p = row["Open"]
        high = row["High"]
        low = row["Low"]
        close = row["Close"]
        volume = row["Volume"]

        print(
            f"{date:<12} ${open_p:>9.2f} ${high:>9.2f} ${low:>9.2f} ${close:>9.2f} {volume:>15,.0f}"
        )

    print(f"{'-'*90}")
    print(f"共 {len(df)} 条数据")


def main():
    parser = argparse.ArgumentParser(
        description="获取股票K线数据",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
    python get_kline.py AAPL                          # 默认最近1个月日线
    python get_kline.py AAPL --period 1y              # 最近1年
    python get_kline.py AAPL --period 1y --top 60     # 最近1年，显示最后60条
    python get_kline.py AAPL --interval 1wk           # 周线
    python get_kline.py AAPL --period max --top 100   # 全部历史，显示最近100条

参数说明:
    period: 时间周期 (1d,5d,1mo,3mo,6mo,1y,2y,5y,10y,ytd,max)
    interval: 时间间隔 (1m,2m,5m,15m,30m,60m,90m,1h,1d,5d,1wk,1mo,3mo)
"""
    )
    parser.add_argument("symbol", help="股票代码 (例如: AAPL, MSFT)")
    parser.add_argument(
        "--period",
        type=str,
        default="1mo",
        help="时间周期 (默认: 1mo)",
    )
    parser.add_argument(
        "--interval",
        type=str,
        default="1d",
        help="K线间隔 (默认: 1d)",
    )
    parser.add_argument(
        "--top",
        type=int,
        default=None,
        help="只显示最后N条数据",
    )
    args = parser.parse_args()

    df = get_kline(args.symbol, period=args.period, interval=args.interval)
    format_data(df, args.symbol, top_n=args.top)


if __name__ == "__main__":
    main()
