from __future__ import annotations
import pandas as pd
import yfinance as yf

def fetch_ohlcv(ticker: str, start: str, end: str, interval: str = "1d") -> pd.DataFrame:
    df = yf.download(ticker, start=start, end=end, interval=interval, auto_adjust=True, progress=False)
    if isinstance(df.columns, pd.MultiIndex):
        # For multi-index columns from multi-ticker download, pick single level
        df.columns = [c[0] if isinstance(c, tuple) else c for c in df.columns]
    df = df.rename(columns={
        "Open":"open", "High":"high", "Low":"low", "Close":"close", "Adj Close":"close", "Volume":"volume"
    })
    return df.dropna()
