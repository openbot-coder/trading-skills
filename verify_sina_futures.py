#!/usr/bin/env python3
"""
验证新浪财经接口对中国期货的支持
"""

import requests
import re

SINA_URL = "http://hq.sinajs.cn/list="

test_codes = [
    # 商品期货（连续合约）
    "M0",        # 豆粕连续
    "RB0",       # 螺纹钢连续
    "CU0",       # 铜连续
    "AU0",       # 黄金连续
    "AG0",       # 白银连续
    "RU0",       # 橡胶连续
    "C0",        # 玉米连续
    "A0",        # 大豆连续
    "Y0",        # 豆油连续
    "P0",        # 棕榈油连续
    "TA0",       # PTA连续
    "TA0",       # TA连续
    "SR0",       # 白糖连续
    "CF0",       # 棉花连续
    "FG0",       # 玻璃连续
    "MA0",       # 甲醇连续
    "MA0",       # MA连续
    "I0",        # 铁矿石连续
    "J0",        # 焦炭连续
    "JM0",       # 焦煤连续
    "BU0",       # 沥青连续
    "NR0",       # 20号胶连续
    "NR0",       # NR连续
    "LC0",       # 碳酸锂连续
    "LC0",       # LC连续
    
    # 金融期货
    "NF_IF2508",  # 沪深300 IF
    "NF_IC2508",  # 中证500 IC
    "NF_IH2508",  # 上证50 IH
    "NF_IM2508",  # 中证1000 IM
    "NF_T2506",   # 10年期国债
    "NF_TF2506",  # 5年期国债
    "NF_TS2506",  # 2年期国债
]

print("验证新浪财经接口...")
print("="*80)

# 分组测试
for i in range(0, len(test_codes), 5):
    batch = test_codes[i:i+5]
    url = SINA_URL + ",".join(batch)
    
    try:
        response = requests.get(url, headers={'Referer': 'http://finance.sina.com.cn/'}, timeout=10)
        text = response.content.decode('gbk')
        
        print(f"\n测试: {', '.join(batch)}")
        
        lines = text.strip().split(';')
        for line in lines:
            line = line.strip()
            if not line:
                continue
            match = re.match(r'var hq_str_([^=]+)="([^"]+)"', line)
            if match:
                code = match.group(1)
                data = match.group(2)
                if data:
                    fields = data.split(',')
                    name = fields[0] if len(fields) > 0 else ""
                    if name:
                        print(f"  ✓ {code}: {name}")
                        if len(fields) > 8:
                            print(f"    最新价: {fields[8]}")
    except Exception as e:
        print(f"  异常: {e}")
