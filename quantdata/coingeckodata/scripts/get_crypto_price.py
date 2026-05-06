#!/usr/bin/env python3
"""
获取加密货币价格

使用方式:
    python get_crypto_price.py bitcoin         # 获取比特币价格
    python get_crypto_price.py ethereum --cny  # 获取以太坊价格（人民币）
    python get_crypto_price.py "bitcoin,ethereum,solana"  # 获取多个币种
"""

import argparse
import requests

API_URL = "https://api.coingecko.com/api/v3/simple/price"


def get_crypto_price(coin_ids: str, vs_currencies: str = "usd,cny"):
    """获取加密货币价格"""
    params = {
        "ids": coin_ids,
        "vs_currencies": vs_currencies,
        "include_24hr_change": "true",
        "include_market_cap": "true",
        "include_24hr_vol": "true",
    }

    try:
        response = requests.get(API_URL, params=params, timeout=10)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        print(f"请求失败: {e}")
        return None


def format_price(data: dict, show_cny: bool = False):
    """格式化输出价格信息"""
    for coin_id, info in data.items():
        print(f"\n{'='*50}")
        print(f"币种: {coin_id.upper()}")
        print(f"{'='*50}")

        if "usd" in info:
            price_usd = info["usd"]
            print(f"价格 (USD): ${price_usd:,.2f}")

        if show_cny and "cny" in info:
            price_cny = info["cny"]
            print(f"价格 (CNY): ¥{price_cny:,.2f}")

        if "usd_24h_change" in info:
            change = info["usd_24h_change"]
            emoji = "📈" if change > 0 else "📉"
            print(f"24h涨跌幅: {change:+.2f}% {emoji}")

        if "usd_market_cap" in info:
            market_cap = info["usd_market_cap"]
            print(f"市值: ${market_cap:,.0f}")

        if "usd_24h_vol" in info:
            volume = info["usd_24h_vol"]
            print(f"24h交易量: ${volume:,.0f}")


def main():
    parser = argparse.ArgumentParser(
        description="获取加密货币价格",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
    python get_crypto_price.py bitcoin                          # 获取比特币价格
    python get_crypto_price.py ethereum --cny                   # 获取以太坊价格（含人民币）
    python get_crypto_price.py "bitcoin,ethereum,solana"        # 获取多个币种
"""
    )
    parser.add_argument(
        "coin",
        nargs="?",
        default="bitcoin",
        help='币种ID (例如: bitcoin, ethereum, solana; 多个用逗号分隔)',
    )
    parser.add_argument("--cny", action="store_true", help="显示人民币价格")
    args = parser.parse_args()

    vs_currencies = "usd,cny" if args.cny else "usd"
    data = get_crypto_price(args.coin, vs_currencies)

    if data:
        format_price(data, show_cny=args.cny)
    else:
        print("获取数据失败")


if __name__ == "__main__":
    main()
