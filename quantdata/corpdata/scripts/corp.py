#!/usr/bin/env python3
"""
A股公司事件数据模块

数据源:
  - stock_share_hold_change_sse: 上交所董监高增减持
  - stock_share_hold_change_szse: 深交所董监高增减持
  - stock_add_stock: 增发（定向增发）明细

依赖: akshare, pandas
"""

import argparse
import json
import sys

try:
    import akshare as ak
    import pandas as pd
except ImportError as e:
    print(f"缺少依赖: {e}", file=sys.stderr)
    print("请运行: pip install akshare pandas", file=sys.stderr)
    sys.exit(1)


def fetch_share_change(market: str = "sse", json_output: bool = False):
    """获取董监高增减持数据"""
    if market == "sse":
        try:
            df = ak.stock_share_hold_change_sse()
        except Exception as e:
            print(f"获取上交所增减持失败: {e}", file=sys.stderr)
            return None
        market_name = "上交所"
    elif market == "szse":
        try:
            df = ak.stock_share_hold_change_szse()
        except Exception as e:
            print(f"获取深交所增减持失败: {e}", file=sys.stderr)
            return None
        market_name = "深交所"
    else:
        print(f"不支持的交易所: {market}（支持: sse, szse）", file=sys.stderr)
        return None

    if json_output:
        records = df.to_dict(orient="records")
        print(json.dumps(records, ensure_ascii=False, default=str))
    else:
        print(f"\n📋 {market_name}董监高增减持（共 {len(df)} 条记录）")
        print(f"{'代码':<8} {'名称':<12} {'姓名':<8} {'职务':<12} "
              f"{'变动前':>10} {'变动数':>10} {'后持股':>10} {'原因':<12} {'日期':<12}")
        print("-" * 100)
        for _, row in df.head(20).iterrows():
            print(f"{str(row.get('公司代码', '')):<8} "
                  f"{str(row.get('公司名称', '')):<12} "
                  f"{str(row.get('姓名', '')):<8} "
                  f"{str(row.get('职务', '')):<12} "
                  f"{str(row.get('本次变动前持股数', '')):>10} "
                  f"{str(row.get('变动数', '')):>10} "
                  f"{str(row.get('变动后持股数', '')):>10} "
                  f"{str(row.get('变动原因', '')):<12} "
                  f"{str(row.get('变动日期', '')):<12}")
        print(f"\n... 共 {len(df)} 条记录（仅展示前 20 条）")

    return df


def fetch_placement(symbol: str, json_output: bool = False):
    """获取定向增发明细"""
    try:
        df = ak.stock_add_stock(symbol=symbol)
        if json_output:
            records = df.to_dict(orient="records")
            print(json.dumps(records, ensure_ascii=False, default=str))
        else:
            print(f"\n📋 {symbol} 增发明细")
            if df.empty:
                print("  无增发记录")
            else:
                print(df.to_string(index=False))
        return df
    except Exception as e:
        print(f"获取 {symbol} 增发信息失败: {e}", file=sys.stderr)
        return None


def main():
    parser = argparse.ArgumentParser(
        description="A股公司事件数据",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  python corp.py share_change --market sse       # 上交所增减持
  python corp.py share_change --market szse      # 深交所增减持
  python corp.py share_change --market sse --json
  python corp.py placement 600519                # 定增明细
        """,
    )
    subparsers = parser.add_subparsers(dest="command", help="子命令")

    # share_change
    p_sc = subparsers.add_parser("share_change", help="董监高增减持")
    p_sc.add_argument("--market", choices=["sse", "szse"], default="sse",
                       help="交易所: sse(上交所), szse(深交所)")
    p_sc.add_argument("--json", action="store_true", help="JSON 输出")

    # placement
    p_pl = subparsers.add_parser("placement", help="定向增发")
    p_pl.add_argument("symbol", type=str, help="股票代码，如 600519")
    p_pl.add_argument("--json", action="store_true", help="JSON 输出")

    args = parser.parse_args()

    if args.command == "share_change":
        fetch_share_change(market=args.market, json_output=args.json)
    elif args.command == "placement":
        fetch_placement(symbol=args.symbol, json_output=args.json)
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
