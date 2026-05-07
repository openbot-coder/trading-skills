#!/usr/bin/env python3
"""
测试腾讯财经接口对中国期货的支持
"""

import requests
import re

# 腾讯财经接口
API_URL = "https://qt.gtimg.cn/q="

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
}

# 测试中国期货代码格式
test_codes = [
    # 尝试各种可能的前缀
    "hf_SHFE",    # 上期所
    "hf_DCE",     # 大商所
    "hf_CZCE",    # 郑商所
    "hf_CFFEX",   # 中金所
    "hf_GZFE",    # 广期所
    
    # 具体品种
    "hf_RU",      # 橡胶
    "hf_CU",      # 铜
    "hf_AL",      # 铝
    "hf_ZN",      # 锌
    "hf_AU",      # 黄金
    "hf_AG",      # 白银
    
    # 中国期货常用格式
    "shfe_RU",
    "czce_CU",
    "dce_M",
    "cffex_IF",
    
    # 不带前缀
    "RU2409",
    "CU2408",
    "M2409",
    "IF2408",
    
    # 其他可能格式
    "CFFEX_IF",
    "SHFE_RU",
]

print("="*80)
print("测试腾讯财经接口对中国期货的支持")
print("="*80)

# 批量查询
url = API_URL + ",".join(test_codes)
print(f"\n请求URL: {url}\n")

try:
    response = requests.get(url, headers=HEADERS, timeout=10)
    
    # 尝试多种编码
    for encoding in ['gbk', 'utf-8', 'gb2312']:
        try:
            text = response.content.decode(encoding)
            break
        except:
            continue
    else:
        text = response.text
    
    print(f"响应内容:\n{text}\n")
    
    # 解析结果
    lines = text.strip().split(';')
    results = []
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
            
        match = re.match(r'v_([^=]+)="([^"]+)"', line)
        if match:
            code = match.group(1)
            data = match.group(2)
            
            # 检查是否有有效数据（不是空的或无法识别的）
            if data and not "pv_none_match" in line.lower():
                fields = data.split('~')
                name = fields[1] if len(fields) > 1 else "N/A"
                price = fields[3] if len(fields) > 3 else "N/A"
                
                if name and name != code and price:
                    results.append({
                        'code': code,
                        'name': name,
                        'price': price,
                        'data': data
                    })
    
    if results:
        print("="*80)
        print(f"找到 {len(results)} 个有效的期货品种：")
        print("="*80)
        
        for r in results:
            print(f"\n代码: {r['code']}")
            print(f"名称: {r['name']}")
            print(f"价格: {r['price']}")
            print(f"完整数据: {r['data']}")
    else:
        print("未找到有效的中国期货数据")
        
except Exception as e:
    print(f"请求异常: {e}")
    import traceback
    traceback.print_exc()

# 再查看一下 westockdata 的期货支持
print("\n" + "="*80)
print("查看项目其他文件中是否有期货相关信息...")
print("="*80)

import glob
import os

# 搜索项目中的期货相关文件
for pattern in ['**/*future*.py', '**/*期货*.py', '**/*FUTURE*']:
    files = glob.glob(os.path.join('d:/src/trading-skills', pattern), recursive=True)
    for f in files[:5]:
        print(f"\n找到: {f}")
