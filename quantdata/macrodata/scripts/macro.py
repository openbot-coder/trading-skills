#!/usr/bin/env python3
"""
宏观数据查询工具 — MacroData
=============================
从东方财富、金十数据等公开数据源爬取宏观经济数据，AKShare 作为兜底。

数据源优先级：爬虫（requests）→ AKShare → 浏览器（macro_monitor.py）

用法:
    python scripts/macro.py list                           # 列出所有指标
    python scripts/macro.py query <region> <indicator>     # 查询指标
    python scripts/macro.py query cn cpi                   # 中国 CPI
    python scripts/macro.py query us nonfarm               # 美国非农
    python scripts/macro.py report                         # 宏观报告

作者: macrodata team
创建日期: 2026-05-14
"""

import argparse
import json
import sys
import time
import logging
from datetime import datetime
from typing import List, Dict, Optional, Any

try:
    import requests
except ImportError:
    print("错误：需要 requests 库，请运行 pip install requests")
    sys.exit(1)

# ============================================================
# 日志配置
# ============================================================
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(name)s:%(lineno)d - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger('macro')

# ============================================================
# 数据源配置
# ============================================================

# 东方财富数据中心 API 地址
EASTMONEY_API = "https://datacenter-web.eastmoney.com/api/data/v1/get"

# 金十数据 API 地址
JIN10_API = "https://datacenter-api.jin10.com/reports/list_v2"
JIN10_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Referer": "https://datacenter.jin10.com/",
    "Accept": "application/json, text/plain, */*",
    "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
    "x-app-id": "rU6QIu7JHe2gOUeR",
    "x-csrf-token": "x-csrf-token",
    "x-version": "1.0.0",
}

# 东方财富宏观指标配置
# reportName 参考: https://github.com/akfamily/akshare/blob/main/akshare/economic/macro_china.py
# 数据源: http://data.eastmoney.com/cjsj/
CN_INDICATORS = {
    "cpi": {
        "name": "中国 CPI",
        "report_name": "RPT_ECONOMY_CPI",
        "description": "居民消费价格指数（同比），月频",
        "source": "东方财富"
    },
    "ppi": {
        "name": "中国 PPI",
        "report_name": "RPT_ECONOMY_PPI",
        "description": "工业生产者出厂价格指数（同比），月频",
        "source": "东方财富"
    },
    "pmi": {
        "name": "中国 PMI",
        "report_name": "RPT_ECONOMY_PMI",
        "description": "采购经理指数（制造业），月频",
        "source": "东方财富"
    },
    "gdp": {
        "name": "中国 GDP",
        "report_name": "RPT_ECONOMY_GDP",
        "description": "国内生产总值（同比），季频",
        "source": "东方财富"
    },
    "m2": {
        "name": "中国 M2",
        "report_name": "RPT_ECONOMY_CURRENCY_SUPPLY",
        "description": "广义货币供应量（同比），月频",
        "source": "东方财富"
    },
    "fixed_invest": {
        "name": "固定资产投资",
        "report_name": "RPT_ECONOMY_ASSET_INVEST",
        "description": "城镇固定资产投资（累计同比），月频",
        "source": "东方财富"
    },
    "trade": {
        "name": "进出口总额",
        "report_name": "RPT_ECONOMY_CUSTOMS",
        "description": "海关进出口金额及同比，月频",
        "source": "东方财富"
    },
    "fx_reserves": {
        "name": "外汇与黄金储备",
        "report_name": "RPT_ECONOMY_GOLD_CURRENCY",
        "description": "国家外汇/黄金储备，月频",
        "source": "东方财富"
    },
    "consumer_confidence": {
        "name": "消费者信心指数",
        "report_name": "RPT_ECONOMY_FAITH_INDEX",
        "description": "消费者信心/满意/预期指数，月频",
        "source": "东方财富"
    },
    "tax_revenue": {
        "name": "全国税收收入",
        "report_name": "RPT_ECONOMY_TAX",
        "description": "全国税收收入（累计），月频",
        "source": "东方财富"
    },
    "new_house_price": {
        "name": "新房价指数",
        "report_name": "RPT_ECONOMY_HOUSE_PRICE",
        "description": "新建商品住宅价格指数（同比），月频",
        "source": "东方财富"
    },
    "fdi": {
        "name": "外商直接投资",
        "report_name": "RPT_ECONOMY_FDI",
        "description": "外商直接投资数据，月频",
        "source": "东方财富"
    },
    "enterprise_boom": {
        "name": "企业景气指数",
        "report_name": "RPT_ECONOMY_BOOM_INDEX",
        "description": "企业景气及企业家信心指数，季频",
        "source": "东方财富"
    },
}

