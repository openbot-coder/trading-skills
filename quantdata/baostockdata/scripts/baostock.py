#!/usr/bin/env python3
"""
Baostock A股数据查询脚本

使用方式:
    # K线数据
    python baostock.py kline sh.600000
    python baostock.py kline sh.600000 --start 2024-01-01 --frequency d --adjustflag 2

    # 财务数据
    python baostock.py profit sh.600000

    # 宏观经济数据
    python baostock.py macro deposit
    python baostock.py macro loan

所有命令都可以用 --help 查看详细用法
"""

import argparse
import sys
from datetime import datetime, timedelta

try:
    import baostock as bs
except ImportError:
    print("请先安装: pip install baostock")
    sys.exit(1)


def kline(code, start_date=None, end_date=None, frequency="d", adjustflag="3", top=None):
    """获取K线数据"""
    if not end_date:
        end_date = datetime.now().strftime("%Y-%m-%d")
    if not start_date:
        start_date = (datetime.now() - timedelta(days=365)).strftime("%Y-%m-%d")

    try:
        lg = bs.login()
        if lg.error_code != "0":
            print(f"登录失败: {lg.error_msg}")
            return

        fields = "date,code,open,high,low,close,preclose,volume,amount,adjustflag,turn,tradestatus,pctChg,isST"

        rs = bs.query_history_k_data_plus(
            code,
            fields,
            start_date=start_date,
            end_date=end_date,
            frequency=frequency,
            adjustflag=adjustflag,
        )

        data_list = []
        while (rs.error_code == "0") & rs.next():
            data_list.append(rs.get_row_data())

        bs.logout()

        if top and len(data_list) > top:
            data_list = data_list[-top:]

        print(f"\n{'='*130}")
        print(f"K线数据: {code} | 复权: {adjustflag} | 周期: {frequency}")
        print(f"时间范围: {start_date} ~ {end_date}")
        print("="*130)
        print(f"{'日期':<12}{'开盘':>9}{'最高':>9}{'最低':>9}{'收盘':>9}{'昨收':>9}{'成交量':>14}{'成交额':>15}{'涨跌':>8}{'换手率':>8}")
        print("-"*130)

        for row in data_list:
            (date, code, open_p, high, low, close, preclose, volume,
             amount, adj_flag, turn, tradestatus, pctChg, isST) = row)
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

                emoji = "📈" if pctChg > 0 else "📉" if pctChg < 0 else ""

                print(
                    f"{date:<12}"
                    f"{open_p:>9.2f}"
                    f"{high:>9.2f}"
                    f"{low:>9.2f}"
                    f"{close:>9.2f}"
                    f"{preclose:>9.2f}"
                    f"{volume:>14,.0f}"
                    f"{amount:>15,.0f}"
                    f"{pctChg:>+8.2f}% {emoji}"
                    f"{turn:>8.3f}%"
                )
            except (ValueError, TypeError):
                pass

        print("-"*130)
        print(f"共 {len(data_list)} 条数据")
        print("="*130)
    except Exception as e:
        print(f"查询失败: {e}")
        try:
            bs.logout()
        except:
            pass


def profit_data(code, year=2023, quarter=4):
    """获取财务数据"""
    try:
        lg = bs.login()
        if lg.error_code != "0":
            print(f"登录失败: {lg.error_msg}")
            return

        rs_profit = bs.query_profit_data(code=code, year=year, quarter=quarter)
        profit_list = []
        while (rs_profit.error_code == "0") & rs_profit.next():
            profit_list.append(rs_profit.get_row_data())

        bs.logout()

        print(f"\n{'='*100}")
        print(f"财务数据: {code} | {year}年 Q{quarter}")
        print("="*100)
        if profit_list:
            for row in profit_list:
                print(f"  发布日期: {row[1]}")
                print(f"  净利润: {row[6]}")
                print(f"  营业收入: {row[11]}")
                print(f"  ROE: {row[14]}")
                print(f"  销售毛利率: {row[13]}")
        else:
            print("  无数据")
        print("="*100)
    except Exception as e:
        print(f"查询失败: {e}")
        try:
            bs.logout()
        except:
            pass


def macro_data(data_type="deposit"):
    """获取宏观经济数据"""
    try:
        lg = bs.login()
        if lg.error_code != "0":
            print(f"登录失败: {lg.error_msg}")
            return

        rs = None
        if data_type == "deposit":
            rs = bs.query_deposit_rate_data()
            title = "存款利率"
        elif data_type == "loan":
            rs = bs.query_loan_rate_data()
            title = "贷款利率"
        elif data_type == "reserve":
            rs = bs.query_required_reserve_ratio_data()
            title = "存款准备金率"
        elif data_type == "money_month":
            rs = bs.query_money_supply_data_month()
            title = "货币供应量(月度)"
        elif data_type == "money_year":
            rs = bs.query_money_supply_data_year()
            title = "货币供应量(年度)"
        else:
            print(f"不支持的数据类型")
            bs.logout()
            return

        data_list = []
        while (rs.error_code == "0") & rs.next():
            data_list.append(rs.get_row_data())

        bs.logout()

        print(f"\n{'='*80}")
        print(f"宏观经济数据: {title}")
        print("="*80)
        if data_list:
            for row in data_list[-20:]:
                print(f"  {row}")
        else:
            print("  无数据")
        print("="*80)
    except Exception as e:
        print(f"查询失败: {e}")
        try:
            bs.logout()
        except:
            pass


def main():
    parser = argparse.ArgumentParser(
        description="Baostock A股数据查询",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
    # K线数据
    python baostock.py kline sh.600000
    python baostock.py kline sh.600000 --start 2024-01-01 --frequency d --adjustflag 2

    # 财务数据
    python baostock.py profit sh.600000

    # 宏观经济数据
    python baostock.py macro deposit
    python baostock.py macro loan
        """
    )
    subparsers = parser.add_subparsers(title="命令", dest="command")

    # K线查询
    kline_parser = subparsers.add_parser("kline", help="获取K线数据")
    kline_parser.add_argument("code", help="股票代码 (如: sh.600000, sz.000001)")
    kline_parser.add_argument("--start", help="开始日期 (YYYY-MM-DD)")
    kline_parser.add_argument("--end", help="结束日期 (YYYY-MM-DD)")
    kline_parser.add_argument("--frequency", default="d", help="K线周期 (d=日,w=周,m=月,5=5分钟等)")
    kline_parser.add_argument("--adjustflag", default="3", help="复权类型 (1=后复权,2=前复权,3=不复权)")
    kline_parser.add_argument("--top", type=int, default=None, help="只显示最后N条数据")

    # 财务数据
    profit_parser = subparsers.add_parser("profit", help="获取财务数据")
    profit_parser.add_argument("code", help="股票代码")
    profit_parser.add_argument("--year", type=int, default=2023, help="年份")
    profit_parser.add_argument("--quarter", type=int, default=4, help="季度 (1-4)")

    # 宏观数据
    macro_parser = subparsers.add_parser("macro", help="获取宏观经济数据")
    macro_parser.add_argument("data_type", choices=["deposit", "loan", "reserve", "money_month", "money_year"], help="数据类型 (deposit=存款, loan=贷款, reserve=准备金, money_month=月度货币, money_year=年度货币)")

    args = parser.parse_args()

    if args.command == "kline":
        kline(args.code, start_date=args.start, end_date=args.end,
              frequency=args.frequency, adjustflag=args.adjustflag,
              top=args.top)
    elif args.command == "profit":
        profit_data(args.code, year=args.year, quarter=args.quarter)
    elif args.command == "macro":
        macro_data(args.data_type)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
