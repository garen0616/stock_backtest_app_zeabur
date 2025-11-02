import streamlit as st
import pandas as pd
from datetime import date, timedelta
from data import fetch_ohlcv
from backtest import sma_crossover_bt

st.set_page_config(page_title="美股查價與回測", layout="wide")

st.title("📈 美股股價查詢 & SMA 回測 (Streamlit)")

col1, col2, col3 = st.columns([2,1,1])
with col1:
    ticker = st.text_input("Ticker（如 AAPL, NVDA, SPY）", value="NVDA").strip().upper()
with col2:
    start = st.date_input("開始日期", value=date.today() - timedelta(days=365*3))
with col3:
    end = st.date_input("結束日期", value=date.today())

interval = st.selectbox("頻率", ["1d", "1h", "1wk", "1mo"], index=0)
log_scale = st.checkbox("對數刻度", value=False)

with st.spinner("下載資料中…"):
    df = fetch_ohlcv(ticker, str(start), str(end + timedelta(days=1)), interval=interval)

if df.empty:
    st.warning("查無資料，請換一個 Ticker 或調整日期區間。")
    st.stop()

st.subheader(f"{ticker} 價格走勢")
price_col, vol_col = st.columns([3,1])
with price_col:
    chart_df = df[["close"]].copy()
    chart_df.columns = [f"{ticker} Close"]
    st.line_chart(chart_df, height=360, use_container_width=True)
with vol_col:
    st.bar_chart(df[["volume"]].rename(columns={"volume":"Volume"}), height=360, use_container_width=True)

st.divider()
st.subheader("SMA 均線交叉回測")
fast = st.number_input("快均線 (日)", min_value=2, max_value=250, value=10)
slow = st.number_input("慢均線 (日)", min_value=3, max_value=400, value=20)
fee = st.number_input("單邊交易成本 (費率)", min_value=0.0, max_value=0.01, step=0.0005, value=0.0005, format="%.4f")

if fast >= slow:
    st.error("快均線必須小於慢均線")
else:
    bt = sma_crossover_bt(df["close"], fast=fast, slow=slow, fee=fee)
    met1, met2, met3, met4 = st.columns(4)
    stats = bt["stats"]
    met1.metric("總報酬", f"{stats['total_return']*100:,.2f}%")
    met2.metric("年化報酬(估)", f"{stats['annual_return_est']*100:,.2f}%")
    met3.metric("最大回撤", f"{stats['max_drawdown']*100:,.2f}%")
    met4.metric("夏普(估)", f"{stats['sharpe_est']:.2f}")
    st.line_chart(bt["equity_curve"].rename("Equity"), height=320, use_container_width=True)

    with st.expander("顯示技術線與訊號"):
        tech = pd.concat([df["close"].rename("close"), bt["fast_ma"].rename(f"SMA{fast}"), bt["slow_ma"].rename(f"SMA{slow}")], axis=1).dropna()
        st.line_chart(tech, height=320, use_container_width=True)
        st.dataframe(tech.tail(20))

st.caption("資料來源：Yahoo Finance（經 yfinance 取得）")