# 金十数据美国宏观指标配置
# API: https://datacenter-api.jin10.com/reports/list_v2
# attr_id 参考: https://github.com/akfamily/akshare/blob/main/akshare/economic/macro_usa.py
US_INDICATORS = {
    "nonfarm": {
        "name": "美国非农就业",
        "attr_id": "33",
        "description": "非农就业人数变化（万人），月频",
        "source": "金十数据"
    },
    "cpi": {
        "name": "美国 CPI",
        "attr_id": "9",
        "description": "CPI 月率（%），月频",
        "source": "金十数据"
    },
    "unemployment": {
        "name": "美国失业率",
        "attr_id": "47",
        "description": "失业率（%），月频",
        "source": "金十数据"
    },
    "gdp": {
        "name": "美国 GDP",
        "attr_id": "53",
        "description": "国内生产总值（年化季率），季频",
        "source": "金十数据"
    },
    "retail_sales": {
        "name": "美国零售销售",
        "attr_id": "39",
        "description": "零售销售月率（%），月频",
        "source": "金十数据"
    },
    "ism_pmi": {
        "name": "美国 ISM 制造业 PMI",
        "attr_id": "28",
        "description": "ISM 制造业采购经理人指数，月频",
        "source": "金十数据"
    },
    "initial_jobless": {
        "name": "美国初请失业金",
        "attr_id": "44",
        "description": "初请失业金人数（万人），周频",
        "source": "金十数据"
    },
    "core_cpi": {
        "name": "美国核心 CPI",
        "attr_id": "6",
        "description": "核心 CPI 月率（%），月频",
        "source": "金十数据"
    },
}

# AKShare 作为兜底
AKSHARE_INDICATORS = {
    "cn": {
        "cpi": {"func": "macro_china_cpi_yearly", "desc": "中国 CPI 年率"},
        "ppi": {"func": "macro_china_ppi_yearly", "desc": "中国 PPI 年率"},
        "pmi": {"func": "macro_china_pmi_yearly", "desc": "中国官方制造业 PMI"},
        "gdp": {"func": "macro_china_gdp_yearly", "desc": "中国 GDP 年率"},
        "m2": {"func": "macro_china_m2_yearly", "desc": "中国 M2 年率"},
        "non_man_pmi": {"func": "macro_china_non_man_pmi", "desc": "中国非制造业 PMI"},
        "industrial": {"func": "macro_china_industrial_production_yoy", "desc": "中国工业增加值年率"},
        "lpr": {"func": "macro_china_lpr", "desc": "中国 LPR"},
    },
    "us": {
        "cpi": {"func": "macro_usa_cpi_yoy", "desc": "美国 CPI 年率"},
        "nonfarm": {"func": "macro_usa_non_farm", "desc": "美国非农就业"},
        "unemployment": {"func": "macro_usa_unemployment_rate", "desc": "美国失业率"},
        "ppi": {"func": "macro_usa_ppi", "desc": "美国 PPI"},
        "adp": {"func": "macro_usa_adp_employment", "desc": "美国 ADP 就业"},
        "ism_pmi": {"func": "macro_usa_ism_pmi", "desc": "美国 ISM 制造业 PMI"},
        "pce": {"func": "macro_usa_core_pce_price", "desc": "美国核心 PCE"},
    },
}

REGIONS = {
    "cn": "中国",
    "us": "美国",
}


