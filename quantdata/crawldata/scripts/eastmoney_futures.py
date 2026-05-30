"""
国内期货实时行情 — 新浪/东方财富 API

✅ 主力API（2026-05-30 验证可用）:
    URL:     https://stock2.finance.sina.com.cn/futures/api/jsonp.php/=/InnerFuturesNewService.getFewMinLine
    参数:    symbol=ZN0  type=5
    返回:    JSON数组，每条含 d/datetime, o/open, h/high, l/low, c/close, v/volume, p/hold
    实时性:  最新 2026-06-01 00:00 ✅ 实时更新
    频率:    5分钟K线，保留约1023条（≈170个交易日）
    Header:  Referer=https://finance.sina.com.cn/

⚠️ 旧接口（已失效）:
    http://hq.sinajs.cn/list=nf_ZN0 → 返回 null

主力合约代码（新浪格式）:
    ZN0=沪锌  CU0=沪铜  AL0=沪铝  NI0=沪镍  AU0=沪金  AG0=沪银
    RB0=螺纹钢  I0=铁矿石   SC0=原油   J0=焦炭   JM0=焦煤
    TA0=PTA    MA0=甲醇    RU0=橡胶   V0=PVC
    格式: XX0=连续合约, XXYYMM=具体月份合约
"""

import requests
import json
import re
import time
import random
from datetime import datetime, timedelta
from typing import List, Dict, Optional

# ─── API 常量 ───────────────────────────────────────────────────────
SINA_FUTURES_URL = "https://stock2.finance.sina.com.cn/futures/api/jsonp.php/=/InnerFuturesNewService.getFewMinLine"
SINA_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "Referer": "https://finance.sina.com.cn/",
}

# ─── 主力合约表 ──────────────────────────────────────────────────────
MAIN_CONTRACTS: Dict[str, str] = {
    "ZN0": "沪锌",
    "CU0": "沪铜",
    "AL0": "沪铝",
    "NI0": "沪镍",
    "PB0": "沪铅",
    "AU0": "沪金",
    "AG0": "沪银",
    "RB0": "螺纹钢",
    "HC0": "热卷",
    "I0":  "铁矿石",
    "J0":  "焦炭",
    "JM0": "焦煤",
    "SC0": "原油",
    "BU0": "沥青",
    "RU0": "橡胶",
    "FU0": "燃油",
    "V0":  "PVC",
    "L0":  "聚乙烯",
    "PP0": "聚丙烯",
    "TA0": "PTA",
    "MA0": "甲醇",
    "EG0": "乙二醇",
    "P0":  "棕榈油",
    "M0":  "豆粕",
    "Y0":  "豆油",
    "C0":  "玉米",
    "CF0": "棉花",
    "SR0": "白糖",
    "LH0": "生猪",
}

# 反向映射
NAME_TO_SYMBOL: Dict[str, str] = {v: k for k, v in MAIN_CONTRACTS.items()}

# ─── 工具函数 ───────────────────────────────────────────────────────

def _parse_response(text: str) -> List[Dict]:
    """解析 =(JSON); 格式"""
    m = re.search(r"=\((.+)\);", text, re.DOTALL)
    if not m:
        return []
    return json.loads(m.group(1))


def _to_float(v, default=0.0) -> float:
    try:
        return float(v)
    except (TypeError, ValueError):
        return default


def _rate_limit():
    """请求间隔，避免被封"""
    time.sleep(random.uniform(0.2, 0.5))


# ─── 核心接口 ───────────────────────────────────────────────────────

def get_minute_bars(symbol: str, period: str = "5") -> List[Dict]:
    """
    获取新浪期货分钟K线数据（实时）

    Args:
        symbol: 合约代码，如 "ZN0", "AU0"
        period: "1"/"5"/"15"/"30"/"60" 分钟

    Returns:
        K线列表，每条含 datetime/open/high/low/close/volume/hold
        最新一条 = 当前实时行情
    """
    _rate_limit()
    params = {"symbol": symbol.upper(), "type": period}
    try:
        resp = requests.get(
            SINA_FUTURES_URL,
            params=params,
            headers=SINA_HEADERS,
            timeout=10,
        )
        data = _parse_response(resp.text)
        if not data:
            return []
        result = []
        for item in data:
            result.append({
                "datetime": item.get("d", ""),
                "open":    _to_float(item.get("o")),
                "high":    _to_float(item.get("h")),
                "low":     _to_float(item.get("l")),
                "close":   _to_float(item.get("c")),
                "volume":  int(_to_float(item.get("v"))),
                "hold":    int(_to_float(item.get("p"))),
            })
        return result
    except Exception:
        return []


def get_latest_price(symbol: str, period: str = "5") -> Dict:
    """
    获取最新一条K线数据 = 当前实时价格
    """
    bars = get_minute_bars(symbol, period)
    if not bars:
        return {"error": f"获取失败: {symbol}"}

    latest = bars[-1]
    prev   = bars[-2] if len(bars) >= 2 else latest

    c    = latest["close"]
    o    = latest["open"]
    prev_c = prev["close"]
    chg    = c - prev_c
    chg_pct = chg / prev_c * 100 if prev_c else 0

    return {
        "symbol":   symbol.upper(),
        "name":     MAIN_CONTRACTS.get(symbol.upper(), symbol),
        "datetime": latest["datetime"][:16],
        "open":     o,
        "high":     latest["high"],
        "low":      latest["low"],
        "close":    c,
        "prev_close": prev_c,
        "chg":      chg,
        "chg_pct":  round(chg_pct, 2),
        "volume":   latest["volume"],
        "hold":     latest["hold"],
        "direction": "▲" if chg >= 0 else "▼",
        "emoji":    "🔴" if chg >= 0 else "🟢",
    }


def query(name: str) -> Dict:
    """
    按中文品种名快速查询实时行情
    例: query("沪锌") / query("黄金")
    """
    sym = NAME_TO_SYMBOL.get(name)
    if not sym:
        # 模糊匹配
        for n, s in NAME_TO_SYMBOL.items():
            if name.lower() in n.lower() or n.lower() in name.lower():
                sym = s
                name = n
                break
    if not sym:
        return {"error": f"未找到品种: {name}"}
    return get_latest_price(sym)


def format_info(info: Dict) -> str:
    """美化打印"""
    if "error" in info:
        return f"❌ {info['error']}"
    name = info.get("name", "")
    sym  = info.get("symbol", "")
    dt   = info.get("datetime", "")
    c    = info.get("close", 0)
    chg  = info.get("chg", 0)
    pct  = info.get("chg_pct", 0)
    h    = info.get("high", 0)
    l    = info.get("low", 0)
    vol  = info.get("volume", 0)
    d    = info.get("direction", "")
    sign = "+" if chg >= 0 else ""
    return (
        f"{name}({sym}) {dt}\n"
        f"  最新: {c:>10.2f}  {d}{sign}{abs(chg):.2f} ({sign}{pct}%)\n"
        f"  最高: {h:.2f}  最低: {l:.2f}  成交量: {vol:,}"
    )


# ─── 演示 ──────────────────────────────────────────────────────────
if __name__ == "__main__":
    print("=== 国内期货实时行情 (新浪) ===\n")

    targets = ["沪锌", "沪金", "沪银", "沪铜", "原油", "铁矿石"]
    for name in targets:
        print(format_info(query(name)))
        print()
