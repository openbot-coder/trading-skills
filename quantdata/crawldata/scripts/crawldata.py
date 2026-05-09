#!/usr/bin/env python3
"""
CrawlData - 财经爬虫数据工具
整合腾讯财经(股票/指数/国际期货) + 新浪财经(中国期货)
"""

import argparse
import sys
from get_quote import fetch_quotes, print_simple, print_detail, print_json


def main():
    parser = argparse.ArgumentParser(
        description="CrawlData - 财经爬虫数据工具",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  # 查询单个股票
  python crawldata.py quote sh600000
  
  # 查询中国期货
  python crawldata.py quote M0 RB0 AU0
  
  # 查询国际期货
  python crawldata.py quote hf_GC hf_CL
  
  # 混合查询
  python crawldata.py quote sh600000 hf_GC M0 NF_IF2508
  
  # 显示详细信息
  python crawldata.py quote M0 --detail
  
  # JSON输出
  python crawldata.py quote hf_GC M0 --json
  
常用代码:
  指数: sh000001(上证指数), sh000300(沪深300), sz399001(深证成指)
  股票: sh600000(浦发), sh600519(茅台), sz000001(平安)
  国际期货: hf_GC(黄金), hf_CL(原油), hf_SI(白银)
  中国期货: M0(豆粕), RB0(螺纹), AU0(黄金), NF_IF2508(沪深300期指)
        """
    )
    
    subparsers = parser.add_subparsers(title="命令", dest="command")
    
    # quote命令
    quote_parser = subparsers.add_parser("quote", help="查询行情")
    quote_parser.add_argument("codes", nargs="+", help="代码列表")
    quote_parser.add_argument("--detail", action="store_true", help="详细输出")
    quote_parser.add_argument("--json", action="store_true", help="JSON输出")
    
    args = parser.parse_args()
    
    if args.command == "quote":
        quotes = fetch_quotes(args.codes)
        if not quotes:
            print("未获取到数据")
            sys.exit(1)
        
        if args.json:
            print_json(quotes)
        elif args.detail:
            print_detail(quotes)
        else:
            print_simple(quotes)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
