#!/usr/bin/env python3
"""
宏观深度采集工具 — MacroMonitor
=================================
用于经济日历、政策动态等非结构化数据的浏览器采集辅助。
仅当 macro.py 爬虫和 AKShare 都无法获取数据时使用。

数据源优先级: 爬虫 > AKShare > 浏览器（本脚本）
优先使用: python scripts/macro.py query <region> <indicator>

用法:
    python scripts/macro_monitor.py calendar        # 经济日历
    python scripts/macro_monitor.py policy          # 政策动态
    python scripts/macro_monitor.py list            # 列出采集源

作者: macrodata team
创建日期: 2026-05-14
"""

import argparse
import logging
import sys
from datetime import datetime

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(name)s:%(lineno)d - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger('macro_monitor')

# ============================================================
# 数据源配置
# ============================================================

SOURCES = {
    "tradingeconomics": {
        "name": "Trading Economics",
        "url": "https://tradingeconomics.com/calendar",
        "description": "全球经济日历",
        "focus": "高重要性事件（红色标记）",
        "fields": "时间、国家、事件、实际值、预期值、前值",
        "priority": 1,
    },
    "fred": {
        "name": "FRED (美联储)",
        "url": "https://fred.stlouisfed.org/releases",
        "description": "美联储经济数据发布",
        "focus": "最新数据发布",
        "priority": 2,
    },
    "stats_gov_cn": {
        "name": "国家统计局",
        "url": "http://www.stats.gov.cn/",
        "description": "中国宏观经济数据",
        "focus": "最新数据发布栏目",
        "priority": 3,
    },
    "pbc": {
        "name": "央行官网",
        "url": "http://www.pbc.gov.cn/",
        "description": "货币政策、利率、流动性数据",
        "focus": "新闻发布、政策解读",
        "priority": 4,
    },
    "csrc": {
        "name": "证监会官网",
        "url": "http://www.csrc.gov.cn/",
        "description": "监管政策发布",
        "focus": "最新政策法规",
        "priority": 5,
    },
    "cls": {
        "name": "财联社",
        "url": "https://www.cls.cn/",
        "description": "实时金融新闻",
        "focus": "宏观新闻头条",
        "priority": 6,
    },
    "wallstreetcn": {
        "name": "华尔街见闻",
        "url": "https://wallstreetcn.com/",
        "description": "市场资讯与分析",
        "focus": "宏观分析、市场解读",
        "priority": 7,
    },
}


def list_sources():
    """列出所有浏览器采集源"""
    print(f"\n{'=' * 70}")
    print(f"  MacroMonitor 浏览器采集数据源")
    print(f"  使用场景: 爬虫/AKShare 无法覆盖的数据（经济日历、政策、新闻等）")
    print(f"{'=' * 70}")

    for key, src in sorted(SOURCES.items(), key=lambda x: x[1]["priority"]):
        print(f"\n  {src['priority']}. {src['name']}")
        print(f"     URL: {src['url']}")
        print(f"     说明: {src['description']}")
        print(f"     关注: {src['focus']}")

    print(f"\n{'=' * 70}")
    print(f"  [提示] 优先使用 macro.py 爬虫，浏览器仅作为最后手段")
    print(f"  [提示] 每个数据源采集后需整理成结构化格式")
    print(f"{'=' * 70}\n")


def print_calendar_guide():
    """打印经济日历采集指南"""
    print(f"\n{'=' * 70}")
    print(f"  📅 经济日历采集指南")
    print(f"  采集过去 24 小时发布的宏观经济数据和事件")
    print(f"{'=' * 70}")

    print(f"""
采集步骤:

1. 访问 Trading Economics 经济日历:
   {SOURCES['tradingeconomics']['url']}
   - 关注高重要性事件（红色标记）
   - 字段: {SOURCES['tradingeconomics']['fields']}

2. 访问 FRED 美联储数据发布:
   {SOURCES['fred']['url']}
   - 关注最新数据发布

3. 访问国家统计局:
   {SOURCES['stats_gov_cn']['url']}
   - 重点关注: GDP、CPI、PPI、PMI、工业增加值、社零

4. 访问央行官网:
   {SOURCES['pbc']['url']}
   - 重点关注: LPR利率、MLF操作、公开市场操作、货币政策报告

5. 访问证监会官网:
   {SOURCES['csrc']['url']}
   - 重点关注: 监管政策、市场规则变化

6. 访问财联社 / 华尔街见闻:
   - 收集宏观新闻头条

整理格式:
{_format_template()}
""")


def print_policy_guide():
    """打印政策动态采集指南"""
    print(f"\n{'=' * 70}")
    print(f"  📜 政策动态采集指南")
    print(f"  采集过去 24 小时发布的政策信息")
    print(f"{'=' * 70}")

    print(f"""
采集步骤:

1. 央行官网: {SOURCES['pbc']['url']}
   - 货币政策工具操作
   - 利率调整
   - 流动性管理

2. 证监会官网: {SOURCES['csrc']['url']}
   - 市场准入政策
   - 交易规则变更
   - 投资者保护

3. 财联社: {SOURCES['cls']['url']}
   - 政策解读
   - 监管动态

4. 国家统计局: {SOURCES['stats_gov_cn']['url']}
   - 最新数据发布通知

整理格式:
{_format_policy_template()}
""")


def _format_template() -> str:
    return """
【经济日历 - {日期}】

🌍 国际数据
- [数据名称] [实际值] [预期值] [前值] [影响说明]
  💡 [科普解释]

🇨🇳 国内数据
- [数据名称] [实际值] [预期值] [前值] [影响说明]
  💡 [科普解释]
"""


def _format_policy_template() -> str:
    return """
【政策动态 - {日期}】

📜 货币政策
- [政策名称] - [主要内容]

📜 监管政策
- [政策名称] - [主要内容]

📰 重要资讯
- [标题] - [简要说明]
"""


def main():
    parser = argparse.ArgumentParser(
        description="MacroMonitor - 宏观深度采集工具（浏览器兜底）",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  python scripts/macro_monitor.py list              # 列出采集源
  python scripts/macro_monitor.py calendar          # 经济日历指南
  python scripts/macro_monitor.py policy            # 政策动态指南

注意:
  优先使用 macro.py 的爬虫功能，浏览器仅作为最后手段。
  如果 macro.py 无法获取某指标，可尝试浏览器手动采集。
        """
    )

    subparsers = parser.add_subparsers(dest="command", help="子命令")

    subparsers.add_parser("list", help="列出所有浏览器采集源")
    subparsers.add_parser("calendar", help="经济日历采集指南")
    subparsers.add_parser("policy", help="政策动态采集指南")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return

    if args.command == "list":
        list_sources()
    elif args.command == "calendar":
        print_calendar_guide()
    elif args.command == "policy":
        print_policy_guide()


if __name__ == "__main__":
    main()
