#!/usr/bin/env python3
"""
财经行情查询工具 - 整合腾讯财经(股票/指数/国际期货) + 新浪财经(中国期货)
支持K线数据下载（日K/周K/月K/分钟K线）
"""

import argparse
import requests
import re
import json
from typing import List, Dict, Optional, Union
import sys
import os

# 添加项目根目录到路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
from cache import get_cache, determine_ttl

# 获取全局缓存实例
cache = get_cache()

# 全局缓存开关
CACHE_ENABLED = True


def is_cache_enabled() -> bool:
    """检查缓存是否启用"""
    return CACHE_ENABLED

# 腾讯财经接口（股票、指数、国际期货）
TENCENT_API_URL = "https://qt.gtimg.cn/q="
TENCENT_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
    "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
    "Referer": "https://finance.qq.com/",
}

# 腾讯K线接口
TENCENT_KLINE_DAILY_URL = "https://data.gtimg.cn/flashdata/hushen/latest/daily/"
TENCENT_KLINE_WEEKLY_URL = "https://data.gtimg.cn/flashdata/hushen/latest/weekly/"
TENCENT_KLINE_MONTHLY_URL = "https://data.gtimg.cn/flashdata/hushen/monthly/"
TENCENT_KLINE_YEARLY_URL = "https://data.gtimg.cn/flashdata/hushen/daily/"

# 新浪财经接口（中国期货）
SINA_API_URL = "http://hq.sinajs.cn/list="
SINA_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Referer": "http://finance.sina.com.cn/",
}

# 新浪K线接口
SINA_KLINE_URL = "http://money.finance.sina.com.cn/quotes_service/api/json_v2.php/CN_MarketData.getKLineData"


def to_float(value: str) -> Optional[float]:
    """安全转换为浮点数"""
    if not value:
        return None
    try:
        return float(value)
    except (ValueError, TypeError):
        return None


def to_int(value: str) -> Optional[int]:
    """安全转换为整数"""
    if not value:
        return None
    try:
        return int(float(value))
    except (ValueError, TypeError):
        return None


def is_sina_code(code: str) -> bool:
    """判断是否为新浪财经代码（中国期货）"""
    # 新浪财经中国期货代码特征：
    # - 商品期货连续合约：品种代码+0（如 M0, RB0, AU0）
    # - 金融期货：NF_前缀（如 NF_IF2508）
    if code.startswith("NF_"):
        return True
    # 商品期货连续合约：通常是2-3个字母+0
    if len(code) <= 4 and code.endswith("0") and not code.startswith(("sh", "sz", "hf_")):
        return True
    return False


