# Pyramid Terminal

A Bloomberg-style personal finance terminal built with Streamlit.
Live at **https://tolbaterminal.streamlit.app**

## Functions

| View | Contents |
|---|---|
| Home | Market snapshot board + function directory (auto-synced to all views) |
| Deep Finance | Multi-model AI chat: Claude Fable 5 / Opus 4.8 / Sonnet 5, Perplexity Sonar & Sonar Pro, web grounding, any-file attachments |
| Market Pulse | U.S. / Europe / APAC region boards, benchmark chart, Commodities · FX · Rates strip, sector heatmap, movers, headlines |
| Stock Analyzer | Global equity search (U.S./EU/APAC), 4 chart views with period bar, factor gauges, key statistics, AI analysis, news sentiment |
| Equity Research | 9-agent research pipeline (analysts, bull/bear debate, trader, risk desk) ending in a BUY/HOLD/SELL verdict |
| Financial Statements | Income statement / balance sheet / cash flow, SEC 10-K filings, earnings-call transcripts with speaker view |
| ETF Analyzer | Returns, risk profile, sector breakdown, top holdings, peer cost comparison |
| Macro | FRED indicators, yield curve, Commodities · FX · Rates strip, AI pulse-check |
| Portfolio | PA-engine-style analytics: performance vs SPY, Brinson attribution, contribution to return, exposures, MCTR risk decomposition, VaR, AI review |
| News | Market and per-ticker headlines |
| Events & Insiders | Earnings calendar, IPOs, analyst rating trends, insider transactions |
| PE/VC | PE deal headlines, VC Traded archive, VC Corner archive |
| Technology | TechCrunch: Latest, Startups, Venture, Apple, Security, AI, Apps |
| Compound AI / Perceptis AI / Pretus AI | Third-party platform launch panels |

## Data sources

Yahoo Finance (prices, fundamentals, fund data — keyless), FRED (macro),
Finnhub (events, insiders, symbol fallback), Alpha Vantage (earnings,
transcripts, news sentiment), SEC EDGAR (filings — keyless), Anthropic
Claude (analysis, agents, chat), Perplexity (chat + web grounding),
TechCrunch / Google News / beehiiv / Substack (headlines & archives).

## Configuration

Keys live in Streamlit Cloud Secrets (or a local `.env`):

```toml
ANTHROPIC_API_KEY = "..."
FRED_API_KEY = "..."
FINNHUB_API_KEY = "..."
ALPHA_VANTAGE_API_KEY = "..."
PERPLEXITY_API_KEY = "..."
```

The app runs without keys; affected views show a setup note.

## Run locally

```bash
pip install -r requirements.txt
streamlit run app.py
```


## Build your own Pyramid Terminal

Everything below is free-tier. Total setup time is roughly 30 minutes.

### 1. Fork and clone

Fork this repo on GitHub, then:

```bash
git clone https://github.com/<your-username>/<your-fork>.git
cd <your-fork>
pip install -r requirements.txt
```

### 2. Get your API keys (all free)

| Key | Where | Notes |
|---|---|---|
| `ANTHROPIC_API_KEY` | console.anthropic.com → API Keys | Powers AI analysis, the 9-agent Equity Research pipeline, and Deep Finance chat. Pay-as-you-go. |
| `FRED_API_KEY` | fred.stlouisfed.org/docs/api/api_key.html | Macro indicators and yield curve. Instant, free. |
| `FINNHUB_API_KEY` | finnhub.io/register | Earnings calendar, IPOs, insider transactions. Free tier. |
| `ALPHA_VANTAGE_API_KEY` | alphavantage.co/support/#api-key | Earnings transcripts, news sentiment. Free tier is ~25 requests/day — the app caches aggressively around this. |
| `PERPLEXITY_API_KEY` | perplexity.ai → Settings → API | Sonar models + web grounding in Deep Finance. |

Yahoo Finance and SEC EDGAR need no keys. The app runs with any subset
of keys — views missing a key show a setup note instead of crashing.

### 3. Run locally

```bash
cp .env.example .env   # paste your keys into .env
streamlit run app.py
```

### 4. Deploy free on Streamlit Community Cloud

1. Push your fork to GitHub.
2. Go to **share.streamlit.io** → New app → pick your fork, branch
   `main`, main file `app.py`.
3. In the app's **Settings → Secrets**, paste your keys in TOML form:

```toml
ANTHROPIC_API_KEY = "sk-ant-..."
FRED_API_KEY = "..."
FINNHUB_API_KEY = "..."
ALPHA_VANTAGE_API_KEY = "..."
PERPLEXITY_API_KEY = "..."
```

4. Deploy. The app auto-updates on every push to your fork.

### 5. Make it yours

- Rename the brand: edit `render_sidebar` in `lib/config.py`.
- Add a view: create `views/my_view.py`, register it in
  `lib/registry.py` — navigation and the Home function grid update
  automatically.
- Change the accent color: search-and-replace `#f97316` in
  `lib/config.py` and `.streamlit/config.toml`.

## Architecture

- `app.py` — `st.navigation` router, 15-minute auto-refresh (paused on
  long-running AI views), global crash guard with Retry.
- `lib/registry.py` — single source of truth for navigation and the Home
  function grid; adding a view updates both automatically.
- `lib/pa_engine.py` — portfolio analytics engine; component structure
  recycled from FactSet's open-source enterprise-sdk (PA Engine v3),
  reimplemented over free data.
- `lib/market_data.py` — cached yfinance layer; live-quote splicing keeps
  charts current intraday with DATA THROUGH stamps.
- All `st.cache_data` uses are TTL- and entry-capped for Streamlit
  Community Cloud's 1 GB container; bulk downloads run single-threaded.
- Quota-aware Alpha Vantage layer with throttle detection and long caches.
