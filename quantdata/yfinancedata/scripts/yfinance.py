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

import os
import time
import logging
import argparse
from functools import wraps
from typing import Optional

try:
    import yfinance as yf
    import pandas as pd
except ImportError as e:
    print(f"缺少依赖: {e}")
    print("请先安装: pip install yfinance pandas")
    exit(1)

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
                except Exception as e:
                    last_exception = e
                    if attempt < max_attempts - 1:
                        logger.warning(f"请求失败 (尝试 {attempt + 1}/{max_attempts}): {e}")
                        time.sleep(delay)
                    else:
                        logger.error(f"请求最终失败: {e}")
            raise last_exception
        return wrapper
    return decorator


def safe_get_number(val, default=None):
    """安全获取数值"""
    if val is None:
        return default
    try:
        return float(val)
    except (ValueError, TypeError):
        return default


def format_money(val, default="N/A"):
    """格式化货币值"""
    if val is None or val == default:
        return default
    try:
        return f"${float(val)::,.0f}"
    except (ValueError, TypeError):
        return str(val) if val else default


def format_percent(val, default="N/A"):
    """格式化百分比"""
    if val is None or val == default:
        return default
    try:
        return f"{float(val) * 100:.2f}%"
    except (ValueError, TypeError):
        return str(val) if val else default


@retry(max_attempts=3, delay=1.0)
def _fetch_ticker_info(symbol: str) -> dict:
    """获取股票信息（带重试）"""
    ticker = yf.Ticker(symbol)
    return ticker.info


@retry(max_attempts=3, delay=1.0)
def _fetch_history(symbol: str, period: str, interval: str) -> pd.DataFrame:
    """获取历史K线数据（带重试）"""
    ticker = yf.Ticker(symbol)
    return ticker.history(period=period, interval=interval)


def price(symbols):
    """获取股票实时价格"""
    if not isinstance(symbols, list):
        symbols = [symbols]

    for symbol in symbols:
        try:
            info = _fetch_ticker_info(symbol)

            name = info.get('longName', symbol)
            current = safe_get_number(info.get('currentPrice'))
            prev_close = safe_get_number(info.get('previousClose'))
            open_price = safe_get_number(info.get('open'))
            day_high = safe_get_number(info.get('dayHigh'))
            day_low = safe_get_number(info.get('dayLow'))
            volume = info.get('volume')
            market_cap = safe_get_number(info.get('marketCap'))

            print("\n" + "="*80)
            print(f"  {name} ({symbol})")
            print("="*80)

            if current is not None:
                print(f"    最新价格: ${current:,.2f}")
            if prev_close is not None:
                print(f"    昨收: ${prev_close:,.2f}")
            if open_price is not None:
                print(f"    开盘: ${open_price:,.2f}")
            if day_high is not None:
                print(f"    最高: ${day_high:,.2f}")
            if day_low is not None:
                print(f"    最低: ${day_low:,.2f}")

            change = safe_get_number(info.get('change'))
            if change is not None:
                emoji = "↑" if change > 0 else "↓"
                print(f"    涨跌: ${change:,.2f} {emoji}")

            if volume is not None:
                try:
                    print(f"    成交量: {int(volume):,}")
                except (ValueError, TypeError):
                    print(f"    成交量: {volume}")

            if market_cap is not None:
                print(f"    市值: ${market_cap:,.0f}")

            print("="*80)
        except Exception as e:
            print(f"查询 {symbol} 失败: {e}")


