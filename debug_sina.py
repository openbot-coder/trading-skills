#!/usr/bin/env python3
"""
调试新浪财经接口
"""

import requests
import re

SINA_API = "http://hq.sinajs.cn/list="

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
}

codes = ['hf_GC', 'hf_CL']

url = f"{SINA_API}{','.join(codes)}"
print(f"请求: {url}")
print()

response = requests.get(url, headers=HEADERS, timeout=10)
response.encoding = 'gbk'
print(f"状态码: {response.status_code}")
print(f"原始响应:")
print(repr(response.text))
print()

lines = response.text.strip().split('\n')
for line in lines:
    if not line:
        continue
    
    print(f"处理行: {repr(line)}")
    
    match = re.search(r'var hq_str_([^=]+)="([^"]+)";', line)
    if match:
        code = match.group(1)
        data_str = match.group(2)
        data = data_str.split(',')
        
        print(f"  代码: {code}")
        print(f"  原始数据: {data_str}")
        print(f"  分割后: {data}")
        print(f"  数据个数: {len(data)}")
        print()
        for i, val in enumerate(data):
            print(f"  [{i}]: {repr(val)}")
