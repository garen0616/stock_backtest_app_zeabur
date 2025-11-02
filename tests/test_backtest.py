import pandas as pd
from app.backtest import sma_crossover_bt

def test_sma_backtest_runs():
    idx = pd.date_range("2022-01-01", periods=300, freq="B")
    close = pd.Series(range(1, 301), index=idx, dtype=float)
    res = sma_crossover_bt(close, 10, 20, 0.0)
    assert "equity_curve" in res and not res["equity_curve"].empty
