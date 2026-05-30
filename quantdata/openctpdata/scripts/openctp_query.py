#!/usr/bin/env python3
"""
OpenCTP 数据查询脚本
用法:
  python openctp_query.py --products futures
  python openctp_query.py --instruments au,rb,IF
  python openctp_query.py --times ag,au
  python openctp_query.py --markets
  python openctp_query.py --prices au2508,rb2510
  python openctp_query.py --all-futures
"""

import argparse
import json
import urllib.request
import urllib.parse
import sys

BASE_URL = "http://dict.openctp.cn"


def get(url: str) -> dict:
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            return json.loads(resp.read().decode())
    except Exception as e:
        print(f"❌ 网络请求失败: {e}")
        sys.exit(1)


def _fmt_margin(ratio: float) -> str:
    """保证金率转百分比字符串"""
    if ratio is None or ratio == 0:
        return "-"
    return f"{ratio * 100:.1f}%"


def _fmt_fee(ratio: float, volume_fee: float) -> str:
    """手续费转字符串（万分比 + 绝对值）"""
    if ratio is None and volume_fee is None:
        return "-"
    parts = []
    if ratio and ratio > 0:
        parts.append(f"{round(ratio * 10000, 4):.2f}%%")  # 万分之
    if volume_fee and volume_fee > 0:
        parts.append(f"¥{round(volume_fee, 2)}/手")
    return " + ".join(parts) if parts else "-"


def list_products(types: str = "futures", areas: str = "China") -> None:
    params = {"types": types, "areas": areas}
    url = f"{BASE_URL}/products?{urllib.parse.urlencode(params)}"
    data = get(url)
    if data.get("rsp_code") != 0:
        print(f"❌ 错误: {data.get('rsp_message')}")
        return

    products = data.get("data", [])
    cls_map = {"1": "期货", "2": "期权", "3": "组合", "8": "股票", "f": "基金", "b": "债券"}
    print(f"\n📋 国内期货品种列表 ({len(products)} 个)\n")
    print(f"{'品种ID':<8} {'品种名称':<20} {'交易所':<8} {'类别'}")
    print("-" * 50)
    for p in sorted(products, key=lambda x: x.get("ExchangeID", "") + x.get("ProductID", "")):
        cls = cls_map.get(p.get("ProductClass", ""), p.get("ProductClass", ""))
        print(f"{p.get('ProductID', ''):<8} {p.get('ProductName', ''):<20} {p.get('ExchangeID', ''):<8} {cls}")


def list_instruments(products: str = "", markets: str = "", types: str = "futures") -> None:
    params = {"types": types}
    if products:
        params["products"] = products
    if markets:
        params["markets"] = markets
    url = f"{BASE_URL}/instruments?{urllib.parse.urlencode(params)}"
    data = get(url)
    if data.get("rsp_code") != 0:
        print(f"❌ 错误: {data.get('rsp_message')}")
        return

    instruments = data.get("data", [])
    print(f"\n📋 合约详情 ({len(instruments)} 个)\n")
    print(
        f"{'合约代码':<10} {'交易所':<6} {'品种':<5} {'乘数':<5} {'跳动':<6} "
        f"{'保证金':<8} {'开仓费':<14} {'平今费':<14} {'到期日':<12} {'状态'}"
    )
    print("-" * 110)
    phase_map = {"1": "上市", "2": "上市", "3": "停牌"}
    for ins in sorted(instruments, key=lambda x: x.get("ProductID", "") + x.get("InstrumentID", "")):
        ins_id = ins.get("InstrumentID", "")
        status = phase_map.get(ins.get("InstLifePhase", ""), ins.get("InstLifePhase", ""))
        expire = ins.get("ExpireDate", ins.get("DeliveryDate", ""))
        # 保证金取多头按金额
        margin = _fmt_margin(ins.get("LongMarginRatioByMoney"))
        # 手续费
        open_fee = _fmt_fee(
            ins.get("OpenRatioByMoney"),
            ins.get("OpenRatioByVolume")
        )
        today_fee = _fmt_fee(
            ins.get("CloseTodayRatioByMoney"),
            ins.get("CloseTodayRatioByVolume")
        )
        print(
            f"{ins_id:<10} {ins.get('ExchangeID', ''):<6} {ins.get('ProductID', ''):<5} "
            f"{ins.get('VolumeMultiple', ''):<5} {ins.get('PriceTick', ''):<6} "
            f"{margin:<8} {open_fee:<14} {today_fee:<14} {expire:<12} {status}"
        )


