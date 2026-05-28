#!/usr/bin/env python3
"""
综合技术分析报告生成器
整合 7 大技术分析体系，一键生成多维度技术面报告。

用法:
    python3 ta_report.py BTC/USDT
    python3 ta_report.py BTC/USDT --exchange okx --timeframe 4h
    python3 ta_report.py 000001.SZ --exchange akshare
    python3 ta_report.py BTC/USDT --engines candlestick,technical-basic,ichimoku
"""

import sys
import os
import argparse
import importlib
import importlib.util
from datetime import datetime, timezone
from typing import Dict, List, Optional, Tuple

import numpy as np
import pandas as pd

# ── 路径设置 ──────────────────────────────────────────────

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
SKILL_DIR = os.path.dirname(SCRIPT_DIR)

# Vibe-Trading 引擎路径
# scripts → tech-analysis → skills → trading-skills → projects → Vibe-Trading
_VIBE_BASE = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(SCRIPT_DIR))))
VIBE_ENGINES_DIR = os.path.normpath(os.path.join(_VIBE_BASE, "Vibe-Trading", "agent", "src", "skills"))

# ── 引擎注册表 ──────────────────────────────────────────

ENGINE_REGISTRY = {
    "candlestick": {
        "name": "K线形态",
        "path": "candlestick",
        "weight": 1,
        "required": False,
    },
    "chanlun": {
        "name": "缠论",
        "path": "chanlun",
        "weight": 1.5,
        "required": False,
        "deps": ["czsc"],
    },
    "elliott-wave": {
        "name": "艾略特波浪",
        "path": "elliott-wave",
        "weight": 1,
        "required": False,
    },
    "harmonic": {
        "name": "谐波形态",
        "path": "harmonic",
        "weight": 1,
        "required": False,
    },
    "ichimoku": {
        "name": "一目均衡",
        "path": "ichimoku",
        "weight": 1,
        "required": False,
    },
    "smc": {
        "name": "SMC/ICT",
        "path": "smc",
        "weight": 1,
        "required": False,
        "deps": ["smartmoneyconcepts"],
    },
    "technical-basic": {
        "name": "基础指标",
        "path": "technical-basic",
        "weight": 1,
        "required": False,
    },
}

# ── 引擎加载 ──────────────────────────────────────────────

def _load_engine(engine_id: str):
    """动态加载 Vibe-Trading 引擎"""
    info = ENGINE_REGISTRY[engine_id]

    # 检查依赖
    for dep in info.get("deps", []):
        try:
            importlib.import_module(dep)
        except ImportError:
            print(f"  ⚠️  跳过 {info['name']}（缺少依赖: {dep}）", file=sys.stderr)
            return None

    # 加载引擎模块
    engine_path = os.path.join(VIBE_ENGINES_DIR, info["path"], "example_signal_engine.py")
    if not os.path.exists(engine_path):
        print(f"  ⚠️  跳过 {info['name']}（引擎文件不存在: {engine_path}）", file=sys.stderr)
        return None

    try:
        spec = importlib.util.spec_from_file_location(
            f"engine_{engine_id}", engine_path
        )
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        return mod.SignalEngine()
    except Exception as e:
        print(f"  ⚠️  跳过 {info['name']}（加载失败: {e}）", file=sys.stderr)
        return None


def load_engines(engine_ids: List[str]) -> Dict[str, object]:
    """批量加载引擎"""
    engines = {}
    for eid in engine_ids:
        engine = _load_engine(eid)
        if engine is not None:
            engines[eid] = engine
    return engines


# ── 数据获取 ──────────────────────────────────────────────

def fetch_data(symbol: str, exchange: str = "binance", timeframe: str = "1d",
               limit: int = 200) -> pd.DataFrame:
    """获取 OHLCV 数据"""
    symbol_upper = symbol.upper().replace("-", "/")

    # 加密货币通过 ccxt
    if exchange in ("binance", "okx", "bybit", "gate", "htx", "kucoin", "bitget"):
        try:
            import ccxt
            ex_class = getattr(ccxt, exchange)
            ex = ex_class({"enableRateLimit": True})
            ohlcv = ex.fetch_ohlcv(symbol_upper, timeframe=timeframe, limit=limit)
            df = pd.DataFrame(ohlcv, columns=["timestamp", "open", "high", "low", "close", "volume"])
            df["timestamp"] = pd.to_datetime(df["timestamp"], unit="ms")
            df.set_index("timestamp", inplace=True)
            return df
        except Exception as e:
            print(f"ccxt 获取失败: {e}", file=sys.stderr)

    # A股通过 akshare
    if exchange == "akshare":
        try:
            import akshare as ak
            code = symbol.split(".")[0] if "." in symbol else symbol
            df = ak.stock_zh_a_hist(symbol=code, period="daily", adjust="qfq")
            df = df.rename(columns={
                "日期": "timestamp", "开盘": "open", "最高": "high",
                "最低": "low", "收盘": "close", "成交量": "volume"
            })
            df["timestamp"] = pd.to_datetime(df["timestamp"])
            df.set_index("timestamp", inplace=True)
            return df[["open", "high", "low", "close", "volume"]].tail(limit)
        except Exception as e:
            print(f"akshare 获取失败: {e}", file=sys.stderr)

    # 美股/港股通过 yfinance
    if exchange == "yfinance":
        try:
            import yfinance as yf
            ticker = yf.Ticker(symbol)
            df = ticker.history(period="6mo", interval=timeframe)
            df = df.rename(columns={
                "Open": "open", "High": "high", "Low": "low",
                "Close": "close", "Volume": "volume"
            })
            return df[["open", "high", "low", "close", "volume"]].tail(limit)
        except Exception as e:
            print(f"yfinance 获取失败: {e}", file=sys.stderr)

    raise RuntimeError(f"无法从 {exchange} 获取 {symbol} 的数据")


