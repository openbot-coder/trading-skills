#!/usr/bin/env python3
"""
Yahoo Finance 股票/金融数据查询脚本

使用方式:
    # 实时价格
    python yfinance.py price AAPL
    python yfinance.py price AAPL MSFT TSLA

    # K线历史
    python yfinance.py kline AAPL
    python yfinance.py kline AAPL --period 1y --interval 1d --top 60

    # 股票信息
    python yfinance.py info AAPL

    # 财务数据
    python yfinance.py financials AAPL

所有命令都可以用 --help 查看详细用法
"""

import argparse
import sys
import time

try:
    import yfinance as yf
    import pandas as pd
except ImportError as e:
    print(f"缺少依赖: {e}")
    print("请先安装: pip install yfinance pandas")
    sys.exit(1)


def price(symbols):
    """获取股票实时价格"""
    if not isinstance(symbols, list):
        symbols = [symbols]

    for symbol in symbols:
        try:
            ticker = yf.Ticker(symbol)
            info = ticker.info
            print("\n" + "="*80)
            print(f"  {info.get('longName', symbol)} ({symbol})")
            print("="*80)
            print(f"    最新价格: ${info.get('currentPrice', 'N/A'):,.2f}")
            print(f"    昨收: ${info.get('previousClose', 'N/A'):,.2f}")
            print(f"    开盘: ${info.get('open', 'N/A'):,.2f}")
            print(f"    最高: ${info.get('dayHigh', 'N/A'):,.2f}")
            print(f"    最低: ${info.get('dayLow', 'N/A'):,.2f}")
            if info.get('change'):
                change = info['change']
                change_pct = info.get('changePercent', 0)
                emoji = "📈" if change > 0 else "📉"
                print(f"    涨跌: ${change:,.2f} ({change_pct:+.2f}%) {emoji}")
            print(f"    成交量: {info.get('volume', 'N/A'):,.0f}")
            print(f"    市值: ${info.get('marketCap', 'N/A'):,.0f}")
            print("="*80)
        except Exception as e:
            print(f"查询 {symbol} 失败: {e}")


def kline(symbol, period="1mo", interval="1d", top=None):
    """获取历史K线数据"""
    try:
        ticker = yf.Ticker(symbol)
        hist = ticker.history(period=period, interval=interval)
        info = ticker.info

        if top and len(hist) > top:
            hist = hist.tail(top)

        print(f"\n{'='*120}")
        print(f"{info.get('longName', symbol)} ({symbol}) 历史K线")
        print(f"时间周期: {period} | 时间间隔: {interval}")
        print("="*120)
        print(f"{'日期':<18}{'开盘':>12}{'最高':>12}{'最低':>12}{'收盘':>12}{'成交量':>18}{'涨跌':>10}")
        print("-"*120)

        for idx, row in hist.iterrows():
            dt = idx.strftime('%Y-%m-%d')
            change = row['Close'] - row['Open']
            change_pct = (change / row['Open']) * 100 if row['Open'] != 0 else 0
            emoji = "📈" if change > 0 else "📉"

            print(
                f"{dt:<18}"
                f"${row['Open']:>11,.2f}"
                f"${row['High']:>11,.2f}"
                f"${row['Low']:>11,.2f}"
                f"${row['Close']:>11,.2f}"
                f"{int(row['Volume']):>17,.0f}"
                f" {change:>+9,.2f} {emoji}"
            )

        print("-"*120)
        print(f"共 {len(hist)} 条数据")
        print("="*120)
    except Exception as e:
        print(f"查询失败: {e}")


