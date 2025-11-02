from __future__ import annotations
import pandas as pd
import numpy as np
import pytz
from datetime import datetime

TW_TZ = pytz.timezone("Asia/Taipei")

def to_local_time(dt: pd.Timestamp | None) -> pd.Timestamp | None:
    if dt is None: 
        return None
    if dt.tzinfo is None:
        return TW_TZ.localize(dt)
    return dt.astimezone(TW_TZ)

def annualized_return(series: pd.Series, freq: str = "D") -> float:
    if series.empty:
        return 0.0
    ret = series.iloc[-1] / series.iloc[0] - 1.0
    n = (series.index[-1] - series.index[0]).days / (365 if freq.upper().startswith("D") else 1)
    if n <= 0:
        return float("nan")
    return (1 + ret) ** (1 / n) - 1

def max_drawdown(equity_curve: pd.Series) -> float:
    if equity_curve.empty:
        return 0.0
    roll_max = equity_curve.cummax()
    dd = equity_curve / roll_max - 1.0
    return float(dd.min())

def sharpe_ratio(returns: pd.Series, rf: float = 0.0, periods_per_year: int = 252) -> float:
    if returns.std() == 0 or returns.empty:
        return 0.0
    excess = returns - rf / periods_per_year
    return np.sqrt(periods_per_year) * excess.mean() / excess.std()