# ── 报告生成 ──────────────────────────────────────────────

def run_engines(engines: Dict[str, object], data_map: Dict[str, pd.DataFrame]) -> Dict[str, Dict]:
    """运行所有引擎，收集结果"""
    results = {}
    for eid, engine in engines.items():
        info = ENGINE_REGISTRY[eid]
        try:
            signals = engine.generate(data_map)
            # 取第一个 symbol 的信号
            for sym, sig in signals.items():
                latest = sig.iloc[-1] if len(sig) > 0 else 0
                recent = sig.tail(10)
                bull_count = int((recent == 1).sum())
                bear_count = int((recent == -1).sum())
                results[eid] = {
                    "name": info["name"],
                    "signal": int(latest),
                    "bull_count": bull_count,
                    "bear_count": bear_count,
                    "series": sig,
                }
                break
        except Exception as e:
            print(f"  ⚠️  {info['name']} 运行失败: {e}", file=sys.stderr)
    return results


def compute_key_levels(df: pd.DataFrame) -> Dict:
    """计算关键价位"""
    close = df["close"].iloc[-1]
    high = df["high"]
    low = df["low"]

    # 近期高低点
    recent_high = high.tail(20).max()
    recent_low = low.tail(20).min()

    # 布林带
    sma20 = df["close"].rolling(20).mean().iloc[-1]
    std20 = df["close"].rolling(20).std().iloc[-1]
    bb_upper = sma20 + 2 * std20
    bb_lower = sma20 - 2 * std20

    return {
        "close": close,
        "recent_high": recent_high,
        "recent_low": recent_low,
        "bb_upper": bb_upper,
        "bb_middle": sma20,
        "bb_lower": bb_lower,
    }


def format_report(symbol: str, exchange: str, timeframe: str,
                  results: Dict[str, Dict], levels: Dict,
                  fmt: str = "text") -> str:
    """格式化报告"""
    if fmt == "json":
        return _format_json(symbol, exchange, timeframe, results, levels)

    lines = []
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")

    # 标题
    lines.append(f"═══ {symbol} 技术分析报告 ═══")
    lines.append(f"时间: {now} | 周期: {timeframe} | 收盘: {levels['close']:,.2f}")
    lines.append("")

    # 综合信号
    total_score = 0
    bull_engines = []
    bear_engines = []
    neutral_engines = []

    for eid, r in results.items():
        sig = r["signal"]
        weight = ENGINE_REGISTRY[eid]["weight"]
        total_score += sig * weight
        if sig > 0:
            bull_engines.append(r["name"])
        elif sig < 0:
            bear_engines.append(r["name"])
        else:
            neutral_engines.append(r["name"])

    max_score = sum(ENGINE_REGISTRY[eid]["weight"] for eid in results)

    if total_score >= max_score * 0.5:
        verdict = "强烈看多 🟢🟢"
    elif total_score >= max_score * 0.2:
        verdict = "偏多 🟢"
    elif total_score <= -max_score * 0.5:
        verdict = "强烈看空 🔴🔴"
    elif total_score <= -max_score * 0.2:
        verdict = "偏空 🔴"
    else:
        verdict = "中性/震荡 ⚖️"

    lines.append("── 1. 综合信号 ──────────────")
    lines.append(f"看多: {', '.join(bull_engines) if bull_engines else '无'}")
    lines.append(f"看空: {', '.join(bear_engines) if bear_engines else '无'}")
    lines.append(f"中性: {', '.join(neutral_engines) if neutral_engines else '无'}")
    lines.append(f"综合评分: {total_score:+.1f} (范围 {-max_score:.0f} ~ +{max_score:.0f}) → {verdict}")
    lines.append("")

    # 各引擎详情
    section_num = 2
    for eid, r in results.items():
        sig = r["signal"]
        sig_text = {1: "看多 ✅", -1: "看空 ❌", 0: "中性 ⚖️"}.get(sig, "未知")

        lines.append(f"── {section_num}. {r['name']} ──────────────")
        lines.append(f"  当前信号: {sig_text}")
        lines.append(f"  近10期: {r['bull_count']}看多 / {r['bear_count']}看空")

        # 各引擎特色信息
        if eid == "ichimoku":
            series = r["series"]
            if len(series) > 0:
                lines.append(f"  价格与云带: {'云上方(看多)' if series.iloc[-1] > 0 else '云下方(看空)' if series.iloc[-1] < 0 else '云中(观望)'}")

        if eid == "technical-basic":
            series = r["series"]
            if len(series) > 0:
                # 显示最近趋势
                recent = series.tail(5)
                trend = "上升" if (recent.diff() > 0).all() else "下降" if (recent.diff() < 0).all() else "波动"
                lines.append(f"  近5期趋势: {trend}")

        lines.append("")
        section_num += 1

    # 关键价位
    lines.append(f"── {section_num}. 关键价位 ──────────────")
    lines.append(f"  强阻力: {levels['recent_high']:,.2f} (近20日高点)")
    lines.append(f"  弱阻力: {levels['bb_upper']:,.2f} (BB上轨)")
    lines.append(f"  当前价: {levels['close']:,.2f}")
    lines.append(f"  弱支撑: {levels['bb_lower']:,.2f} (BB下轨)")
    lines.append(f"  强支撑: {levels['recent_low']:,.2f} (近20日低点)")
    lines.append("")

    return "\n".join(lines)


