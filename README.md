# 美股股價查詢 + 回測平台（VS Code + Python）

這是一個使用 **Streamlit** + **yfinance** 的最小可用（MVP）專案：
- 即時下載美股歷史行情（Yahoo Finance）
- 顯示收盤價／成交量圖
- 內建 **SMA 均線交叉** 回測（可調快/慢均線、手續費）
- 以 **pandas** 實作回測核心（不依賴沉重框架），易於擴充

> 進階：可逐步換成 `vectorbt` 或 `backtrader`。

---

## 快速開始

```bash
# 建議用 Python 3.11+
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

pip install -r requirements.txt

# 啟動
streamlit run app/streamlit_app.py
```

瀏覽器打開 `http://localhost:8501`。

---

## 使用 VS Code

1. 安裝 VS Code 外掛：
   - Python (Microsoft)
   - Pylance
   - Jupyter（選用）
   - **ChatGPT / Codex 擴充**（若你已使用 ChatGPT Plus/Team/Enterprise，可安裝官方 Codex 擴充）
2. 開啟此資料夾，按 `F5` 或使用 **Run and Debug**。

### 使用 Codex（可選）
- 在 VS Code 命令面板輸入：`Codex: Enable in this folder`
- 給它如下指令（Prompt）產生功能：
  - 「新增一個 RSI 指標並加入回測條件（RSI < 30 進場、> 70 出場）」
  - 「把圖表換成 Plotly 並支援多股同圖比較」
  - 「把回測寫成類別 `Strategy`，拆成檔案」

> 若你使用 **Codex CLI**，在終端機 `codex plan` / `codex apply` 讓它對原始碼做變更。

---

## 結構

```
stock_backtest_app/
├─ app/
│  ├─ streamlit_app.py        # UI + 繪圖 + 參數
│  ├─ data.py                 # yfinance 抓取
│  ├─ backtest.py             # SMA 回測核心
│  └─ utils.py                # 共用工具（時區、快取等）
├─ tests/
│  └─ test_backtest.py
├─ .vscode/
│  ├─ launch.json
│  └─ tasks.json
├─ requirements.txt
└─ README.md
```

---

## 已內建的功能

- **下載資料**：指定 `Ticker`（例如 `AAPL`、`NVDA`、`SPY`）、日期區間、頻率。
- **圖表**：收盤價（折線）、成交量（柱狀）、可切換對數刻度。
- **回測**：SMA 快/慢交叉，含：
  - 交易成本（單邊手續費）
  - 部位大小（100% 全倉或固定金額）
  - 成本與滑價簡化估計
- **績效**：總報酬、年化報酬、最大回撤、夏普（簡化）。

---

## 測試

```bash
pytest -q
```

---

## 授權

MIT
