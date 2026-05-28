#!/usr/bin/env python3
"""
CCXT 统一加密货币数据接口
支持 100+ 交易所的行情/K线/深度/资金费率/成交记录
"""

import sys
import json
import argparse
from datetime import datetime, timezone

import ccxt


# ── 工具函数 ──────────────────────────────────────────────

def get_exchange(exchange_id: str = "binance") -> ccxt.Exchange:
    """获取交易所实例（公共行情，无需 API Key）"""
    exchange_id = exchange_id.lower()
    if exchange_id not in ccxt.exchanges:
        print(f"错误: 不支持的交易所 '{exchange_id}'", file=sys.stderr)
        print(f"可用交易所: {', '.join(sorted(ccxt.exchanges[:30]))}...", file=sys.stderr)
        sys.exit(1)
    exchange_class = getattr(ccxt, exchange_id)
    return exchange_class({"enableRateLimit": True})


def ts_to_str(ts_ms) -> str:
    """毫秒时间戳转可读字符串"""
    if ts_ms is None:
        return "N/A"
    return datetime.fromtimestamp(ts_ms / 1000, tz=timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")


def fmt_num(n, precision=8) -> str:
    """格式化数字，去掉尾部零"""
    if n is None:
        return "N/A"
    if isinstance(n, str):
        n = float(n)
    if abs(n) >= 1e9:
        return f"{n/1e9:.2f}B"
    if abs(n) >= 1e6:
        return f"{n/1e6:.2f}M"
    if abs(n) >= 1e3:
        return f"{n/1e3:.2f}K"
    return f"{n:.{precision}f}".rstrip("0").rstrip(".")


# ── 命令实现 ──────────────────────────────────────────────

def cmd_ticker(args):
    """实时行情"""
    ex = get_exchange(args.exchange)
    symbol = args.symbol.upper().replace("-", "/")
    # 永续合约格式修正: BTC/USDT:USDT
    if ":" not in symbol and "/USDT" in symbol and args.swap:
        symbol = f"{symbol}:USDT"

    ticker = ex.fetch_ticker(symbol)

    print(f"═══ {symbol} @ {args.exchange} ═══")
    print(f"  最新价:    {fmt_num(ticker['last'])}")
    print(f"  买一:      {fmt_num(ticker['bid'])}")
    print(f"  卖一:      {fmt_num(ticker['ask'])}")
    print(f"  24h涨跌:   {ticker.get('percentage', 'N/A')}%")
    print(f"  24h最高:   {fmt_num(ticker['high'])}")
    print(f"  24h最低:   {fmt_num(ticker['low'])}")
    print(f"  24h成交量: {fmt_num(ticker['baseVolume'])} ({ticker.get('symbol', symbol).split('/')[0]})")
    print(f"  24h成交额: {fmt_num(ticker['quoteVolume'])} USDT")
    print(f"  时间:      {ts_to_str(ticker['timestamp'])}")


def cmd_kline(args):
    """K线数据"""
    ex = get_exchange(args.exchange)
    symbol = args.symbol.upper().replace("-", "/")
    if ":" not in symbol and "/USDT" in symbol and args.swap:
        symbol = f"{symbol}:USDT"

    ohlcv = ex.fetch_ohlcv(symbol, timeframe=args.timeframe, limit=args.limit)

    if not ohlcv:
        print(f"无数据: {symbol} {args.timeframe}")
        return

    # CSV 输出
    print("timestamp,open,high,low,close,volume")
    for candle in ohlcv:
        ts, o, h, l, c, v = candle
        print(f"{ts_to_str(ts)},{o},{h},{l},{c},{v}")

    print(f"\n共 {len(ohlcv)} 根K线 | {symbol} {args.timeframe} @ {args.exchange}", file=sys.stderr)


def cmd_depth(args):
    """订单簿深度"""
    ex = get_exchange(args.exchange)
    symbol = args.symbol.upper().replace("-", "/")
    if ":" not in symbol and "/USDT" in symbol and args.swap:
        symbol = f"{symbol}:USDT"

    orderbook = ex.fetch_order_book(symbol, limit=args.limit)

    bids = orderbook.get("bids", [])[:args.limit]
    asks = orderbook.get("asks", [])[:args.limit]

    bid_vol = sum(float(b[1]) for b in bids)
    ask_vol = sum(float(a[1]) for a in asks)
    ratio = bid_vol / ask_vol if ask_vol > 0 else float("inf")

    print(f"═══ {symbol} 订单簿 @ {args.exchange} (Top {args.limit}) ═══")
    print(f"\n{'卖盘(asks)':>30}  │  {'买盘(bids)':<30}")
    print("─" * 65)

    max_rows = max(len(bids), len(asks))
    for i in range(max_rows):
        ask_str = ""
        if i < len(asks):
            price, qty = asks[len(asks) - 1 - i]
            ask_str = f"{fmt_num(price):>14} × {fmt_num(qty):>12}"

        bid_str = ""
        if i < len(bids):
            price, qty = bids[i]
            bid_str = f"{fmt_num(price):>14} × {fmt_num(qty):<12}"

        print(f"{ask_str:>30}  │  {bid_str:<30}")

    print("─" * 65)
    print(f"  卖量合计: {fmt_num(ask_vol):>14}  │  买量合计: {fmt_num(bid_vol):<14}")
    print(f"  买卖比:   {ratio:.4f}  {'偏多 ✅' if ratio > 1.05 else '偏空 ❌' if ratio < 0.95 else '均衡 ⚖️'}")


def cmd_funding(args):
    """资金费率"""
    ex = get_exchange(args.exchange)
    symbol = args.symbol.upper().replace("-", "/")

    # 确保是永续合约格式
    if ":" not in symbol:
        if "/USDT" in symbol:
            symbol = f"{symbol}:USDT"
        elif "/USD" in symbol:
            symbol = f"{symbol}:USD"

    funding = ex.fetch_funding_rate(symbol)

    rate = funding.get("fundingRate", "N/A")
    next_rate = funding.get("nextFundingRate", "N/A")
    timestamp = funding.get("fundingTimestamp")

    print(f"═══ {symbol} 资金费率 @ {args.exchange} ═══")
    if rate != "N/A":
        print(f"  当前费率:   {rate * 100:.4f}%")
        print(f"  年化费率:   {rate * 3 * 365 * 100:.2f}%")
    else:
        print(f"  当前费率:   N/A")
    if next_rate is not None and next_rate != "N/A":
        print(f"  预测费率:   {next_rate * 100:.4f}%")
    if timestamp:
        print(f"  结算时间:   {ts_to_str(timestamp)}")


def cmd_trades(args):
    """最近成交"""
    ex = get_exchange(args.exchange)
    symbol = args.symbol.upper().replace("-", "/")
    if ":" not in symbol and "/USDT" in symbol and args.swap:
        symbol = f"{symbol}:USDT"

    trades = ex.fetch_trades(symbol, limit=args.limit)

    print(f"═══ {symbol} 最近成交 @ {args.exchange} ═══")
    print(f"{'时间':>22}  {'方向':>4}  {'价格':>14}  {'数量':>14}")
    print("─" * 60)

    for t in trades:
        side = "🟢买" if t["side"] == "buy" else "🔴卖"
        print(f"{ts_to_str(t['timestamp']):>22}  {side:>4}  {fmt_num(t['price']):>14}  {fmt_num(t['amount']):>14}")

    print(f"\n共 {len(trades)} 条成交", file=sys.stderr)


def cmd_exchanges(args):
    """列出支持的交易所"""
    exchanges = sorted(ccxt.exchanges)
    print(f"═══ CCXT 支持的交易所 ({len(exchanges)} 个) ═══\n")

    # 按字母分组显示，每行5个
    for i in range(0, len(exchanges), 5):
        row = exchanges[i:i+5]
        print("  ".join(f"{e:<14}" for e in row))


def cmd_markets(args):
    """列出交易所市场"""
    ex = get_exchange(args.exchange)
    ex.load_markets()

    print(f"═══ {args.exchange} 市场 ({len(ex.symbols)} 个交易对) ═══\n")

    # 按类型分组
    spot = []
    swap = []
    future = []
    other = []

    for symbol, market in ex.markets.items():
        mtype = market.get("type", "unknown")
        if mtype == "spot":
            spot.append(symbol)
        elif mtype == "swap":
            swap.append(symbol)
        elif mtype == "future":
            future.append(symbol)
        else:
            other.append(symbol)

    if spot:
        print(f"【现货 Spot】({len(spot)} 个)")
        for s in sorted(spot)[:30]:
            print(f"  {s}")
        if len(spot) > 30:
            print(f"  ... 还有 {len(spot) - 30} 个")

    if swap:
        print(f"\n【永续合约 Swap】({len(swap)} 个)")
        for s in sorted(swap)[:20]:
            print(f"  {s}")
        if len(swap) > 20:
            print(f"  ... 还有 {len(swap) - 20} 个")

    if future:
        print(f"\n【交割合约 Future】({len(future)} 个)")
        for s in sorted(future)[:20]:
            print(f"  {s}")
        if len(future) > 20:
            print(f"  ... 还有 {len(future) - 20} 个")

    print(f"\n合计: 现货 {len(spot)} | 永续 {len(swap)} | 交割 {len(future)} | 其他 {len(other)}", file=sys.stderr)


# ── 主入口 ──────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="CCXT 统一加密货币数据接口 (100+交易所)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  %(prog)s ticker BTC/USDT                         # BTC实时行情
  %(prog)s ticker ETH/USDT --exchange okx           # OKX的ETH行情
  %(prog)s kline BTC/USDT --timeframe 1h --limit 50 # 1小时K线
  %(prog)s depth BTC/USDT --limit 10                # 10档深度
  %(prog)s funding BTC/USDT:USDT                    # 资金费率
  %(prog)s trades BTC/USDT --limit 20               # 最近20笔成交
  %(prog)s exchanges                                # 列出所有交易所
  %(prog)s markets --exchange okx                   # OKX市场列表
        """,
    )

    parser.add_argument("--exchange", "-e", default="binance", help="交易所ID (默认: binance)")
    parser.add_argument("--swap", action="store_true", default=True, help="自动追加永续合约后缀 (默认开启)")
    parser.add_argument("--no-swap", action="store_false", dest="swap", help="禁用永续合约自动追加")

    sub = parser.add_subparsers(dest="command", help="命令")

    # ticker
    p_ticker = sub.add_parser("ticker", help="实时行情")
    p_ticker.add_argument("symbol", help="交易对，如 BTC/USDT")

    # kline
    p_kline = sub.add_parser("kline", help="K线数据")
    p_kline.add_argument("symbol", help="交易对")
    p_kline.add_argument("--timeframe", "-t", default="1h", help="K线周期 (1m/5m/15m/1h/4h/1d/1w)")
    p_kline.add_argument("--limit", "-l", type=int, default=100, help="返回条数 (默认100)")

    # depth
    p_depth = sub.add_parser("depth", help="订单簿深度")
    p_depth.add_argument("symbol", help="交易对")
    p_depth.add_argument("--limit", "-l", type=int, default=10, help="深度档位 (默认10)")

    # funding
    p_funding = sub.add_parser("funding", help="资金费率")
    p_funding.add_argument("symbol", help="交易对，如 BTC/USDT:USDT")

    # trades
    p_trades = sub.add_parser("trades", help="最近成交")
    p_trades.add_argument("symbol", help="交易对")
    p_trades.add_argument("--limit", "-l", type=int, default=20, help="返回条数 (默认20)")

    # exchanges
    sub.add_parser("exchanges", help="列出支持的交易所")

    # markets
    sub.add_parser("markets", help="列出交易所市场")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(0)

    commands = {
        "ticker": cmd_ticker,
        "kline": cmd_kline,
        "depth": cmd_depth,
        "funding": cmd_funding,
        "trades": cmd_trades,
        "exchanges": cmd_exchanges,
        "markets": cmd_markets,
    }

    try:
        commands[args.command](args)
    except ccxt.BadSymbol as e:
        print(f"交易对错误: {e}", file=sys.stderr)
        sys.exit(1)
    except ccxt.ExchangeNotAvailable as e:
        print(f"交易所不可用: {e}", file=sys.stderr)
        sys.exit(1)
    except ccxt.NetworkError as e:
        print(f"网络错误: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"错误: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