def kline(symbol, period="1mo", interval="1d", top=None):
    """获取历史K线数据"""
    try:
        hist = _fetch_history(symbol, period, interval)

        if top and len(hist) > top:
            hist = hist.tail(top)

        info = _fetch_ticker_info(symbol)
        name = info.get('longName', symbol)

        print(f"\n{'='*120}")
        print(f"{name} ({symbol}) 历史K线")
        print(f"时间周期: {period} | 时间间隔: {interval}")
        print("="*120)
        print(f"{'日期':<18}{'开盘':>12}{'最高':>12}{'最低':>12}{'收盘':>12}{'成交量':>18}{'涨跌':>10}")
        print("-"*120)

        for idx, row in hist.iterrows():
            dt = idx.strftime('%Y-%m-%d')
            open_val = row['Open']
            close_val = row['Close']
            change = close_val - open_val
            emoji = "↑" if change > 0 else "↓" if change < 0 else ""

            print(
                f"{dt:<18}"
                f"${open_val:>11,.2f}"
                f"${row['High']:>11,.2f}"
                f"${row['Low']:>11,.2f}"
                f"${close_val:>11,.2f}"
                f"{int(row['Volume']):>17,}"
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
        info = _fetch_ticker_info(symbol)

        name = info.get('longName', symbol)
        print(f"\n{'='*80}")
        print(f"{name} ({symbol})")
        print("="*80)

        print("\n【基本信息】")
        print(f"  行业: {info.get('sector', 'N/A')}")
        print(f"  行业领域: {info.get('industry', 'N/A')}")
        print(f"  国家: {info.get('country', 'N/A')}")
        employees = info.get('fullTimeEmployees')
        if employees is not None:
            try:
                print(f"  员工数: {int(employees):,}")
            except (ValueError, TypeError):
                print(f"  员工数: {employees}")
        print(f"  网站: {info.get('website', 'N/A')}")

        print("\n【估值信息】")
        print(f"  市值: {format_money(info.get('marketCap'))}")
        print(f"  PE: {format_percent(info.get('trailingPE'))}")
        print(f"  市净率: {format_percent(info.get('priceToBook'))}")
        print(f"  股息率: {format_percent(info.get('dividendYield'))}")
        print(f"  Beta: {format_percent(info.get('beta'))}")

        print("\n【交易信息】")
        print(f"  最新价: {format_money(info.get('currentPrice'))}")
        print(f"  52周最高: {format_money(info.get('fiftyTwoWeekHigh'))}")
        print(f"  52周最低: {format_money(info.get('fiftyTwoWeekLow'))}")

        print("="*80)
    except Exception as e:
        print(f"查询失败: {e}")


def financials(symbol):
    """获取财务数据"""
    try:
        info = _fetch_ticker_info(symbol)
        ticker = yf.Ticker(symbol)

        name = info.get('longName', symbol)
        print(f"\n{'='*80}")
        print(f"{name} ({symbol}) 财务数据")
        print("="*80)

        print("\n【主要指标】")
        print(f"  总收入: {format_money(info.get('totalRevenue'))}")
        print(f"  净利润: {format_money(info.get('netIncomeToCommon'))}")
        print(f"  总资产: {format_money(info.get('totalCash'))}")
        print(f"  总负债: {format_money(info.get('totalDebt'))}")
        print(f"  负债权益比: {format_percent(info.get('debtToEquity'))}")
        print(f"  毛利率: {format_percent(info.get('grossMargins'))}")
        print(f"  净利率: {format_percent(info.get('profitMargins'))}")
        print(f"  ROE: {format_percent(info.get('returnOnEquity'))}")

        print("\n【利润表】")
        try:
            income_stmt = ticker.income_stmt
            if income_stmt is not None and not income_stmt.empty:
                print(income_stmt.iloc[:, :2].to_string())
        except Exception:
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

    price_parser = subparsers.add_parser("price", help="获取股票实时价格")
    price_parser.add_argument("symbols", nargs="+", help="股票代码 (如: AAPL, MSFT)")

    kline_parser = subparsers.add_parser("kline", help="获取历史K线数据")
    kline_parser.add_argument("symbol", help="股票代码")
    kline_parser.add_argument("--period", default="1mo", help="时间周期 (1d,5d,1mo,3mo,6mo,1y,2y,5y,10y,ytd,max)")
    kline_parser.add_argument("--interval", default="1d", help="时间间隔 (1m,2m,5m,15m,30m,60m,90m,1h,1d,5d,1wk,1mo,3mo)")
    kline_parser.add_argument("--top", type=int, default=None, help="只显示最后N条数据")

    info_parser = subparsers.add_parser("info", help="获取股票详细信息")
    info_parser.add_argument("symbol", help="股票代码")

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
