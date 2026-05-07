#!/usr/bin/env python3
"""调试腾讯期货数据"""

data = "4703.72,0.20,4705.20,4705.60,4730.50,4694.00,12:59:05,4694.30,4702.60,0,1,1,2026-05-07,纽约黄金"
fields = data.split(',')
print(f"原始字段数: {len(fields)}")
for i, f in enumerate(fields):
    print(f"  [{i}]: {f}")

last = float(fields[0])
change = float(fields[1])
prev = last - change
print(f"\nlast: {last}, change: {change}, prev: {prev}")
pct = (change / prev) * 100
print(f"涨跌幅: {pct}%")