def stock_info(symbol):
    """获取股票详细信息"""
    try:
        ticker = yf.Ticker(symbol)
        info = ticker.info

        print(f"\n{'='*80}")
        print(f"{info.get('longName', symbol)} ({symbol})")
        print("="*80)

        # 基本信息
        print("\n【基本信息】")
        print(f"  行业: {info.get('sector', 'N/A')}")
        print(f"  行业领域: {info.get('industry', 'N/A')}")
        print(f"  国家: {info.get('country', 'N/A')}")
        print(f"  员工数: {info.get('fullTimeEmployees', 'N/A'):,.0f}")
        print(f"  网站: {info.get('website', 'N/A')}")

        # 估值信息
        print("\n【估值信息】")
        print(f"  市值: ${info.get('marketCap', 'N/A'):,.0f}")
        print(f"  PE: {info.get('trailingPE', 'N/A'):,.2f}")
        print(f"  市净率: {info.get('priceToBook', 'N/A'):,.2f}")
        print(f"  股息率: {info.get('dividendYield', 'N/A'):.2%}")
        print(f"  Beta: {info.get('beta', 'N/A'):,.2f}")

        # 交易信息
        print("\n【交易信息】")
        print(f"  最新价: ${info.get('currentPrice', 'N/A'):,.2f}")
        print(f"  52周最高: ${info.get('fiftyTwoWeekHigh', 'N/A'):,.2f}")
        print(f"  52周最低: ${info.get('fiftyTwoWeekLow', 'N/A'):,.2f}")

        print("="*80)
    except Exception as e:
        print(f"查询失败: {e}")


def financials(symbol):
    """获取财务数据"""
    try:
        ticker = yf.Ticker(symbol)
        info = ticker.info

        print(f"\n{'='*80}")
        print(f"{info.get('longName', symbol)} ({symbol}) 财务数据")
        print("="*80)

        # 主要财务指标
        print("\n【主要指标】")
        print(f"  总收入: ${info.get('totalRevenue', 'N/A'):,.0f}")
        print(f"  净利润: ${info.get('netIncomeToCommon', 'N/A'):,.0f}")
        print(f"  总资产: ${info.get('totalCash', 'N/A'):,.0f}")
        print(f"  总负债: ${info.get('totalDebt', 'N/A'):,.0f}")
        print(f"  负债权益比: {info.get('debtToEquity', 'N/A'):,.2f}")
        print(f"  毛利率: {info.get('grossMargins', 'N/A'):,.2%}")
        print(f"  净利率: {info.get('profitMargins', 'N/A'):,.2%}")
        print(f"  ROE: {info.get('returnOnEquity', 'N/A'):,.2%}")

        # 利润表
        print("\n【利润表】")
        try:
            income_stmt = ticker.income_stmt
            if not income_stmt.empty:
                print(income_stmt.iloc[:, :2].to_string())
        except:
            pass

        print("="*80)
    except Exception as e:
        print(f"查询失败: {e}")


def main():
    parser = argparse.ArgumentParser(
        description="Yahoo Finance 股票/金融数据查询",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
    # 实时价格
    python yfinance.py price AAPL
    python yfinance.py price AAPL MSFT TSLA

    # K线历史
    python yfinance.py kline AAPL
    python yfinance.py kline AAPL --period 1y --interval 1d --top 60

    # 股票信息
    python yfinance.py info AAPL

    # 财务数据
    python yfinance.py financials AAPL
        """
    )
    subparsers = parser.add_subparsers(title="命令", dest="command")

    # 价格查询
    price_parser = subparsers.add_parser("price", help="获取股票实时价格")
    price_parser.add_argument("symbols", nargs="+", help="股票代码 (如: AAPL, MSFT)")

    # K线
    kline_parser = subparsers.add_parser("kline", help="获取历史K线数据")
    kline_parser.add_argument("symbol", help="股票代码")
    kline_parser.add_argument("--period", default="1mo", help="时间周期 (1d,5d,1mo,3mo,6mo,1y,2y,5y,10y,ytd,max)")
    kline_parser.add_argument("--interval", default="1d", help="时间间隔 (1m,2m,5m,15m,30m,60m,90m,1h,1d,5d,1wk,1mo,3mo)")
    kline_parser.add_argument("--top", type=int, default=None, help="只显示最后N条数据")

    # 股票信息
    info_parser = subparsers.add_parser("info", help="获取股票详细信息")
    info_parser.add_argument("symbol", help="股票代码")

    # 财务数据
    fin_parser = subparsers.add_parser("financials", help="获取财务数据")
    fin_parser.add_argument("symbol", help="股票代码")

    args = parser.parse_args()

    if args.command == "price":
        price(args.symbols)
    elif args.command == "kline":
        kline(args.symbol, period=args.period, interval=args.interval, top=args.top)
    elif args.command == "info":
        stock_info(args.symbol)
    elif args.command == "financials":
        financials(args.symbol)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
