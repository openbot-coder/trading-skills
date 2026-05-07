#!/usr/bin/env python3
"""调试腾讯财经接口"""

import requests
import re

TENCENT_API_URL = "https://qt.gtimg.cn/q="
TENCENT_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "Referer": "https://finance.qq.com/",
}

codes = ["hf_GC", "hf_CL"]

code_str = ",".join(codes)
url = f"{TENCENT_API_URL}{code_str}"

print(f"请求URL: {url}")
print(f"请求头: {TENCENT_HEADERS}")

response = requests.get(url, headers=TENCENT_HEADERS, timeout=10)

print(f"\n状态码: {response.status_code}")
print(f"\n原始内容长度: {len(response.content)}")

for encoding in ['gbk', 'utf-8', 'gb2312', 'gb18030']:
    try:
        text = response.content.decode(encoding)
        print(f"\n编码: {encoding}")
        print(f"内容: {text[:500]}")
    except Exception as e:
        print(f"\n编码 {encoding} 失败: {e}")