def _format_json(symbol, exchange, timeframe, results, levels):
    """JSON 格式输出"""
    import json
    data = {
        "symbol": symbol,
        "exchange": exchange,
        "timeframe": timeframe,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "close": levels["close"],
        "signals": {},
        "levels": levels,
    }
    for eid, r in results.items():
        data["signals"][eid] = {
            "name": r["name"],
            "signal": r["signal"],
            "bull_count": r["bull_count"],
            "bear_count": r["bear_count"],
        }
    return json.dumps(data, indent=2, ensure_ascii=False)


# ── 主入口 ──────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="综合技术分析报告生成器 — 整合7大技术分析体系",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  %(prog)s BTC/USDT                                  # BTC日线综合报告
  %(prog)s BTC/USDT -e okx -t 4h                     # OKX 4小时线
  %(prog)s 000001.SZ -e akshare                       # A股平安银行
  %(prog)s ETH/USDT --engines candlestick,ichimoku    # 只跑K线+一目
  %(prog)s BTC/USDT --format json                     # JSON输出
        """,
    )

    parser.add_argument("symbol", nargs="?", help="标的代码 (如 BTC/USDT, 000001.SZ)")
    parser.add_argument("-e", "--exchange", default="binance",
                        help="数据源 (binance/okx/akshare/yfinance, 默认: binance)")
    parser.add_argument("-t", "--timeframe", default="1d",
                        help="K线周期 (1m/5m/15m/1h/4h/1d/1w, 默认: 1d)")
    parser.add_argument("-l", "--limit", type=int, default=200,
                        help="获取K线数量 (默认: 200)")
    parser.add_argument("--engines", default=None,
                        help="指定引擎 (逗号分隔, 默认全部)")
    parser.add_argument("--format", choices=["text", "markdown", "json"],
                        default="text", help="输出格式 (默认: text)")
    parser.add_argument("--list-engines", action="store_true",
                        help="列出所有可用引擎")

    args = parser.parse_args()

    # 列出引擎
    if args.list_engines:
        print("可用引擎:")
        for eid, info in ENGINE_REGISTRY.items():
            deps = info.get("deps", [])
            dep_str = f" (需要: {','.join(deps)})" if deps else ""
            print(f"  {eid:<20} {info['name']:<10}{dep_str}")
        return

    if not args.symbol:
        parser.error("请指定标的代码 (如 BTC/USDT)")

    # 确定引擎列表
    if args.engines:
        engine_ids = [e.strip() for e in args.engines.split(",")]
        for eid in engine_ids:
            if eid not in ENGINE_REGISTRY:
                print(f"错误: 未知引擎 '{eid}'", file=sys.stderr)
                print(f"可用: {', '.join(ENGINE_REGISTRY.keys())}", file=sys.stderr)
                sys.exit(1)
    else:
        engine_ids = list(ENGINE_REGISTRY.keys())

    # 加载引擎
    print(f"加载引擎...", file=sys.stderr)
    engines = load_engines(engine_ids)
    if not engines:
        print("错误: 没有可用的引擎", file=sys.stderr)
        sys.exit(1)
    print(f"已加载: {', '.join(ENGINE_REGISTRY[eid]['name'] for eid in engines)}", file=sys.stderr)

    # 获取数据
    print(f"获取数据: {args.symbol} @ {args.exchange} ({args.timeframe})...", file=sys.stderr)
    try:
        df = fetch_data(args.symbol, args.exchange, args.timeframe, args.limit)
    except Exception as e:
        print(f"错误: {e}", file=sys.stderr)
        sys.exit(1)
    print(f"获取 {len(df)} 根K线", file=sys.stderr)

    # 构建 data_map（引擎要求 Dict[symbol, DataFrame]）
    data_map = {args.symbol: df}

    # 运行引擎
    print(f"运行分析...", file=sys.stderr)
    results = run_engines(engines, data_map)

    # 计算关键价位
    levels = compute_key_levels(df)

    # 生成报告
    report = format_report(
        args.symbol, args.exchange, args.timeframe,
        results, levels, args.format
    )
    print(report)


if __name__ == "__main__":
    main()