def fetch_eastmoney(indicator_config: Dict, days: int = 10) -> Optional[Dict]:
    """从东方财富数据中心获取宏观数据

    参考: http://data.eastmoney.com/cjsj/
    reportName 参考: https://github.com/akfamily/akshare/blob/main/akshare/economic/macro_china.py
    """
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "Referer": "http://data.eastmoney.com/cjsj/",
        "Accept": "application/json",
    }
    params = {
        "reportName": indicator_config["report_name"],
        "columns": "ALL",
        "pageNumber": 1,
        "pageSize": min(days, 30),
        "sortTypes": -1,
        "sortColumns": "REPORT_DATE",
        "source": "WEB",
        "client": "WEB",
        "_": int(time.time() * 1000),
    }

    try:
        resp = requests.get(EASTMONEY_API, params=params, headers=headers, timeout=15)
        resp.raise_for_status()
        data = resp.json()

        if data.get("code") != 0 or not data.get("result"):
            logger.warning(f"东方财富 API 返回异常({indicator_config['name']}): {data.get('code')} - {data.get('message', '')}")
            return None

        rows = data["result"].get("data", [])
        if not rows:
            logger.warning(f"东方财富 API 返回空数据({indicator_config['name']})")
            return None

        values = []
        for row in rows[:days]:
            values.append(_format_eastmoney_row(row))

        return {
            "indicator": indicator_config["name"],
            "source": "东方财富",
            "data": values,
        }

    except requests.RequestException as e:
        logger.warning(f"东方财富 API 请求失败({indicator_config['name']}): {e}")
        return None
    except (ValueError, KeyError) as e:
        logger.warning(f"东方财富数据解析失败({indicator_config['name']}): {e}")
        return None


def _format_eastmoney_row(row: Dict) -> Dict:
    """格式化东方财富数据行

    东方财富列名约定:
      - *_SAME = 同比 (NATIONAL_SAME, BASE_SAME, SUM_SAME, MAKE_SAME)
      - *_BASE = 当月值/指数 (NATIONAL_BASE, BASE, DOMESTICL_PRODUCT_BASE)
      - *_SEQUENTIAL = 环比 (NATIONAL_SEQUENTIAL, BASIC_CURRENCY_SEQUENTIAL)
      - *_ACCUMULATE = 累计值 (NATIONAL_ACCUMULATE, BASE_ACCUMULATE)
      - *_INDEX = PMI指数 (MAKE_INDEX, NMAKE_INDEX)
    """
    result = {}

    # 日期字段
    for date_field in ["REPORT_DATE", "TRADE_DATE", "END_DATE", "TIME"]:
        if date_field in row and row[date_field]:
            result["date"] = str(row[date_field])[:10]
            break
    result.setdefault("date", "—")

    # 识别列名分类
    # 注意: 字段名可能直接叫 "BASE"（不以下划线开头）
    all_keys = list(row.keys())

    index_fields = [k for k in all_keys if k.endswith("_INDEX") and row[k] is not None]
    # _SAME 作为同比指标，对所有有同比含义的列
    same_fields = [k for k in all_keys if k.endswith("_SAME") and row[k] is not None]
    # _BASE 或正好叫 BASE
    base_fields = [k for k in all_keys if (k.endswith("_BASE") or k == "BASE") and row[k] is not None]
    amount_fields = [k for k in all_keys if k.endswith("_AMOUNT") and row[k] is not None]
    sequential_fields = [k for k in all_keys if k.endswith("_SEQUENTIAL") and row[k] is not None]
    accumulate_fields = [k for k in all_keys if k.endswith("_ACCUMULATE") and row[k] is not None]

    # 主数值选择策略:
    #   PMI 等: 取 _INDEX（绝对值比同比更受关注）
    #   CPI/GDP: 取 _SAME（用户更关注通胀率/GDP增速，而非指数值）
    #   PPI: 有 _SAME + BASE → 取 _SAME（同比2.8%比指数102.8更有意义）
    #   其他: 取 BASE / AMOUNT 等

    is_index_type = bool(index_fields)  # PMI 等指数型指标
    is_rate_type = bool(same_fields) and not bool(index_fields)  # CPI/GDP/PPI 等同比型

    if is_index_type:
        result["value"] = row[index_fields[0]]
        if same_fields:
            result["change"] = row[same_fields[0]]
    elif is_rate_type:
        # 同比型指标: 直接取 _SAME 作为主值
        result["value"] = row[same_fields[0]]
        # 环比/累计作为变动
        if sequential_fields:
            result["change"] = row[sequential_fields[0]]
        elif accumulate_fields:
            result["change"] = row[accumulate_fields[0]]
    elif base_fields:
        result["value"] = row[base_fields[0]]
    elif amount_fields:
        result["value"] = row[amount_fields[0]]
    else:
        result["value"] = "—"

    # 如果变动还未设置，尝试环比或累计
    if result.get("change") in (None, "—"):
        if sequential_fields:
            result["change"] = row[sequential_fields[0]]
        elif accumulate_fields:
            result["change"] = row[accumulate_fields[0]]
        else:
            result["change"] = "—"

    return result