def parse_tencent_quote(raw_line: str) -> Optional[Dict]:
    """
    解析腾讯财经单条行情数据
    
    Args:
        raw_line: 原始数据行，格式如 v_sh600000="1~...";
        
    Returns:
        解析后的字典
    """
    match = re.match(r'v_([^=]+)="([^"]+)"', raw_line)
    if not match:
        return None
    
    code_full = match.group(1)
    data_str = match.group(2)
    
    # 判断是股票/指数（~分隔）还是期货（,分隔）
    if '~' in data_str:
        fields = data_str.split('~')
        if len(fields) < 52:
            return None
        
        result = {}
        result["source"] = "tencent"
        result["full_code"] = code_full
        result["exchange_id"] = to_int(fields[0])
        result["exchange"] = "SSE" if fields[0] == "1" else "SZSE" if fields[0] == "51" else "OTHER"
        result["name"] = fields[1]
        result["code"] = fields[2]
        
        # 价格信息
        result["last_price"] = to_float(fields[3])
        result["pre_close"] = to_float(fields[4])
        result["open"] = to_float(fields[5])
        result["high"] = to_float(fields[33])
        result["low"] = to_float(fields[34])
        
        # 涨跌
        result["change"] = to_float(fields[31])
        result["change_pct"] = to_float(fields[32])
        
        # 成交量
        result["volume"] = to_int(fields[6])
        result["outer_plate"] = to_int(fields[7])
        result["inner_plate"] = to_int(fields[8])
        
        # 买卖盘
        result["bid"] = []
        for i in range(5):
            price_idx = 9 + i * 2
            vol_idx = 10 + i * 2
            if price_idx < len(fields) and vol_idx < len(fields):
                result["bid"].append({
                    "price": to_float(fields[price_idx]),
                    "volume": to_int(fields[vol_idx])
                })
        
        result["ask"] = []
        for i in range(5):
            price_idx = 19 + i * 2
            vol_idx = 20 + i * 2
            if price_idx < len(fields) and vol_idx < len(fields):
                result["ask"].append({
                    "price": to_float(fields[price_idx]),
                    "volume": to_int(fields[vol_idx])
                })
        
        # 成交金额
        result["turnover"] = to_float(fields[37])
        if result["turnover"] is not None:
            result["turnover"] *= 10000  # 万 -> 元
        
        # 尝试从组合字段获取成交额
        if result["turnover"] is None and fields[35]:
            parts = fields[35].split('/')
            if len(parts) >= 3:
                result["turnover"] = to_float(parts[2])
        
        result["turnover_rate"] = to_float(fields[38])
        result["pe_ratio"] = to_float(fields[39])
        result["pb_ratio"] = to_float(fields[46])
        result["volume_ratio"] = to_float(fields[49])
        result["amplitude"] = to_float(fields[43])
        
        result["market_cap_float"] = to_float(fields[44])
        result["market_cap_total"] = to_float(fields[45])
        
        result["price_limit_high"] = to_float(fields[47])
        result["price_limit_low"] = to_float(fields[48])
        
        result["average_price"] = to_float(fields[51])
        
        # 时间
        if len(fields) > 30 and fields[30]:
            dt = fields[30]
            result["datetime"] = dt
            if len(dt) >= 14:
                result["date"] = dt[:8]
                result["time"] = dt[8:]
                result["time_formatted"] = f"{result['time'][:2]}:{result['time'][2:4]}:{result['time'][4:]}"
        
        # 保存原始字段
        result["raw_fields"] = fields
        
        return result
    else:
        # 期货格式：逗号分隔
        fields = data_str.split(',')
        if len(fields) < 12:
            return None
        
        result = {}
        result["source"] = "tencent"
        result["full_code"] = code_full
        result["name"] = fields[-1] if len(fields) > 0 else ""
        result["code"] = code_full
        result["exchange"] = "GLOBAL"
        
        # 期货价格信息
        result["last_price"] = to_float(fields[0])
        result["change"] = to_float(fields[1])
        result["open"] = to_float(fields[3])
        result["high"] = to_float(fields[4])
        result["low"] = to_float(fields[5])
        result["time"] = fields[6] if len(fields) > 6 else ""
        result["time_formatted"] = result["time"]
        result["date"] = fields[-2] if len(fields) >= 2 else ""
        
        # 腾讯财经期货的涨跌幅直接用change和last_price计算
        if result["change"] is not None and result["last_price"] is not None:
            prev_price = result["last_price"] - result["change"]
            if prev_price and prev_price != 0:
                result["change_pct"] = (result["change"] / prev_price) * 100
            else:
                result["change_pct"] = None
        
        # 买卖盘
        if len(fields) > 7:
            result["bid"] = [{"price": to_float(fields[7]), "volume": None}]
        if len(fields) > 8:
            result["ask"] = [{"price": to_float(fields[8]), "volume": None}]
        
        # 保存原始字段
        result["raw_fields"] = fields
        
        return result


