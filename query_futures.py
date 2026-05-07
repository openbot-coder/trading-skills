#!/usr/bin/env python3
"""
综合期货查询脚本
支持通过腾讯财经、新浪财经和Yahoo Finance查询国际期货价格
"""

import argparse
import sys
import requests
import re

# 尝试导入 yfinance
try:
    import yfinance as yf
    import pandas as pd
    YFINANCE_AVAILABLE = True
except ImportError:
    YFINANCE_AVAILABLE = False

# 腾讯财经接口
TENCENT_API = "https://qt.gtimg.cn/q="

# 新浪财经接口
SINA_API = "http://hq.sinajs.cn/list="

# 请求头，伪装成浏览器
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
    'Accept-Encoding': 'gzip, deflate, br',
    'Connection': 'keep-alive',
    'Referer': 'https://finance.sina.com.cn/',
}

# 期货代码映射
FUTURES_MAP = {
    'hf_GC': {'name': '纽约黄金', 'code': 'hf_GC', 'exchange': 'COMEX', 'yf_code': 'GC=F'},
    'hf_SI': {'name': '纽约白银', 'code': 'hf_SI', 'exchange': 'COMEX', 'yf_code': 'SI=F'},
    'hf_HG': {'name': '纽约铜', 'code': 'hf_HG', 'exchange': 'COMEX', 'yf_code': 'HG=F'},
    'hf_XAU': {'name': '伦敦金（现货黄金）', 'code': 'hf_XAU', 'exchange': 'LBMA', 'yf_code': 'GC=F'},
    'hf_XAG': {'name': '伦敦银（现货白银）', 'code': 'hf_XAG', 'exchange': 'LBMA', 'yf_code': 'SI=F'},
    'hf_CL': {'name': '纽约原油', 'code': 'hf_CL', 'exchange': 'NYMEX', 'yf_code': 'CL=F'},
    'hf_OIL': {'name': '布伦特原油', 'code': 'hf_OIL', 'exchange': 'ICE', 'yf_code': 'BZ=F'},
    'hf_NG': {'name': '美国天然气', 'code': 'hf_NG', 'exchange': 'NYMEX', 'yf_code': 'NG=F'},
}


def parse_tencent_response(text):
    """解析腾讯财经接口返回的数据"""
    results = []
    
    lines = text.strip().split('\n')
    for line in lines:
        if not line or 'v_pv_none_match' in line:
            continue
            
        match = re.match(r'v_([^=]+)="([^"]+)"', line)
        if match:
            code = match.group(1)
            data_str = match.group(2)
            data = data_str.split(',')
            
            if len(data) >= 14:
                result = {
                    'code': code,
                    'name': data[13] if len(data) > 13 else code,
                    'last_price': float(data[0]) if data[0] else 0,
                    'change_pct': float(data[1]) if data[1] else 0,
                    'open': float(data[2]) if data[2] else 0,
                    'prev_close': float(data[3]) if data[3] else 0,
                    'high': float(data[4]) if data[4] else 0,
                    'low': float(data[5]) if data[5] else 0,
                    'time': data[6] if len(data) > 6 else '',
                    'buy': float(data[7]) if data[7] else 0,
                    'sell': float(data[8]) if data[8] else 0,
                    'date': data[12] if len(data) > 12 else '',
                    'source': '腾讯财经',
                }
                
                if result['prev_close'] and result['last_price']:
                    result['change'] = result['last_price'] - result['prev_close']
                    if not result['change_pct'] and result['prev_close'] != 0:
                        result['change_pct'] = (result['change'] / result['prev_close'] * 100)
                else:
                    result['change'] = 0
                
                results.append(result)
    
    return results


def query_tencent_futures(codes):
    """通过腾讯财经接口查询期货（优先使用）"""
    if not codes:
        return []
    
    code_str = ','.join(codes)
    url = f"{TENCENT_API}{code_str}"
    
    try:
        response = requests.get(url, headers=HEADERS, timeout=10)
        
        for encoding in ['gbk', 'utf-8', 'gb2312']:
            try:
                text = response.content.decode(encoding)
                break
            except:
                continue
        else:
            text = response.text
        
        if response.status_code == 200:
            return parse_tencent_response(text)
        else:
            return []
            
    except Exception as e:
        print(f"腾讯财经接口请求异常: {e}")
        return []


def parse_sina_response(text):
    """解析新浪财经接口返回的数据"""
    results = []
    
    lines = text.strip().split('\n')
    for line in lines:
        if not line:
            continue
            
        # 格式: var hq_str_hf_GC="名称,开盘价,最高价,最低价,昨收价,最新价,时间";
        match = re.search(r'var hq_str_([^=]+)="([^"]+)";', line)
        if match:
            code = match.group(1)
            data_str = match.group(2)
            data = data_str.split(',')
            
            if len(data) >= 7:
                result = {
                    'code': code,
                    'name': data[0],
                    'last_price': float(data[5]) if data[5] else 0,
                    'open': float(data[1]) if data[1] else 0,
                    'high': float(data[2]) if data[2] else 0,
                    'low': float(data[3]) if data[3] else 0,
                    'prev_close': float(data[4]) if data[4] else 0,
                    'time': data[6] if len(data) > 6 else '',
                    'date': '',
                    'source': '新浪财经',
                }
                
                if result['prev_close'] and result['last_price']:
                    result['change'] = result['last_price'] - result['prev_close']
                    result['change_pct'] = (result['change'] / result['prev_close'] * 100) if result['prev_close'] != 0 else 0
                else:
                    result['change'] = 0
                    result['change_pct'] = 0
                
                results.append(result)
    
    return results


