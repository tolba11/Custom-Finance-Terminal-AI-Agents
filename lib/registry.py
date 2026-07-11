"""Single source of truth for the Terminal's tabs.

Add a new view here ONCE and it appears in both the sidebar navigation
(app.py) and the Home page FUNCTIONS grid automatically."""

# (file, title, description)
PAGES = [
    ("views/home.py", "Home", "Market snapshot and function directory"),
    ("views/deep_finance.py", "Deep Finance",
     "Multi-model AI chat — Fable 5, Opus 4.8, Sonnet 5, Perplexity"),
    ("views/market_pulse.py", "Market Pulse",
     "Indices, sectors, movers, headlines"),
    ("views/stock_analyzer.py", "Stock Analyzer",
     "Charts, factor scores, statistics, AI"),
    ("views/equity_research.py", "Equity Research",
     "Nine-agent analyst desk with final verdict"),
    ("views/fundamentals.py", "Financial Statements",
     "Statements, SEC filings, earnings transcripts"),
    ("views/etf_analyzer.py", "ETF Analyzer",
     "Returns, risk, holdings, cost peers"),
    ("views/macro.py", "Macro",
     "FRED indicators, yield curve, commodities"),
    ("views/portfolio_view.py", "Portfolio",
     "Holdings, allocation, risk"),
    ("views/news_view.py", "News",
     "Market and per-ticker headlines"),
    ("views/events.py", "Events & Insiders",
     "Earnings, IPOs, ratings, insiders"),
    ("views/pevc.py", "PE/VC",
     "Deal flow, TradedVC archive, The VC Corner"),
    ("views/technology.py", "Technology",
     "TechCrunch across seven sections"),
    ("views/compound_ai.py", "Compound AI",
     "Third-party AI analyst for finance"),
    ("views/perceptis_ai.py", "Perceptis AI",
     "Third-party executive presentation AI"),
    ("views/pretus_ai.py", "Pretus AI",
     "Third-party IB interview prep"),
]


def url_path(file: str) -> str:
    """Streamlit derives the URL from the view filename."""
    return "/" + file.rsplit("/", 1)[-1].removesuffix(".py")