def parse_sina_quote(raw_line: str, original_code: str) -> Optional[Dict]:
    """
    解析新浪财经单条行情数据
    
    Args:
        raw_line: 原始数据行，格式如 var hq_str_M0="豆粕连续,145958,3170,...";
        original_code: 原始请求代码
        
    Returns:
        解析后的字典
    """
    match = re.match(r'var hq_str_([^=]+)="([^"]+)"', raw_line)
    if not match:
        return None
    
    code_full = match.group(1)
    data_str = match.group(2)
    fields = data_str.split(',')
    
    if len(fields) < 10:
        return None
    
    result = {}
    result["source"] = "sina"
    result["full_code"] = original_code  # 使用原始请求代码
    result["name"] = fields[0]
    result["code"] = code_full
    
    # 判断是商品期货还是金融期货
    if len(fields) >= 18:
        # 商品期货格式
        result["exchange"] = fields[15] if len(fields) > 15 else "UNKNOWN"
        result["last_price"] = to_float(fields[8])
        result["open"] = to_float(fields[2])
        result["high"] = to_float(fields[3])
        result["low"] = to_float(fields[4])
        result["pre_close"] = to_float(fields[5])
        result["bid"] = [{
            "price": to_float(fields[6]),
            "volume": to_int(fields[11])
        }] if len(fields) > 11 else []
        result["ask"] = [{
            "price": to_float(fields[7]),
            "volume": to_int(fields[12])
        }] if len(fields) > 12 else []
        result["settlement"] = to_float(fields[9])
        result["pre_settlement"] = to_float(fields[10])
        result["open_interest"] = to_int(fields[13])
        result["volume"] = to_int(fields[14])
        result["date"] = fields[17] if len(fields) > 17 else ""
    else:
        # 金融期货格式
        result["exchange"] = "CFFEX"
        result["last_price"] = to_float(fields[3])
        result["open"] = to_float(fields[1])
        result["high"] = to_float(fields[2])
        result["low"] = to_float(fields[4])
        result["pre_close"] = to_float(fields[5])
        result["volume"] = to_int(fields[6])
        
        if len(fields) > 36:
            result["date"] = fields[36] if len(fields) > 36 else ""
            result["time"] = fields[37] if len(fields) > 37 else ""
            result["time_formatted"] = result["time"] if result.get("time") else ""
    
    # 计算涨跌
    if result["last_price"] is not None and result["pre_close"] is not None:
        result["change"] = result["last_price"] - result["pre_close"]
        if result["pre_close"] > 0:
            result["change_pct"] = (result["change"] / result["pre_close"]) * 100
        else:
            result["change_pct"] = None
    else:
        result["change"] = None
        result["change_pct"] = None
    
    # 保存原始字段
    result["raw_fields"] = fields
    
    return result


def fetch_tencent_quotes(codes: List[str]) -> List[Dict]:
    """从腾讯财经获取行情数据（带缓存）"""
    if not codes:
        return []
    
    # 生成缓存键
    cache_key = ",".join(sorted(codes))
    namespace = "tencent_quotes"
    
    # 确定缓存时间：检查是否有A股代码
    has_a_share = any(code.startswith(('sh', 'sz')) for code in codes)
    market_type = "A_share" if has_a_share else "other"
    ttl = determine_ttl(market_type, "realtime")
    
    # 尝试从缓存获取
    if is_cache_enabled():
        cached_data = cache.get(namespace, cache_key)
        if cached_data is not None:
            return cached_data
    
    # 没有缓存或缓存禁用，实际获取
    code_str = ",".join(codes)
    url = f"{TENCENT_API_URL}{code_str}"
    
    try:
        response = requests.get(url, headers=TENCENT_HEADERS, timeout=10)
        
        for encoding in ['gbk', 'utf-8', 'gb2312']:
            try:
                text = response.content.decode(encoding)
                break
            except:
                continue
        else:
            text = response.text
        
        results = []
        lines = text.strip().split(';')
        for line in lines:
            line = line.strip()
            if line:
                quote = parse_tencent_quote(line)
                if quote:
                    results.append(quote)
        
        # 保存到缓存
        if is_cache_enabled():
            cache.set(namespace, cache_key, results, ttl)
        
        return results
        
    except Exception as e:
        print(f"腾讯财经请求失败: {e}")
        return []


