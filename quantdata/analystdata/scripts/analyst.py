#!/usr/bin/env python3
"""
A股分析师一致预期数据模块

数据源:
  - stock_profit_forecast_em: A股分析师一致预期（盈利预测、评级分布）
  - stock_analyst_detail_em: 分析师明细数据

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


def fetch_forecast(json_output: bool = False):
    """获取 A股分析师一致预期（盈利预测+评级分布）"""
    df = ak.stock_profit_forecast_em()
    df.columns = [c.strip() for c in df.columns]

    # 重命名字段为英文，方便下游处理
    df.rename(columns={
        "序号": "rank",
        "代码": "symbol",
        "名称": "name",
        "研报数": "report_count",
        "机构投资评级(近六个月)-买入": "rating_buy",
        "机构投资评级(近六个月)-增持": "rating_hold",
        "机构投资评级(近六个月)-中性": "rating_neutral",
        "机构投资评级(近六个月)-减持": "rating_reduce",
        "机构投资评级(近六个月)-卖出": "rating_sell",
        "2025预测每股收益": "eps_2025e",
        "2026预测每股收益": "eps_2026e",
        "2027预测每股收益": "eps_2027e",
        "2028预测每股收益": "eps_2028e",
    }, inplace=True)

    if json_output:
        records = df.to_dict(orient="records")
        print(json.dumps(records, ensure_ascii=False, default=str))
    else:
        print(f"\n📊 A股分析师一致预期（共 {len(df)} 只股票）")
        print(f"{'代码':<8} {'名称':<12} {'研报数':>6} {'买入':>5} {'增持':>5} "
              f"{'EPS-25e':>10} {'EPS-26e':>10} {'EPS-27e':>10}")
        print("-" * 80)
        for _, row in df.head(30).iterrows():
            print(f"{row['symbol']:<8} {row['name']:<12} "
                  f"{int(row['report_count']):>6} "
                  f"{int(row['rating_buy']) if pd.notna(row['rating_buy']) else 0:>5} "
                  f"{int(row['rating_hold']) if pd.notna(row['rating_hold']) else 0:>5} "
                  f"{row['eps_2025e']:>10.2f}" if pd.notna(row['eps_2025e']) else "N/A" 
                  f" {row['eps_2026e']:>10.2f}" if pd.notna(row['eps_2026e']) else "N/A"
                  f" {row['eps_2027e']:>10.2f}" if pd.notna(row['eps_2027e']) else "N/A")
        print(f"\n... 共 {len(df)} 只股票（仅展示前 30 只）")

    return df


def fetch_detail(symbol: str, json_output: bool = False):
    """获取指定股票的详细分析师研报数据"""
    try:
        df = ak.stock_analyst_detail_em(symbol=symbol)
        if json_output:
            records = df.head(20).to_dict(orient="records")
            print(json.dumps(records, ensure_ascii=False, default=str))
        else:
            print(f"\n📋 {symbol} 分析师研报明细（前 20 条）")
            print(df.head(20).to_string(index=False))
        return df
    except Exception as e:
        print(f"查询 {symbol} 明细失败: {e}", file=sys.stderr)
        return None


def main():
    parser = argparse.ArgumentParser(
        description="A股分析师一致预期",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  python analyst.py forecast              # 分析师一致预期
  python analyst.py forecast --json       # JSON 输出
  python analyst.py detail 600519         # 贵州茅台研报明细
        """,
    )
    subparsers = parser.add_subparsers(dest="command", help="子命令")

    # forecast
    p_forecast = subparsers.add_parser("forecast", help="分析师一致预期")
    p_forecast.add_argument("--json", action="store_true", help="JSON 输出")

    # detail
    p_detail = subparsers.add_parser("detail", help="个股研报明细")
    p_detail.add_argument("symbol", type=str, help="股票代码，如 600519")

    args = parser.parse_args()

    if args.command == "forecast":
        fetch_forecast(json_output=args.json)
    elif args.command == "detail":
        fetch_detail(symbol=args.symbol, json_output=args.json)
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
