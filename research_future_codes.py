#!/usr/bin/env python3
"""
研究腾讯财经接口支持的期货代码格式
"""

import requests
import re

API_URL = "https://qt.gtimg.cn/q="
HEADERS = {"User-Agent": "Mozilla/5.0"}

# 尝试更多可能的格式
test_codes = [
    # 国内期货常见前缀
    "SHFE_RU",
    "DCE_M",
    "CZCE_CU",
    "CFFEX_IF",
    "GZFE_LI",
    
    # 数字前缀
    "001_RU",
    "101_RU",
    
    # 其他可能
    "future_RU",
    "f_RU",
    "CN_RU",
    
    # 具体合约（带月份）
    "hf_RU2409",
    "hf_CU2408",
    "hf_AU2410",
    "hf_AG2408",
    "hf_IF2408",
    "hf_M2409",
    
    # 国际期货验证
    "hf_GC",
    "hf_CL",
    "hf_SI",
]

print("测试更多期货代码格式...")
print("="*80)

# 分组测试
for i in range(0, len(test_codes), 5):
    batch = test_codes[i:i+5]
    url = API_URL + ",".join(batch)
    
    try:
        response = requests.get(url, headers=HEADERS, timeout=10)
        text = response.content.decode('gbk')
        
        print(f"\n测试: {', '.join(batch)}")
        print(f"响应: {text[:200]}")
        
        # 解析
        lines = text.strip().split(';')
        for line in lines:
            if line and "v_pv_none_match" not in line:
                match = re.match(r'v_([^=]+)="([^"]+)"', line)
                if match:
                    code = match.group(1)
                    data = match.group(2)
                    fields = data.split('~')
                    name = fields[1] if len(fields) > 1 else ""
                    price = fields[3] if len(fields) > 3 else ""
                    if name and name != code:
                        print(f"  ✓ 找到: {code} - {name} - {price}")
                        
    except Exception as e:
        print(f"  异常: {e}")

print("\n" + "="*80)
print("查看富途API的期货代码格式...")
print("="*80)

# 读取富途的文档看看
import os
futu_doc = "d:/src/trading-skills/quantdata/futuopendata/futuapi/docs/FUTURES_TRADING.md"
if os.path.exists(futu_doc):
    with open(futu_doc, 'r', encoding='utf-8') as f:
        content = f.read(5000)
        print(content)