def fetch_sina_quotes(codes: List[str]) -> List[Dict]:
    """从新浪财经获取行情数据（带缓存）"""
    if not codes:
        return []
    
    # 生成缓存键
    cache_key = ",".join(sorted(codes))
    namespace = "sina_quotes"
    
    # 新浪主要是中国期货，按other市场处理
    ttl = determine_ttl("other", "realtime")
    
    # 尝试从缓存获取
    if is_cache_enabled():
        cached_data = cache.get(namespace, cache_key)
        if cached_data is not None:
            return cached_data
    
    # 没有缓存或缓存禁用，实际获取
    code_str = ",".join(codes)
    url = f"{SINA_API_URL}{code_str}"
    
    try:
        response = requests.get(url, headers=SINA_HEADERS, timeout=10)
        
        text = response.content.decode('gbk')
        
        results = []
        lines = text.strip().split(';')
        for line in lines:
            line = line.strip()
            if line:
                # 尝试匹配代码
                match = re.match(r'var hq_str_([^=]+)="', line)
                if match:
                    matched_code = match.group(1)
                    # 找到对应的原始代码
                    original_code = None
                    for c in codes:
                        if c == matched_code or c.endswith(matched_code):
                            original_code = c
                            break
                    if original_code:
                        quote = parse_sina_quote(line, original_code)
                        if quote:
                            results.append(quote)
        
        # 保存到缓存
        if is_cache_enabled():
            cache.set(namespace, cache_key, results, ttl)
        
        return results
        
    except Exception as e:
        print(f"新浪财经请求失败: {e}")
        return []


def fetch_quotes(codes: List[str]) -> List[Dict]:
    """
    获取多个品种的行情数据，自动选择数据源
    
    Args:
        codes: 代码列表，如 ['sh600000', 'sz000001', 'hf_GC', 'M0', 'NF_IF2508']
        
    Returns:
        解析后的行情列表
    """
    # 分组
    tencent_codes = []
    sina_codes = []
    
    for code in codes:
        if is_sina_code(code):
            sina_codes.append(code)
        else:
            tencent_codes.append(code)
    
    results = []
    
    # 获取腾讯财经数据
    if tencent_codes:
        results.extend(fetch_tencent_quotes(tencent_codes))
    
    # 获取新浪财经数据
    if sina_codes:
        results.extend(fetch_sina_quotes(sina_codes))
    
    # 保持原始顺序
    code_order = {code: i for i, code in enumerate(codes)}
    results.sort(key=lambda x: code_order.get(x["full_code"], 999))
    
    return results


def print_simple(quotes: List[Dict]):
    """简单格式输出"""
    print("\n" + "="*130)
    print(f"{'代码':<12} {'名称':<12} {'最新价':<12} {'涨跌':<10} {'涨跌幅':<10} {'开盘':<10} {'最高':<10} {'最低':<10} {'成交量':<12} {'时间':<15} {'源':<8}")
    print("-"*130)
    
    for q in quotes:
        change_str = f"{q['change']:+.2f}" if q.get('change') is not None else "-"
        change_pct_str = f"{q['change_pct']:+.2f}%" if q.get('change_pct') is not None else "-"
        time_str = q.get('time_formatted', q.get('time', ''))
        source = "腾讯" if q.get('source') == 'tencent' else "新浪"
        
        last_price = f"{q['last_price']:.2f}" if q.get('last_price') is not None else "-"
        open_price = f"{q['open']:.2f}" if q.get('open') is not None else "-"
        high_price = f"{q['high']:.2f}" if q.get('high') is not None else "-"
        low_price = f"{q['low']:.2f}" if q.get('low') is not None else "-"
        volume = str(q['volume']) if q.get('volume') is not None else "-"
        
        print(f"{q['full_code']:<12} {q['name']:<12} {last_price:<12} {change_str:<10} {change_pct_str:<10} {open_price:<10} {high_price:<10} {low_price:<10} {volume:<12} {time_str:<15} {source:<8}")
    
    print("="*130)


