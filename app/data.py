# app/data.py
from __future__ import annotations
import pandas as pd
import yfinance as yf
from datetime import datetime, timedelta
import requests

_INTRADAY = {"1m":7, "2m":7, "5m":30, "15m":60, "30m":60, "90m":60, "1h":730}  # 天數上限（粗估）

def _parse_date(s):
    try:
        return datetime.fromisoformat(str(s).split(" ")[0])
    except Exception:
        if hasattr(s, "to_pydatetime"): return s.to_pydatetime()
        if hasattr(s, "year"): return datetime(s.year, s.month, s.day)
        raise

def _rename_cols(df: pd.DataFrame) -> pd.DataFrame:
    if df is None or df.empty:
        return pd.DataFrame()
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = [c[0] if isinstance(c, tuple) else c for c in df.columns]
    rename_map = {"Open":"open","High":"high","Low":"low","Close":"close","Adj Close":"close","Volume":"volume"}
    for k,v in rename_map.items():
        if k in df.columns: df.rename(columns={k:v}, inplace=True)
    return df

def fetch_ohlcv(ticker: str, start, end, interval: str = "1d") -> pd.DataFrame:
    ticker = str(ticker).upper().strip()
    start_dt = _parse_date(start); end_dt = _parse_date(end)

    # 先建立 session + UA（雲端比較不會被擋）
    sess = requests.Session()
    sess.headers.update({
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36"
    })

    # ① 正常路徑：start/end 或 intraday 用 period
    try:
        if interval in _INTRADAY:
            max_days = _INTRADAY[interval]
            start_dt = max(start_dt, end_dt - timedelta(days=max_days))
            period = f"{(end_dt - start_dt).days}d"
            df = yf.download(ticker, period=period, interval=interval,
                             auto_adjust=True, progress=False, session=sess, threads=False)
        else:
            df = yf.download(ticker,
                             start=start_dt.strftime("%Y-%m-%d"),
                             end=end_dt.strftime("%Y-%m-%d"),
                             interval=interval, auto_adjust=True,
                             progress=False, session=sess, threads=False)
        df = _rename_cols(df)
        if not df.empty:
            return df.reset_index()
    except Exception:
        pass

    # ② 後備：日線也用 period（很多雲端情況更穩）
    try:
        fallback_period = "5y" if interval not in _INTRADAY else "2y"
        df = yf.download(ticker, period=fallback_period, interval=interval,
                         auto_adjust=True, progress=False, session=sess, threads=False)
        df = _rename_cols(df)
        if not df.empty:
            # 再用 start/end 篩掉
            date_col = "Date" if "Date" in df.columns else df.columns[0]
            mask = (pd.to_datetime(df[date_col]) >= start_dt) & (pd.to_datetime(df[date_col]) <= end_dt)
            return df.loc[mask].reset_index(drop=True)
    except Exception:
        pass

    # ③ 最後備援：Ticker().history()
    try:
        tk = yf.Ticker(ticker, session=sess)
        hist = tk.history(period="5y" if interval not in _INTRADAY else "2y",
                          interval=interval, auto_adjust=True)
        hist = _rename_cols(hist)
        if not hist.empty:
            hist = hist.reset_index()
            date_col = "Date" if "Date" in hist.columns else hist.columns[0]
            mask = (pd.to_datetime(hist[date_col]) >= start_dt) & (pd.to_datetime(hist[date_col]) <= end_dt)
            return hist.loc[mask].reset_index(drop=True)
    except Exception:
        pass
    return pd.DataFrame()