def fetch_jin10(indicator_config: Dict, days: int = 10) -> Optional[Dict]:
    """从金十数据获取美国宏观数据

    API: https://datacenter-api.jin10.com/reports/list_v2
    返回格式: {"data": {"keys": [...], "values": [[date, actual, forecast, previous], ...]}}
    参考: https://github.com/akfamily/akshare/blob/main/akshare/economic/macro_usa.py
    """
    params = {
        "category": "ec",
        "attr_id": indicator_config["attr_id"],
        "max_date": "",
        "_": str(int(time.time() * 1000)),
    }

    try:
        resp = requests.get(JIN10_API, params=params, headers=JIN10_HEADERS, timeout=15)
        resp.raise_for_status()
        data = resp.json()

        values_raw = data.get("data", {}).get("values", []) if isinstance(data, dict) else []
        if not values_raw:
            logger.warning(f"金十数据返回空数据({indicator_config['name']})")
            return None

        # values[i] = [date, actual_value, forecast, previous]
        values = []
        for row in values_raw[:days]:
            if not isinstance(row, (list, tuple)):
                continue
            date_val = str(row[0])[:10] if row[0] else "—"
            actual = row[1] if len(row) > 1 and row[1] is not None else "—"
            forecast = row[2] if len(row) > 2 and row[2] is not None else "—"
            previous = row[3] if len(row) > 3 and row[3] is not None else "—"

            v = {
                "date": date_val,
                "value": actual,
                "expected": forecast,
                "previous": previous,
            }
            values.append(v)

        return {
            "indicator": indicator_config["name"],
            "source": "金十数据",
            "data": values,
        }

    except requests.RequestException as e:
        logger.warning(f"金十数据请求失败({indicator_config['name']}): {e}")
        return None
    except (ValueError, KeyError, TypeError) as e:
        logger.warning(f"金十数据解析失败({indicator_config['name']}): {e}")
        return None


def fetch_akshare(region: str, indicator: str, days: int = 10) -> Optional[Dict]:
    """AKShare 兜底查询"""
    try:
        import akshare as ak
    except ImportError:
        return {
            "indicator": f"{REGIONS.get(region, region)}/{indicator}",
            "source": "AKShare(未安装)",
            "error": "AKShare 未安装，请运行: pip install akshare",
            "data": []
        }

    indicators = AKSHARE_INDICATORS.get(region, {})
    if indicator not in indicators:
        return None

    info = indicators[indicator]
    try:
        func = getattr(ak, info["func"])
        df = func()

        if df is None or df.empty:
            return {"indicator": info["desc"], "source": "AKShare", "data": [], "error": "返回空数据"}

        values = []
        for _, row in df.head(days).iterrows():
            v = {}
            for col in df.columns:
                key = col.lower().replace(" ", "_").replace("-", "_")
                if "date" in key or "time" in key:
                    v["date"] = str(row[col])[:10]
                elif "value" in key or "price" in key or "rate" in key or "index" in key:
                    v["value"] = row[col]
            v.setdefault("date", "未知")
            v.setdefault("value", "—")
            values.append(v)

        return {"indicator": info["desc"], "source": "AKShare", "data": values}

    except Exception as e:
        return {"indicator": info["desc"], "source": "AKShare", "data": [], "error": str(e)}


# ============================================================
# 查询路由
# ============================================================