def print_detail(quotes: List[Dict]):
    """详细格式输出"""
    for q in quotes:
        print("\n" + "="*80)
        source = "腾讯财经" if q.get('source') == 'tencent' else "新浪财经"
        print(f"{q.get('name', '')} ({q.get('full_code', '')}) - {source}")
        print("="*80)
        
        print(f"\n【基本行情】")
        if q.get('last_price') is not None:
            print(f"  最新价: {q['last_price']:.2f}")
        else:
            print("  最新价: -")
        if q.get('pre_close') is not None:
            print(f"  昨收: {q['pre_close']:.2f}")
        else:
            print("  昨收: -")
        if q.get('open') is not None:
            print(f"  开盘: {q['open']:.2f}")
        else:
            print("  开盘: -")
        if q.get('high') is not None:
            print(f"  最高: {q['high']:.2f}")
        else:
            print("  最高: -")
        if q.get('low') is not None:
            print(f"  最低: {q['low']:.2f}")
        else:
            print("  最低: -")
        
        change_str = f"{q['change']:+.2f}" if q.get('change') is not None else "-"
        change_pct_str = f"{q['change_pct']:+.2f}%" if q.get('change_pct') is not None else "-"
        print(f"  涨跌: {change_str} ({change_pct_str})")
        
        print(f"\n【成交统计】")
        print(f"  成交量: {q.get('volume', '-')} 手")
        if q.get('outer_plate') is not None:
            print(f"  外盘: {q['outer_plate']} 手")
            print(f"  内盘: {q['inner_plate']} 手")
        if q.get('open_interest') is not None:
            print(f"  持仓量: {q['open_interest']} 手")
        if q.get('turnover') is not None:
            print(f"  成交额: {q['turnover']/100000000:.2f} 亿")
        if q.get('turnover_rate') is not None:
            print(f"  换手率: {q['turnover_rate']:.2f}%")
        if q.get('settlement') is not None:
            print(f"  结算价: {q['settlement']:.2f}")
        if q.get('pre_settlement') is not None:
            print(f"  昨结算: {q['pre_settlement']:.2f}")
        
        if q.get('bid') or q.get('ask'):
            print(f"\n【买卖盘】")
            if q.get('bid'):
                print("  买盘:")
                for i, b in enumerate(q['bid'], 1):
                    if b.get('price'):
                        print(f"    买{i}: {b['price']:<8.2f} x {b.get('volume') or '-'}")
            
            if q.get('ask'):
                print("  卖盘:")
                for i, a in enumerate(q['ask'], 1):
                    if a.get('price'):
                        print(f"    卖{i}: {a['price']:<8.2f} x {a.get('volume') or '-'}")
        
        if q.get('date'):
            print(f"\n【时间】")
            time_str = q.get('time_formatted', q.get('time', ''))
            print(f"  {q['date']} {time_str}")


# ========== K线数据功能 ==========

def parse_tencent_kline(raw_text: str, code: str, period: str) -> List[Dict]:
    """
    解析腾讯K线数据
    
    Args:
        raw_text: 原始数据文本
        code: 股票代码
        period: K线周期
        
    Returns:
        K线数据列表
    """
    match = re.match(r'[^=]+\s*=\s*"([^"]+)"', raw_text)
    if not match:
        return []
    
    data_str = match.group(1)
    if not data_str:
        return []
    
    klines = []
    lines = data_str.split('\\n\\\n')
    
    for line in lines:
        line = line.strip()
        if not line or line.startswith('num:') or line.startswith('total:') or line.startswith('start:'):
            continue
        
        fields = line.split()
        if len(fields) < 6:
            continue
        
        try:
            # 格式: 220527 14.29 14.18 14.35 14.11 723067
            # 日期 开盘 收盘 最高 最低 成交量
            date_short = fields[0]
            # 补全年份，假设20xx年
            if len(date_short) == 6:
                year = '20' + date_short[:2]
                date = year + date_short[2:]
            else:
                date = date_short
            
            kline = {
                "source": "tencent",
                "code": code,
                "period": period,
                "date": date,
                "open": to_float(fields[1]),
                "close": to_float(fields[2]),
                "high": to_float(fields[3]),
                "low": to_float(fields[4]),
                "volume": to_int(fields[5]),
            }
            
            if len(fields) > 6:
                kline["turnover"] = to_float(fields[6])
            
            klines.append(kline)
        except:
            continue
    
    return klines


