"""缠论形态识别信号引擎。

基于 czsc 库实现缠中说禅理论的买卖点信号生成。
适配 czsc 0.10.x 新版 API（generate_czsc_signals）。
核心链路：K线 → 分型 → 笔 → 中枢 → 买卖点。
"""

from typing import Dict
from datetime import datetime

import pandas as pd
from czsc import CZSC, RawBar, Freq


# czsc 0.10.x signals_config 使用完整模块路径
_SIGNALS_CONFIG = [
    {"name": "czsc.signals.cxt_first_buy_V221126", "freq": "日线", "di": 1},
    {"name": "czsc.signals.cxt_first_sell_V221126", "freq": "日线", "di": 1},
    {"name": "czsc.signals.cxt_three_bi_V230618", "freq": "日线", "di": 1},
    {"name": "czsc.signals.cxt_five_bi_V230619", "freq": "日线", "di": 1},
    {"name": "czsc.signals.cxt_bi_base_V230228", "freq": "日线", "di": 1},
]


def _df_to_bars(df: pd.DataFrame, symbol: str, freq: Freq = Freq.D) -> list:
    """将 OHLCV DataFrame 转换为 czsc RawBar 列表。"""
    bars = []
    for i, (dt, row) in enumerate(df.iterrows()):
        if not isinstance(dt, datetime):
            dt = pd.Timestamp(dt).to_pydatetime()
        bars.append(RawBar(
            symbol=symbol,
            id=i,
            dt=dt,
            freq=freq,
            open=float(row["open"]),
            close=float(row["close"]),
            high=float(row["high"]),
            low=float(row["low"]),
            vol=float(row.get("volume", row.get("vol", 0))),
            amount=float(row.get("amount", 0)),
        ))
    return bars


class SignalEngine:
    """缠论形态识别信号引擎。

    基于分型→笔→中枢→买卖点链路，生成做多/做空/观望信号。
    使用 czsc 0.10.x generate_czsc_signals 批量计算。
    """

    def __init__(self, freq: Freq = Freq.D):
        self.freq = freq

    def generate(self, data_map: Dict[str, pd.DataFrame]) -> Dict[str, pd.Series]:
        """根据缠论形态生成交易信号。"""
        from czsc import generate_czsc_signals

        result = {}
        for code, df in data_map.items():
            signal = pd.Series(0, index=df.index)
            bars = _df_to_bars(df, code, self.freq)

            if len(bars) < 50:
                result[code] = signal
                continue

            try:
                # 使用新版 API 批量生成信号
                sig_df = generate_czsc_signals(
                    bars,
                    signals_config=_SIGNALS_CONFIG,
                    init_n=50,
                    df=True,
                )

                if sig_df is None or sig_df.empty:
                    result[code] = signal
                    continue

                # 对齐信号到原始 DataFrame 的 index
                sig_df = sig_df.set_index("dt")
                common_idx = df.index.intersection(sig_df.index)

                for idx in common_idx:
                    if idx not in sig_df.index:
                        continue
                    row = sig_df.loc[idx]

                    # 一买信号
                    buy1 = str(row.get("日线_D1B_BUY1", ""))
                    if "一买" in buy1:
                        signal.loc[idx] = 1
                        continue

                    # 一卖信号
                    sell1 = str(row.get("日线_D1B_SELL1", ""))
                    if "一卖" in sell1:
                        signal.loc[idx] = -1
                        continue

                    # 三笔形态
                    three = str(row.get("日线_D1三笔_形态V230618", ""))
                    if "向上盘背" in three or "三买" in three:
                        signal.loc[idx] = 1
                    elif "向下盘背" in three or "三卖" in three:
                        signal.loc[idx] = -1

                    # 五笔形态
                    five = str(row.get("日线_D1五笔_形态V230619", ""))
                    if "类一买" in five:
                        signal.loc[idx] = 1
                    elif "类一卖" in five:
                        signal.loc[idx] = -1

            except Exception:
                # 降级到简化分析：仅用分型判断方向
                try:
                    c = CZSC(bars_raw=bars)
                    if len(c.bi_list) >= 3:
                        last_bi = c.bi_list[-1]
                        if last_bi.fx_list and last_bi.fx_list[-1].mark.value == "d":
                            signal.iloc[-1] = 1  # 底分型，看多
                        elif last_bi.fx_list and last_bi.fx_list[-1].mark.value == "g":
                            signal.iloc[-1] = -1  # 顶分型，看空
                except Exception:
                    pass

            result[code] = signal
        return result


if __name__ == "__main__":
    import requests

    BASE_URL = "https://www.okx.com/api/v5"
    resp = requests.get(f"{BASE_URL}/market/candles", params={
        "instId": "BTC-USDT", "bar": "1D", "limit": "300"
    })
    candles = resp.json()["data"]
    columns = ["ts", "open", "high", "low", "close", "vol", "volCcy", "volCcyQuote", "confirm"]
    df = pd.DataFrame(reversed(candles), columns=columns)
    df["ts"] = pd.to_datetime(df["ts"].astype("int64"), unit="ms")
    df = df.set_index("ts")
    for col in ["open", "high", "low", "close"]:
        df[col] = df[col].astype(float)
    df["volume"] = df["vol"].astype(float)
    df["amount"] = df["volCcy"].astype(float)

    engine = SignalEngine(freq=Freq.D)
    signals = engine.generate({"BTC-USDT": df})
    sig = signals["BTC-USDT"]
    print(f"BTC-USDT 缠论信号: 做多 {( sig == 1).sum()}, 做空 {(sig == -1).sum()}")