def query_indicator(region: str, indicator: str, days: int = 5, prefer_source: Optional[str] = None) -> Dict:
    """按优先级查询指标"""
    region_lower = region.lower()
    indicator_lower = indicator.lower()

    result = None
    sources_tried = []

    # 优先级 1: 爬虫（东方财富 / 金十数据）
    if region_lower == "cn":
        config = CN_INDICATORS.get(indicator_lower)
        if config:
            sources_tried.append("东方财富")
            result = fetch_eastmoney(config, days)

    elif region_lower == "us":
        config = US_INDICATORS.get(indicator_lower)
        if config:
            sources_tried.append("金十数据")
            result = fetch_jin10(config, days)

    # 优先级 2: AKShare 兜底
    if result is None or not result.get("data"):
        sources_tried.append("AKShare")
        result = fetch_akshare(region_lower, indicator_lower, days)

    if result:
        result["sources_tried"] = sources_tried
        return result

    return {
        "indicator": f"{REGIONS.get(region_lower, region)}/{indicator}",
        "source": "未找到",
        "error": f"未找到指标: {region}/{indicator}",
        "data": [],
        "sources_tried": sources_tried,
        "hint": "尝试用 macro_monitor.py 浏览器采集",
    }


# ============================================================
# 报告生成
# ============================================================

def generate_report() -> List[Dict]:
    """生成综合宏观报告"""
    report = []
    # 中国核心指标
    cn_core = ["cpi", "ppi", "pmi", "gdp", "m2", "industrial", "trade"]
    for ind in cn_core:
        r = query_indicator("cn", ind, days=1)
        report.append(r)
        time.sleep(0.3)  # 避免请求过于频繁

    # 美国核心指标
    us_core = ["nonfarm", "cpi", "unemployment", "ism_pmi"]
    for ind in us_core:
        r = query_indicator("us", ind, days=1)
        report.append(r)
        time.sleep(0.3)

    return report


# ============================================================
# 输出格式化
# ============================================================

def _fmt_val(v: Any) -> str:
    """格式化数值"""
    if v is None or v == "—" or v == "":
        return "—"
    try:
        f = float(v)
        if abs(f) < 0.01:
            return str(f)
        return f"{f:.2f}"
    except (ValueError, TypeError):
        return str(v)


def _fmt_impact(impact: Any) -> str:
    """格式化影响标记"""
    try:
        imp = str(impact).lower()
        if imp in ["3", "high", "高"]:
            return "[高]"
        if imp in ["2", "medium", "中"]:
            return "[中]"
        if imp in ["1", "low", "低"]:
            return "[低]"
    except (ValueError, TypeError):
        pass
    return ""


def print_table(result: Dict, show_hint: bool = True):
    """表格输出"""
    indicator = result.get("indicator", "未知指标")
    source = result.get("source", "—")
    sources_tried = result.get("sources_tried", [])
    data = result.get("data", [])
    error = result.get("error")

    print(f"\n{'=' * 70}")
    print(f"  {indicator}")
    print(f"{'=' * 70}")

    if sources_tried:
        src_str = " → ".join(sources_tried)
        print(f"  数据源尝试: {src_str}")

    if error:
        print(f"  [!] {error}")

    if data:
        # 判断是否有预期/前值列（金十数据格式）
        has_expected = data[0].get("expected") is not None

        if has_expected:
            print(f"\n  {'日期':<14} {'今值':<12} {'预期':<12} {'前值':<12} {'影响':<8}")
            print(f"  {'-' * 58}")
            for row in data:
                impact_str = _fmt_impact(row.get("impact", ""))
                print(f"  {row.get('date', '—'):<14} "
                      f"{_fmt_val(row.get('value', '—')):<12} "
                      f"{_fmt_val(row.get('expected', '—')):<12} "
                      f"{_fmt_val(row.get('previous', '—')):<12} "
                      f"{impact_str:<8}")
        else:
            print(f"\n  {'日期':<14} {'数值':<14} {'变动':<12}")
            print(f"  {'-' * 40}")
            for row in data:
                print(f"  {row.get('date', '—'):<14} "
                      f"{_fmt_val(row.get('value', '—')):<14} "
                      f"{_fmt_val(row.get('change', '—')):<12}")

        print(f"  {'-' * 58}")
        print(f"  数据来源: {source}")

    if show_hint and result.get("hint"):
        print(f"\n  [提示] {result['hint']}")

    print()