def fetch_tencent_kline(code: str, period: str = "daily", year: Optional[int] = None) -> List[Dict]:
    """
    从腾讯财经获取K线数据（带缓存）
    
    Args:
        code: 股票代码，如 sz000001, sh600000
        period: K线周期，支持 daily(日K), weekly(周K), monthly(月K)
        year: 指定年份，仅对period=daily有效
        
    Returns:
        K线数据列表
    """
    # 生成缓存键
    cache_key = f"{code}_{period}_{year if year else 'latest'}"
    namespace = "tencent_kline"
    
    # K线数据按正常数据缓存1小时
    ttl = determine_ttl("any", "kline")
    
    # 尝试从缓存获取
    if is_cache_enabled():
        cached_data = cache.get(namespace, cache_key)
        if cached_data is not None:
            return cached_data
    
    try:
        if period == "daily" and year is not None:
            # 指定年份的日K线
            year_str = str(year)[-2:]
            url = f"{TENCENT_KLINE_YEARLY_URL}{year_str}/{code}.js"
        elif period == "daily":
            url = f"{TENCENT_KLINE_DAILY_URL}{code}.js"
        elif period == "weekly":
            url = f"{TENCENT_KLINE_WEEKLY_URL}{code}.js"
        elif period == "monthly":
            url = f"{TENCENT_KLINE_MONTHLY_URL}{code}.js"
        else:
            print(f"不支持的K线周期: {period}")
            return []
        
        response = requests.get(url, headers=TENCENT_HEADERS, timeout=10)
        
        for encoding in ['gbk', 'utf-8', 'gb2312']:
            try:
                text = response.content.decode(encoding)
                break
            except:
                continue
        else:
            text = response.text
        
        result = parse_tencent_kline(text, code, period)
        
        # 保存到缓存
        if is_cache_enabled():
            cache.set(namespace, cache_key, result, ttl)
        
        return result
        
    except Exception as e:
        print(f"腾讯K线请求失败: {e}")
        return []


def parse_sina_kline(data: List[Dict], code: str, scale: int) -> List[Dict]:
    """
    解析新浪K线数据
    
    Args:
        data: 新浪API返回的JSON数据
        code: 股票代码
        scale: K线周期（分钟数）
        
    Returns:
        K线数据列表
    """
    klines = []
    for item in data:
        try:
            kline = {
                "source": "sina",
                "code": code,
                "period": f"{scale}min",
                "datetime": item.get("day", ""),
                "open": to_float(item.get("open")),
                "high": to_float(item.get("high")),
                "low": to_float(item.get("low")),
                "close": to_float(item.get("close")),
                "volume": to_int(item.get("volume")),
            }
            
            date_str = kline["datetime"]
            if len(date_str) >= 8:
                kline["date"] = date_str[:8]
            if len(date_str) >= 14:
                kline["time"] = date_str[8:]
            
            klines.append(kline)
        except:
            continue
    
    return klines


def fetch_sina_kline(code: str, scale: int = 5, ma: int = 5, datalen: int = 1023) -> List[Dict]:
    """
    从新浪财经获取K线数据（带缓存）
    
    Args:
        code: 股票代码，如 sz000001, sh600000
        scale: K线周期（分钟数），支持 5, 15, 30, 60
        ma: 均线周期
        datalen: 数据长度
        
    Returns:
        K线数据列表
    """
    # 生成缓存键
    cache_key = f"{code}_{scale}min_ma{ma}_len{datalen}"
    namespace = "sina_kline"
    
    # K线数据按正常数据缓存1小时
    ttl = determine_ttl("any", "kline")
    
    # 尝试从缓存获取
    if is_cache_enabled():
        cached_data = cache.get(namespace, cache_key)
        if cached_data is not None:
            return cached_data
    
    try:
        params = {
            "symbol": code,
            "scale": scale,
            "ma": ma,
            "datalen": datalen
        }
        
        response = requests.get(SINA_KLINE_URL, params=params, headers=SINA_HEADERS, timeout=10)
        
        data = response.json()
        if not isinstance(data, list):
            return []
        
        result = parse_sina_kline(data, code, scale)
        
        # 保存到缓存
        if is_cache_enabled():
            cache.set(namespace, cache_key, result, ttl)
        
        return result
        
    except Exception as e:
        print(f"新浪K线请求失败: {e}")
        return []


