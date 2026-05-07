#!/usr/bin/env python3
"""
测试新浪财经接口对期货的支持
"""

import requests
import re

# 新浪财经接口
SINA_URL = "http://hq.sinajs.cn/list="

test_codes = [
    # 中国期货
    "RU2409",      # 橡胶
    "CU2408",      # 铜
    "AU2410",      # 黄金
    "AG2408",      # 白银
    "IF2408",      # 沪深300
    "M2409",       # 豆粕
    "C2409",       # 玉米
    
    # 带前缀
    "SHFE_RU2409",
    "DCE_M2409",
    "CZCE_SR2409",
    "CFFEX_IF2408",
    
    # 新浪常用格式
    "nf_RU2409",
    "hf_RU2409",
    "nf_SHFE_RU",
    
    # 国际期货对比
    "hf_GC",
    "hf_CL",
]

print("测试新浪财经接口...")
print("="*80)

for i in range(0, len(test_codes), 3):
    batch = test_codes[i:i+3]
    url = SINA_URL + ",".join(batch)
    
    try:
        response = requests.get(url, timeout=10)
        text = response.content.decode('gbk')
        
        print(f"\n测试: {', '.join(batch)}")
        if "var hq_str_" in text:
            lines = text.strip().split(';')
            for line in lines:
                line = line.strip()
                if "var hq_str_" in line:
                    match = re.match(r'var hq_str_([^=]+)="([^"]+)"', line)
                    if match:
                        code = match.group(1)
                        data = match.group(2)
                        if data:
                            fields = data.split(',')
                            name = fields[0] if len(fields) > 0 else ""
                            if name:
                                print(f"  ✓ 找到: {code}")
                                print(f"    数据: {data[:100]}")
                        
    except Exception as e:
        print(f"  异常: {e}")
