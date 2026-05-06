#!/usr/bin/env python3
"""
CoinGecko 加密货币数据查询脚本

使用方式:
    # 价格查询
    python coingecko.py price bitcoin
    python coingecko.py price "bitcoin,ethereum,solana" --cny

    # 市值排行
    python coingecko.py top
    python coingecko.py top --top 10 --change 7d

    # K线历史
    python coingecko.py kline bitcoin --days 30

    # 全球市场数据
    python coingecko.py global

所有命令都可以用 --help 查看详细用法
"""

import argparse
import sys
import requests
import time

API_BASE = "https://api.coingecko.com/api/v3"


def price(coin_ids, vs_currencies="usd", cny=False):
    """获取加密货币价格"""
    if cny:
        vs_currencies = "usd,cny"
    params = {
        "ids": coin_ids,
        "vs_currencies": vs_currencies,
        "include_24hr_change": "true",
        "include_market_cap": "true",
        "include_24hr_vol": "true",
    }
    try:
        response = requests.get(f"{API_BASE}/simple/price", params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        print("\n" + "="*80)
        for coin, info in data.items():
            print(f"  {coin.upper()}:")
            if "usd" in info:
                print(f"    价格(USD): ${info['usd']:,.2f}")
            if "cny" in info:
                print(f"    价格(CNY): ¥{info['cny']:,.2f}")
            if "usd_24h_change" in info:
                change = info["usd_24h_change"]
                emoji = "📈" if change > 0 else "📉"
                print(f"    24h涨跌幅: {change:+.2f}% {emoji}")
            if "usd_market_cap" in info:
                print(f"    市值: ${info['usd_market_cap']:,.0f}")
            if "usd_24h_vol" in info:
                print(f"    24h成交量: ${info['usd_24h_vol']:,.0f}")
            print("-"*60)
    except Exception as e:
        print(f"查询失败: {e}")


def top_coins(vs_currency="usd", top=20, change_period="24h"):
    """获取市值排行榜"""
    params = {
        "vs_currency": vs_currency,
        "order": "market_cap_desc",
        "per_page": top,
        "page": 1,
        "sparkline": "false",
        "price_change_percentage": change_period,
    }
    try:
        response = requests.get(f"{API_BASE}/coins/markets", params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        print("\n" + "="*120)
        print(f"{'排名':<6}{'名称':<15}{'代码':<8}{'价格(USD)':>12}{change_period+'涨跌幅':>12}{'市值':>20}{'24h成交量':>20}")
        print("-"*120)
        for idx, coin in enumerate(data, 1):
            change_key = f"price_change_percentage_{change_period}"
            change = coin.get(change_key, 0)
            emoji = "📈" if change > 0 else "📉" if change < 0 else ""
            print(
                f"{idx:<6}{coin['name']:<15}{coin['symbol'].upper():<8}"
                f"${coin['current_price']:>11,.2f}"
                f" {change:>+10,.2f}% {emoji}"
                f"${coin['market_cap']:>19,.0f}"
                f"${coin['total_volume']:>19,.0f}"
            )
        print("="*120)
    except Exception as e:
        print(f"查询失败: {e}")


def kline(coin_id, vs_currency="usd", days=30, interval="daily"):
    """获取历史K线数据"""
    params = {
        "vs_currency": vs_currency,
        "days": days,
        "interval": interval,
    }
    try:
        response = requests.get(f"{API_BASE}/coins/{coin_id}/market_chart", params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        prices = data.get("prices", [])
        print(f"\n{'='*80}")
        print(f"{coin_id.upper()} 历史K线数据 (最近 {days} 天)")
        print("-"*80)
        print(f"{'时间':<20}{'价格(USD)':>18}")
        print("-"*80)
        for timestamp, price in prices[-20:]:
            dt = time.strftime('%Y-%m-%d %H:%M', time.localtime(timestamp/1000))
            print(f"{dt:<20}${price:>17,.2f}")
        print(f"\n共 {len(prices)} 条数据，显示最后 20 条")
        print("="*80)
    except Exception as e:
        print(f"查询失败: {e}")


def global_data():
    """获取全球市场数据"""
    try:
        response = requests.get(f"{API_BASE}/global", timeout=10)
        response.raise_for_status()
        data = response.json()["data"]
        print(f"\n{'='*80}")
        print("加密货币全球市场概览")
        print("="*80)
        print(f"  总市值(USD): ${data['total_market_cap']['usd']:,.0f}")
        print(f"  24h总成交量(USD): ${data['total_volume']['usd']:,.0f}")
        print(f"  BTC 市值占比: {data['market_cap_percentage']['btc']:.2f}%")
        print(f"  ETH 市值占比: {data['market_cap_percentage']['eth']:.2f}%")
        print(f"  活跃加密货币数量: {data['active_cryptocurrencies']}")
        print(f"  活跃交易所数量: {data['exchanges']}")
        print(f"  市值变化(24h): {data['market_cap_change_24h']:.2f}%")
        print("="*80)
    except Exception as e:
        print(f"查询失败: {e}")


def search(query):
    """搜索加密货币"""
    try:
        response = requests.get(f"{API_BASE}/search", params={"query": query}, timeout=10)
        response.raise_for_status()
        data = response.json()
        print(f"\n{'='*80}")
        print(f"搜索 '{query}' 的结果:")
        print("="*80)
        if data.get("coins"):
            print("\n加密货币:")
            for i, coin in enumerate(data["coins"][:10], 1):
                print(f"  {i}. {coin['name']} ({coin['symbol'].upper()}) - ID: {coin['id']}")
        print("="*80)
    except Exception as e:
        print(f"查询失败: {e}")


def main():
    parser = argparse.ArgumentParser(
        description="CoinGecko 加密货币数据查询",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
    # 价格查询
    python coingecko.py price bitcoin
    python coingecko.py price "bitcoin,ethereum,solana" --cny

    # 市值排行
    python coingecko.py top
    python coingecko.py top --top 10 --change 7d

    # K线历史
    python coingecko.py kline bitcoin --days 30

    # 全球市场
    python coingecko.py global

    # 搜索
    python coingecko.py search bitcoin
        """
    )
    subparsers = parser.add_subparsers(title="命令", dest="command")

    # 价格查询
    price_parser = subparsers.add_parser("price", help="获取加密货币价格")
    price_parser.add_argument("coin_ids", help="加密货币ID，多个用逗号分隔 (如: bitcoin,ethereum)")
    price_parser.add_argument("--cny", action="store_true", help="显示人民币价格")
    price_parser.add_argument("--vs-currency", default="usd", help="计价货币 (默认: usd)")

    # 市值排行
    top_parser = subparsers.add_parser("top", help="获取市值排行榜")
    top_parser.add_argument("--top", type=int, default=20, help="显示前N个 (默认: 20)")
    top_parser.add_argument("--change", default="24h", choices=["24h", "7d", "14d", "30d", "60d", "1y"], help="涨跌幅周期 (默认: 24h)")
    top_parser.add_argument("--vs-currency", default="usd", help="计价货币 (默认: usd)")

    # K线历史
    kline_parser = subparsers.add_parser("kline", help="获取历史K线数据")
    kline_parser.add_argument("coin_id", help="加密货币ID")
    kline_parser.add_argument("--days", type=int, default=30, help="天数 (默认: 30)")
    kline_parser.add_argument("--interval", default="daily", choices=["daily", "hourly", "minutely"], help="时间间隔 (默认: daily)")
    kline_parser.add_argument("--vs-currency", default="usd", help="计价货币 (默认: usd)")

    # 全球市场
    subparsers.add_parser("global", help="获取全球市场数据")

    # 搜索
    search_parser = subparsers.add_parser("search", help="搜索加密货币")
    search_parser.add_argument("query", help="搜索关键词")

    args = parser.parse_args()

    if args.command == "price":
        price(args.coin_ids, vs_currencies=args.vs_currency, cny=args.cny)
    elif args.command == "top":
        top_coins(top=args.top, change_period=args.change, vs_currency=args.vs_currency)
    elif args.command == "kline":
        kline(args.coin_id, vs_currency=args.vs_currency, days=args.days, interval=args.interval)
    elif args.command == "global":
        global_data()
    elif args.command == "search":
        search(args.query)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