def print_kline(klines: List[Dict]):
    """打印K线数据"""
    if not klines:
        print("未获取到K线数据")
        return
    
    code = klines[0].get("code", "")
    period = klines[0].get("period", "")
    source = "腾讯" if klines[0].get("source") == "tencent" else "新浪"
    
    print(f"\n" + "="*100)
    print(f"【K线数据】{code} - {period} - {source}")
    print("="*100)
    print(f"{'日期':<12} {'开盘':<10} {'最高':<10} {'最低':<10} {'收盘':<10} {'成交量':<12} {'成交额':<12}")
    print("-"*100)
    
    for k in klines:
        date = k.get("date", k.get("datetime", ""))
        open_p = f"{k['open']:.2f}" if k.get('open') is not None else "-"
        high_p = f"{k['high']:.2f}" if k.get('high') is not None else "-"
        low_p = f"{k['low']:.2f}" if k.get('low') is not None else "-"
        close_p = f"{k['close']:.2f}" if k.get('close') is not None else "-"
        volume = str(k.get("volume", "-"))
        turnover = f"{k.get('turnover', '-')}" if k.get('turnover') is not None else "-"
        
        print(f"{date:<12} {open_p:<10} {high_p:<10} {low_p:<10} {close_p:<10} {volume:<12} {turnover:<12}")
    
    print("="*100)
    print(f"共 {len(klines)} 条K线数据")


def print_json(quotes: List[Dict]):
    """JSON格式输出"""
    output = []
    for q in quotes:
        q_copy = q.copy()
        q_copy.pop('raw_fields', None)
        output.append(q_copy)
    print(json.dumps(output, ensure_ascii=False, indent=2))


def main():
    parser = argparse.ArgumentParser(description="财经行情查询工具 - 腾讯财经(股票/指数/国际期货) + 新浪财经(中国期货)\n支持K线数据下载")
    
    # K线查询模式
    parser.add_argument("--kline", action="store_true", help="K线数据查询模式")
    parser.add_argument("--period", default="daily", help="K线周期: daily/weekly/monthly/5min/15min/30min/60min (默认: daily)")
    parser.add_argument("--year", type=int, help="指定年份（仅对daily周期有效）")
    parser.add_argument("--source", default="tencent", help="K线数据源: tencent/sina (默认: tencent)")
    
    # 普通行情查询
    parser.add_argument("codes", nargs="+", help="代码列表\n"
                        "股票/指数: sh600000 sz000001\n"
                        "国际期货: hf_GC hf_CL\n"
                        "中国期货: M0 RB0 AU0 NF_IF2508")
    parser.add_argument("--detail", action="store_true", help="显示详细信息")
    parser.add_argument("--json", action="store_true", help="JSON格式输出")
    
    # 缓存控制
    parser.add_argument("--no-cache", action="store_true", help="禁用缓存（不使用缓存，也不保存到缓存）")
    parser.add_argument("--clear-cache", action="store_true", help="清除所有缓存后退出")
    
    args = parser.parse_args()
    
    # 处理清除缓存
    if args.clear_cache:
        print("正在清除缓存...")
        cache.clear()
        print("缓存已清除")
        return
    
    # 如果禁用缓存，设置全局开关
    if args.no_cache:
        global CACHE_ENABLED
        CACHE_ENABLED = False
    
    if args.kline:
        # K线查询模式
        for code in args.codes:
            if args.source == "sina":
                # 新浪K线
                scale_map = {"5min": 5, "15min": 15, "30min": 30, "60min": 60}
                scale = scale_map.get(args.period, 5)
                klines = fetch_sina_kline(code, scale=scale)
            else:
                # 腾讯K线
                period_map = {"daily": "daily", "weekly": "weekly", "monthly": "monthly"}
                period = period_map.get(args.period, "daily")
                klines = fetch_tencent_kline(code, period=period, year=args.year)
            
            if args.json:
                print(json.dumps(klines, ensure_ascii=False, indent=2))
            else:
                print_kline(klines)
    else:
        # 普通行情查询
        quotes = fetch_quotes(args.codes)
        
        if not quotes:
            print("未获取到数据")
            return
        
        if args.json:
            print_json(quotes)
        elif args.detail:
            print_detail(quotes)
        else:
            print_simple(quotes)


if __name__ == "__main__":
    main()