def query_sina_futures(codes):
    """通过新浪财经接口查询期货（备用）"""
    if not codes:
        return []
    
    code_str = ','.join(codes)
    url = f"{SINA_API}{code_str}"
    
    try:
        response = requests.get(url, headers=HEADERS, timeout=10)
        response.encoding = 'gbk'
        
        if response.status_code == 200:
            return parse_sina_response(response.text)
        else:
            return []
            
    except Exception as e:
        print(f"新浪财经接口请求异常: {e}")
        return []


def query_yahoo_finance(yf_code, name):
    """通过 Yahoo Finance 查询期货（备用）"""
    if not YFINANCE_AVAILABLE:
        return None, "yfinance 未安装"
    
    try:
        ticker = yf.Ticker(yf_code)
        hist = ticker.history(period="5d")
        
        if hist.empty:
            return None, "无数据"
        
        latest = hist.iloc[-1]
        prev_close = hist.iloc[-2]['Close'] if len(hist) > 1 else latest['Open']
        change = latest['Close'] - prev_close
        change_pct = (change / prev_close * 100) if prev_close != 0 else 0
        
        return {
            'name': name,
            'code': yf_code,
            'last_price': latest['Close'],
            'open': latest['Open'],
            'high': latest['High'],
            'low': latest['Low'],
            'volume': latest['Volume'],
            'prev_close': prev_close,
            'change': change,
            'change_pct': change_pct,
            'date': latest.name.strftime('%Y-%m-%d'),
            'time': '',
            'source': 'Yahoo Finance',
        }, None
    except Exception as e:
        return None, str(e)


def main():
    parser = argparse.ArgumentParser(description='期货价格查询工具')
    parser.add_argument('codes', nargs='*', 
                       help='期货代码，如 hf_GC hf_CL，留空则查询所有')
    parser.add_argument('--list', action='store_true',
                       help='列出所有支持的期货代码')
    parser.add_argument('--source', type=str, choices=['tencent', 'sina', 'yahoo'],
                       help='指定数据源 (tencent/sina/yahoo)')
    
    args = parser.parse_args()
    
    if args.list:
        print("="*80)
        print("支持的期货代码列表")
        print("="*80)
        print(f"{'代码':<10} {'名称':<20} {'交易所':<10} {'数据源':<15}")
        print("-"*80)
        for code, info in FUTURES_MAP.items():
            print(f"{code:<10} {info['name']:<20} {info['exchange']:<10} {'腾讯财经/新浪':<15}")
        print("="*80)
        return
    
    codes_to_query = args.codes if args.codes else list(FUTURES_MAP.keys())
    
    invalid_codes = [c for c in codes_to_query if c not in FUTURES_MAP]
    if invalid_codes:
        print(f"错误: 不支持的代码: {', '.join(invalid_codes)}")
        print("使用 --list 查看所有支持的代码")
        sys.exit(1)
    
    print("="*80)
    print("期货行情查询")
    print("="*80)
    print()
    
    results = []
    
    # 根据用户选择或自动选择数据源
    if args.source == 'tencent':
        print("使用腾讯财经数据源...")
        results = query_tencent_futures(codes_to_query)
    elif args.source == 'sina':
        print("使用新浪财经数据源...")
        results = query_sina_futures(codes_to_query)
    elif args.source == 'yahoo':
        print("使用 Yahoo Finance 数据源...")
        for code in codes_to_query:
            info = FUTURES_MAP[code]
            data, error = query_yahoo_finance(info['yf_code'], info['name'])
            if data:
                results.append(data)
            else:
                print(f"{info['name']}: {error}")
    else:
        # 自动选择: 腾讯 -> 新浪 -> Yahoo
        print("尝试腾讯财经数据源...")
        results = query_tencent_futures(codes_to_query)
        
        if not results:
            print("腾讯财经失败，尝试新浪财经...")
            results = query_sina_futures(codes_to_query)
        
        if not results:
            print("新浪财经失败，尝试 Yahoo Finance...")
            for code in codes_to_query:
                info = FUTURES_MAP[code]
                data, error = query_yahoo_finance(info['yf_code'], info['name'])
                if data:
                    results.append(data)
    
    if results:
        print()
        print("="*110)
        print(f"{'名称':<20} {'最新价':<12} {'涨跌':<10} {'涨跌幅':<10} {'开盘':<10} {'最高':<10} {'最低':<10} {'来源':<15}")
        print("-"*110)
        
        for r in results:
            change_str = f"{r['change']:+.2f}"
            change_pct_str = f"{r['change_pct']:+.2f}%"
            print(f"{r['name']:<20} {r['last_price']:<12.2f} {change_str:<10} {change_pct_str:<10} {r['open']:<10.2f} {r['high']:<10.2f} {r['low']:<10.2f} {r['source']:<15}")
        
        print("-"*110)
        update_time = f"{results[0]['date']} {results[0]['time']}".strip()
        print(f"数据来源: {results[0]['source']} (更新时间: {update_time or '未知'})")
        print("="*110)
    else:
        print("\n无法获取数据，请检查网络连接或稍后重试")


if __name__ == "__main__":
    main()
