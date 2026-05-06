#!/usr/bin/env python3
"""
获取加密货币市值排行榜

使用方式:
    python get_top_crypto.py                    # 默认获取前20
    python get_top_crypto.py --top 10           # 获取前10
    python get_top_crypto.py --change 7d        # 显示7天涨跌幅
"""

import argparse
import requests

API_URL = "https://api.coingecko.com/api/v3/coins/markets"


def get_top_crypto(vs_currency: str = "usd", top_n: int = 20, change_period: str = "24h"):
    """获取市值排行榜"""
    params = {
        "vs_currency": vs_currency,
        "order": "market_cap_desc",
        "per_page": top_n,
        "page": 1,
        "sparkline": "false",
        "price_change_percentage": change_period,
    }

    try:
        response = requests.get(API_URL, params=params, timeout=10)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        print(f"请求失败: {e}")
        return None


def format_data(data: list, change_period: str = "24h"):
    """格式化输出"""
    print(f"\n{'='*110}")
    print(f"{'排名':<4} {'币种':<15} {'价格':>15} {change_period+'涨跌幅':>12} {'市值':>20} {'24h交易量':>20}")
    print(f"{'='*110}")

    for idx, coin in enumerate(data, 1):
        name = coin["name"][:15]
        price = coin["current_price"]
        change_key = f"price_change_percentage_{change_period}"
        change = coin.get(change_key, 0)
        market_cap = coin["market_cap"]
        volume = coin["total_volume"]

        emoji = "📈" if change > 0 else "📉" if change < 0 else " "
        print(
            f"{idx:<4} {name:<15} ${price:>14,.2f} {change:>+11,.2f}% {emoji} ${market_cap:>18,.0f} ${volume:>18,.0f}"
        )
    print(f"{'='*110}")


def main():
    parser = argparse.ArgumentParser(
        description="获取加密货币市值排行榜",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
    python get_top_crypto.py                    # 默认获取前20，24h涨跌幅
    python get_top_crypto.py --top 10           # 获取前10
    python get_top_crypto.py --change 7d        # 显示7天涨跌幅
    python get_top_crypto.py --top 50 --change 30d  # 前50，30天涨跌幅
"""
    )
    parser.add_argument("--top", type=int, default=20, help="显示前N个（默认20）")
    parser.add_argument(
        "--change", type=str, default="24h", help="涨跌幅周期（24h/7d/30d/1y）"
    )
    args = parser.parse_args()

    data = get_top_crypto(top_n=args.top, change_period=args.change)

    if data:
        format_data(data, change_period=args.change)
    else:
        print("获取数据失败")


if __name__ == "__main__":
    main()
