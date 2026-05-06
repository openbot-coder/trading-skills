#!/usr/bin/env python3
"""
获取A股K线数据

使用方式:
    python get_kline.py sh.600000              # 获取浦发银行
    python get_kline.py sz.000001 --start 2024-01-01  # 指定开始日期
    python get_kline.py sh.600000 --frequency d --top 60  # 日线，显示最近60天
"""

import argparse
import sys
from datetime import datetime, timedelta

try:
    import baostock as bs
except ImportError:
    print("请先安装: pip install baostock")
    sys.exit(1)


def get_kline(
    code: str,
    start_date: str = None,
    end_date: str = None,
    frequency: str = "d",
    adjustflag: str = "3",
):
    """获取K线数据"""
    # 如果没有指定日期，默认获取最近一年
    if end_date is None:
        end_date = datetime.now().strftime("%Y-%m-%d")
    if start_date is None:
        start_date = (datetime.now() - timedelta(days=365)).strftime("%Y-%m-%d")

    try:
        lg = bs.login()
        if lg.error_code != "0":
            print(f"登录失败: {lg.error_msg}")
            return None

        rs = bs.query_history_k_data_plus(
            code,
            "date,code,open,high,low,close,preclose,volume,amount,adjustflag,turn,tradestatus,pctChg,isST",
            start_date=start_date,
            end_date=end_date,
            frequency=frequency,
            adjustflag=adjustflag,
        )

        data_list = []
        while (rs.error_code == "0") & rs.next():
            data_list.append(rs.get_row_data())

        bs.logout()
        return data_list
    except Exception as e:
        print(f"获取K线失败: {e}")
        try:
            bs.logout()
        except:
            pass
        return None


def format_data(data_list, code: str, top_n: int = None):
    """格式化输出"""
    if not data_list:
        print("无数据")
        return

    if top_n and len(data_list) > top_n:
        data_list = data_list[-top_n:]

    print(f"\n{'='*110}")
    print(f"K线数据: {code}")
    print(f"{'='*110}")
    print(
        f"{'日期':<12} {'开盘':>8} {'最高':>8} {'最低':>8} {'收盘':>8} {'昨收':>8} {'成交量':>12} {'成交额':>14} {'涨跌幅':>8} {'换手率':>8}"
    )
    print(f"{'-'*110}")

    for row in data_list:
        (
            date,
            code,
            open_p,
            high,
            low,
            close,
            preclose,
            volume,
            amount,
            adjustflag,
            turn,
            tradestatus,
            pctChg,
            isST,
        ) = row

        try:
            open_p = float(open_p) if open_p else 0
            high = float(high) if high else 0
            low = float(low) if low else 0
            close = float(close) if close else 0
            preclose = float(preclose) if preclose else 0
            volume = float(volume) if volume else 0
            amount = float(amount) if amount else 0
            pctChg = float(pctChg) if pctChg else 0
            turn = float(turn) if turn else 0
        except (ValueError, TypeError):
            pass

        print(
            f"{date:<12} {open_p:>8.2f} {high:>8.2f} {low:>8.2f} {close:>8.2f} {preclose:>8.2f} {volume:>12,.0f} {amount:>14,.0f} {pctChg:>7.2f}% {turn:>7.3f}%"
        )

    print(f"{'-'*110}")
    print(f"共 {len(data_list)} 条数据")


def main():
    parser = argparse.ArgumentParser(
        description="获取A股K线数据",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
    python get_kline.py sh.600000                          # 浦发银行，最近一年
    python get_kline.py sz.000001 --start 2024-01-01       # 平安银行，指定开始日期
    python get_kline.py sh.600000 --start 2023-01-01 --end 2023-12-31  # 指定时间范围
    python get_kline.py sh.600000 --frequency w --top 50    # 周线，显示最近50条
    python get_kline.py sh.600000 --frequency m --adjustflag 2  # 月线，前复权

参数说明:
    frequency: K线周期 (d=日, w=周, m=月, 5=5分钟, 15=15分钟, 30=30分钟, 60=60分钟)
    adjustflag: 复权类型 (1=后复权, 2=前复权, 3=不复权)
"""
    )
    parser.add_argument("code", help="股票代码 (例如: sh.600000, sz.000001)")
    parser.add_argument("--start", type=str, help="开始日期 (YYYY-MM-DD)")
    parser.add_argument("--end", type=str, help="结束日期 (YYYY-MM-DD)")
    parser.add_argument(
        "--frequency",
        type=str,
        default="d",
        help="K线周期 (默认: d=日线)",
    )
    parser.add_argument(
        "--adjustflag",
        type=str,
        default="3",
        help="复权类型 (默认: 3=不复权)",
    )
    parser.add_argument(
        "--top",
        type=int,
        default=None,
        help="只显示最后N条数据",
    )
    args = parser.parse_args()

    data_list = get_kline(
        args.code,
        start_date=args.start,
        end_date=args.end,
        frequency=args.frequency,
        adjustflag=args.adjustflag,
    )
    format_data(data_list, args.code, top_n=args.top)


if __name__ == "__main__":
    main()
