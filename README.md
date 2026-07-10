# 📊 Stock Market Analyst

Personal stock market dashboard built with Streamlit. **Educational and
personal-research use only — no buy/sell recommendations.**

## Setup

```bash
python -m venv .venv
.venv\Scripts\activate        # Windows  (macOS/Linux: source .venv/bin/activate)
pip install -r requirements.txt
copy .env.example .env        # then paste your keys into .env
python scripts/fetch_logos.py # optional: download company logos
streamlit run app.py
```

## API keys (optional but recommended)

| Key | Used for | Get it |
|---|---|---|
| `ANTHROPIC_API_KEY` | AI analysis tabs, macro pulse-check, portfolio review | console.anthropic.com |
| `FRED_API_KEY` | Macro page (free) | fred.stlouisfed.org/docs/api |

Without keys the app still runs — prices, charts, ETF analysis, portfolio
tracking, and news all work via yfinance. The AI and Macro features show a
friendly setup note instead.

## Pages

1. **Market Pulse** — indices grid with sparklines, S&P 500 chart, sector
   heatmap, gainers/losers/most-active, top headlines
2. **Stock Analyzer** — chart, descriptive snapshot gauges, key statistics,
   AI analysis
3. **ETF Analyzer** — returns, risk gauge, sector breakdown, top holdings,
   peer cost comparison
4. **Macro** — FRED indicators, yield curve, AI pulse-check
5. **Portfolio** — holdings tracker (stored locally, gitignored), allocation,
   risk score, AI review
6. **News** — market and per-ticker headlines

## Disclosure

This dashboard is for educational and informational purposes only. It is not
financial advice, not a recommendation to buy or sell any security, and is
not personalized to your situation. Consult a licensed advisor before making
investment decisions.
