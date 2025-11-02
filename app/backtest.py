from __future__ import annotations
import pandas as pd
import numpy as np

def sma_crossover_bt(close: pd.Series, fast: int = 10, slow: int = 20, fee: float = 0.0005):
    close = close.dropna().astype(float)
    fast_ma = close.rolling(fast).mean()
    slow_ma = close.rolling(slow).mean()

    # Signals: 1 long / 0 flat
    long_signal = (fast_ma > slow_ma).astype(int)

    # Positions (enter/exit when signal changes)
    pos = long_signal.shift(1).fillna(0)
    # Trade when pos changes
    trade = pos.diff().fillna(pos)  # 1 buy, -1 sell on first valid step may be 0->1 or 1->0
    # Daily returns
    ret = close.pct_change().fillna(0.0)
    strat_ret = pos * ret

    # Apply fees on trades (assume charged on notional when switching)
    strat_ret = strat_ret - fee * trade.abs()

    equity = (1 + strat_ret).cumprod()
    stats = {
        "trades": int(trade.abs().sum()),
        "total_return": float(equity.iloc[-1] - 1.0) if not equity.empty else 0.0,
        "annual_return_est": float((equity.iloc[-1]) ** (252 / len(equity)) - 1.0) if len(equity) > 0 else 0.0,
        "max_drawdown": float((equity / equity.cummax() - 1.0).min()) if not equity.empty else 0.0,
        "sharpe_est": float(np.sqrt(252) * strat_ret.mean() / (strat_ret.std() + 1e-12)) if not strat_ret.empty else 0.0
    }
    return {
        "equity_curve": equity,
        "strat_returns": strat_ret,
        "signals": long_signal,
        "fast_ma": fast_ma,
        "slow_ma": slow_ma,
        "stats": stats
    }