def list_times(products: str = "", markets: str = "", types: str = "futures") -> None:
    params = {"types": types}
    if products:
        params["products"] = products
    if markets:
        params["markets"] = markets
    url = f"{BASE_URL}/times?{urllib.parse.urlencode(params)}"
    data = get(url)
    if data.get("rsp_code") != 0:
        print(f"❌ 错误: {data.get('rsp_message')}")
        return

    times = data.get("data", [])
    grouped: dict = {}
    for t in times:
        key = f"{t.get('ExchangeID', '')}-{t.get('ProductID', '')}"
        grouped.setdefault(key, []).append(t)

    print(f"\n📋 交易时段 ({len(grouped)} 个品种)\n")
    seg_name = {1: "第一段", 2: "第二段", 3: "第三段", 4: "第四段", 5: "第五段"}
    for key in sorted(grouped):
        print(f"  🔸 {key}")
        for seg in sorted(grouped[key], key=lambda x: x.get("SegmentNo", 1)):
            sn = seg.get("SegmentNo", 1)
            begin = seg.get("TimeBegin", "")
            end = seg.get("TimeEnd", "")
            print(f"      {seg_name.get(sn, f'段{sn}')}  {begin} ~ {end}")


def list_markets(areas: str = "China") -> None:
    params = {"areas": areas}
    url = f"{BASE_URL}/markets?{urllib.parse.urlencode(params)}"
    data = get(url)
    if data.get("rsp_code") != 0:
        print(f"❌ 错误: {data.get('rsp_message')}")
        return

    markets = data.get("data", [])
    print(f"\n📋 交易所列表 ({len(markets)} 个)\n")
    print(f"{'交易所ID':<10} {'名称':<20} {'简称':<8} {'时区'}")
    print("-" * 50)
    for m in markets:
        print(
            f"{m.get('ExchangeID', ''):<10} {m.get('ExchangeName', ''):<20} "
            f"{m.get('ShortName', ''):<8} UTC+{m.get('TimeZone', 8)}"
        )


def get_prices(instruments: str = "", exchanges: str = "", types: str = "futures", limit: int = 10) -> None:
    params = {"types": types, "limit": limit}
    if instruments:
        params["instruments"] = instruments
    if exchanges:
        params["exchanges"] = exchanges
    url = f"{BASE_URL}/prices?{urllib.parse.urlencode(params)}"
    data = get(url)
    if data.get("rsp_code") != 0:
        print(f"❌ 错误: {data.get('rsp_message')}")
        return

    prices = data.get("data", [])
    print(f"\n📋 实时行情 ({len(prices)} 条)\n")
    print(f"{'合约代码':<12} {'交易所':<8} {'最新价':<12} {'结算价':<12} {'持仓量':<10} {'涨跌%'}")
    print("-" * 70)
    for p in prices:
        last = p.get("LastPrice") or p.get("ClosePrice", "-")
        settle = p.get("SettlementPrice", "-")
        oi = p.get("OpenInterest", "-")
        chg = p.get("ChangeRate") or p.get("Change", "-")
        if isinstance(chg, (int, float)) and chg != "-":
            chg = f"{chg:+.2f}%"
        print(
            f"{p.get('InstrumentID', ''):<12} {p.get('ExchangeID', ''):<8} "
            f"{last:>12} {settle:>12} {oi:>10} {chg}"
        )


def main():
    parser = argparse.ArgumentParser(description="OpenCTP 数据查询")
    parser.add_argument("--products", "-p", type=str, default=None,
                        help="品种列表 (types: futures/option/stock, 默认 futures)")
    parser.add_argument("--instruments", "-i", type=str, default=None,
                        help="合约详情，如 au,rb,IF")
    parser.add_argument("--times", "-t", type=str, default=None,
                        help="交易时段，如 ag,au,IF")
    parser.add_argument("--markets", "-m", action="store_true", help="交易所列表")
    parser.add_argument("--prices", type=str, default=None,
                        help="实时行情合约列表，如 au2608,rb2610")
    parser.add_argument("--exchanges", "-e", type=str, default="",
                        help="交易所过滤，如 SHFE,DCE")
    parser.add_argument("--limit", "-l", type=int, default=10, help="行情返回条数 (默认10)")
    parser.add_argument("--all-futures", "-a", action="store_true",
                        help="国内期货全品种合约详情")
    args = parser.parse_args()

    if args.markets:
        list_markets()
    elif args.products is not None:
        list_products(types=args.products or "futures")
    elif args.instruments is not None:
        list_instruments(products=args.instruments)
    elif args.times is not None:
        list_times(products=args.times)
    elif args.prices is not None:
        get_prices(instruments=args.prices, exchanges=args.exchanges, limit=args.limit)
    elif args.all_futures:
        print("⏳ 查询国内期货全品种合约详情（保证金/手续费/到期日）...")
        list_instruments(markets="SHFE,DCE,CZCE,CFFEX,INE,GFEX")
    else:
        parser.print_help()
        print("\n📌 常用示例:")
        print("  python openctp_query.py --markets              # 交易所列表")
        print("  python openctp_query.py --products             # 期货全部品种")
        print("  python openctp_query.py -i au,rb,IF           # 黄金/螺纹/沪深300合约详情")
        print("  python openctp_query.py -t ag,au              # 白银/黄金交易时段")
        print("  python openctp_query.py --prices au2608      # 黄金主力实时行情")
        print("  python openctp_query.py -a                    # 国内期货全品种合约详情")


if __name__ == "__main__":
    main()