def print_report(report: List[Dict]):
    """输出完整报告"""
    print(f"\n{'=' * 70}")
    print(f"  [宏观数据报告]")
    print(f"  生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'=' * 70}")

    cn_data = [r for r in report if "中国" in r.get("indicator", "")]
    us_data = [r for r in report if "美国" in r.get("indicator", "")]

    if cn_data:
        print(f"\n{'=' * 70}")
        print(f"  [中国] 宏观数据")
        print(f"{'=' * 70}")
        for r in cn_data:
            print_table(r, show_hint=False)

    if us_data:
        print(f"\n{'=' * 70}")
        print(f"  [美国] 宏观数据")
        print(f"{'=' * 70}")
        for r in us_data:
            print_table(r, show_hint=False)

    print(f"\n{'=' * 70}")
    print(f"  数据来源: 东方财富 / 金十数据 / AKShare(兜底)")
    print(f"  注: 如需经济日历或政策动态，请使用 macro_monitor.py")
    print(f"{'=' * 70}\n")


# ============================================================
# CLI
# ============================================================

def list_indicators():
    """列出所有可用指标"""
    print(f"\n{'=' * 70}")
    print(f"  MacroData 可用宏观数据指标")
    print(f"{'=' * 70}")

    print(f"\n  [中国] 中国宏观（东方财富爬虫）")
    print(f"  {'-' * 50}")
    for key, config in sorted(CN_INDICATORS.items()):
        print(f"    {key:<20} {config['name']:<20} {config['description']}")

    print(f"\n  [美国] 美国宏观（金十数据爬虫）")
    print(f"  {'-' * 50}")
    for key, config in sorted(US_INDICATORS.items()):
        print(f"    {key:<20} {config['name']:<20} {config['description']}")

    print(f"\n  [AKShare] AKShare 兜底指标（额外补充）")
    print(f"  {'-' * 50}")
    for region, indicators in AKSHARE_INDICATORS.items():
        region_name = REGIONS.get(region, region)
        for key, config in sorted(indicators.items()):
            print(f"    {region}/{key:<18} {config['desc']}")
    print()


def main():
    parser = argparse.ArgumentParser(
        description="MacroData - 宏观经济数据查询工具",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  python scripts/macro.py list                           # 列出所有指标
  python scripts/macro.py query cn cpi                   # 中国 CPI
  python scripts/macro.py query us nonfarm               # 美国非农
  python scripts/macro.py query cn gdp --days 5          # 最近5期 GDP
  python scripts/macro.py query cn cpi --json            # JSON 输出
  python scripts/macro.py report                         # 综合宏观报告
        """
    )

    subparsers = parser.add_subparsers(dest="command", help="子命令")

    # list 子命令
    subparsers.add_parser("list", help="列出所有可用指标")

    # query 子命令
    query_parser = subparsers.add_parser("query", help="查询宏观指标")
    query_parser.add_argument("region", help="地区 (cn/us)")
    query_parser.add_argument("indicator", help="指标名称，如 cpi/ppi/pmi/gdp")
    query_parser.add_argument("--days", type=int, default=5, help="返回最近 N 期数据 (默认: 5)")
    query_parser.add_argument("--json", action="store_true", help="JSON 格式输出")
    query_parser.add_argument("--source", choices=["eastmoney", "jin10", "akshare"],
                              help="指定数据源")

    # report 子命令
    report_parser = subparsers.add_parser("report", help="生成综合宏观报告")
    report_parser.add_argument("--json", action="store_true", help="JSON 格式输出")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return

    if args.command == "list":
        list_indicators()

    elif args.command == "query":
        source_map = {"eastmoney": "爬虫", "jin10": "爬虫", "akshare": "AKShare"}
        prefer = source_map.get(args.source) if args.source else None

        result = query_indicator(args.region, args.indicator, args.days, prefer)

        if args.json:
            print(json.dumps(result, ensure_ascii=False, indent=2, default=str))
        else:
            print_table(result)

    elif args.command == "report":
        report = generate_report()
        if args.json:
            print(json.dumps(report, ensure_ascii=False, indent=2, default=str))
        else:
            print_report(report)


if __name__ == "__main__":
    main()
