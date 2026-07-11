"""Multi-agent equity research engine, modeled on the open-source
TradingAgents framework (TauricResearch): analyst team -> bull/bear debate
-> research evaluation -> trader -> risk debate -> portfolio manager.

The LLM callable is injectable for testing. All market inputs come from the
Terminal's existing data layer (Yahoo, Finnhub, news).
"""
import re
import time

from lib.config import get_anthropic_key
from lib import finnhub_data as fh
from lib.market_data import get_history, get_quote, get_stock_fundamentals
from lib.news import ticker_news
from lib.signals import technical_score

MODEL_SETS = {
    "Standard": ["claude-haiku-4-5", "claude-opus-4-8", "claude-sonnet-5"],
    "Opus 4.8": ["claude-opus-4-8", "claude-opus-4-5", "claude-sonnet-5",
                 "claude-haiku-4-5"],
}

DEPTH_ROUNDS = {"Shallow": 0, "Medium": 1, "Deep": 2}

STAGES = [
    ("market", "Market Analyst", "Analyst Agents"),
    ("social", "Sentiment & Flow Analyst", "Analyst Agents"),
    ("news", "News Analyst", "Analyst Agents"),
    ("fundamentals", "Fundamentals Analyst", "Analyst Agents"),
    ("debate", "Bull/Bear Advocates", "Research Agents"),
    ("evaluator", "Research Evaluator", "Research Agents"),
    ("trader", "Trader", "Trading Desk"),
    ("risk", "Risk Analysts", "Risk Management"),
    ("verdict", "Portfolio Manager", "Final Verdict"),
]

SYSTEM = (
    "You are one specialist on a multi-agent equity research desk. Write in "
    "tight, professional sell-side prose with concrete numbers from the "
    "data provided. Never invent figures. Markdown, no top-level heading.")


def _default_llm(models, prompt, max_tokens=900):
    import anthropic
    client = anthropic.Anthropic(api_key=get_anthropic_key())
    last = None
    for m in models:
        try:
            r = client.messages.create(model=m, max_tokens=max_tokens,
                                       system=SYSTEM,
                                       messages=[{"role": "user",
                                                  "content": prompt}])
            return "".join(b.text for b in r.content if b.type == "text")
        except Exception as e:
            last = e
            if "not_found" in str(e) or "404" in str(e):
                continue
            raise
    raise RuntimeError(str(last))


# ---------- data briefs (no LLM) ----------

def _market_brief(ticker):
    df = get_history(ticker, "1Y")
    q = get_quote(ticker)
    tech = technical_score(df)
    lines = [f"Ticker {ticker}. Last price {q.get('price')}, prev close "
             f"{q.get('prev_close')}, day change {q.get('change_pct'):.2f}%"
             if q.get("change_pct") is not None else f"Ticker {ticker}."]
    if df is not None and not df.empty:
        c = df["Close"]
        for w in (20, 50, 200):
            if len(c) >= w:
                lines.append(f"SMA{w}: {c.rolling(w).mean().iloc[-1]:.2f}")
        lines.append(f"1Y return: {(c.iloc[-1]/c.iloc[0]-1)*100:.1f}%")
        lines.append(f"52w high {c.max():.2f}, low {c.min():.2f}")
        if "Volume" in df:
            v = df["Volume"]
            lines.append(f"20d avg volume {v.tail(20).mean():,.0f} vs "
                         f"1Y avg {v.mean():,.0f}")
    lines += [f"Technical score {tech['score']}/100"] + tech["drivers"]
    return "\n".join(lines)


def _fundamentals_brief(ticker):
    info = get_stock_fundamentals(ticker)
    keys = ["longName", "sector", "industry", "marketCap", "trailingPE",
            "forwardPE", "priceToBook", "profitMargins", "operatingMargins",
            "returnOnEquity", "returnOnAssets", "debtToEquity",
            "currentRatio", "totalCash", "totalDebt", "totalRevenue",
            "revenueGrowth", "earningsGrowth", "trailingEps", "beta",
            "dividendYield", "targetMeanPrice", "targetHighPrice",
            "targetLowPrice", "numberOfAnalystOpinions"]
    lines = [f"{k}: {info[k]}" for k in keys if info.get(k) is not None]
    return "\n".join(lines) or "No fundamental data available."


def _news_brief(ticker):
    items = ticker_news(ticker, limit=8)
    if not items:
        return "No recent headlines."
    return "\n".join(f"- {i['title']} ({i['publisher']})"
                     + (f": {i['summary'][:150]}" if i["summary"] else "")
                     for i in items)


def _flow_brief(ticker):
    lines = []
    recs = fh.recommendation_trends(ticker)
    if recs:
        r = recs[0]
        lines.append(f"Latest analyst rating counts ({r.get('period')}): "
                     f"strongBuy {r.get('strongBuy')}, buy {r.get('buy')}, "
                     f"hold {r.get('hold')}, sell {r.get('sell')}, "
                     f"strongSell {r.get('strongSell')}")
        if len(recs) > 3:
            p = recs[3]
            lines.append(f"Three months prior ({p.get('period')}): "
                         f"strongBuy {p.get('strongBuy')}, buy {p.get('buy')},"
                         f" hold {p.get('hold')}, sell {p.get('sell')}")
    ins = fh.insider_transactions(ticker, limit=12)
    if ins:
        buys = sum(1 for t in ins if (t.get("change") or 0) > 0)
        sells = sum(1 for t in ins if (t.get("change") or 0) < 0)
        lines.append(f"Recent insider filings: {buys} acquisitions, "
                     f"{sells} dispositions across last {len(ins)} records")
        for t in ins[:4]:
            lines.append(f"- {t.get('name')}: change {t.get('change')} "
                         f"on {t.get('transactionDate')}")
    return "\n".join(lines) or "No analyst-trend or insider data available."


# ---------- pipeline ----------

def run_pipeline(ticker, depth="Shallow", mode="Standard",
                 llm=None, on_stage=None):
    """Run the full desk. Returns dict with 'reports', 'verdict', 'duration'.
    on_stage(key, status) is called with 'running'/'done' per stage."""
    llm = llm or (lambda p, mt=900: _default_llm(MODEL_SETS[mode], p, mt))
    rounds = DEPTH_ROUNDS.get(depth, 0)
    t0 = time.time()
    reports = {}

    def stage(key, fn):
        if on_stage:
            on_stage(key, "running")
        reports[key] = fn()
        if on_stage:
            on_stage(key, "done")
        return reports[key]

    mkt_data = _market_brief(ticker)
    fund_data = _fundamentals_brief(ticker)
    news_data = _news_brief(ticker)
    flow_data = _flow_brief(ticker)

    stage("market", lambda: llm(
        f"As the Market (technical) Analyst, assess {ticker}'s price "
        f"structure: trend vs moving averages, momentum, volume character, "
        f"key support/resistance levels, and what the tape implies near "
        f"term. Data:\n{mkt_data}"))

    stage("social", lambda: llm(
        f"As the Sentiment & Flow Analyst for {ticker}, read positioning "
        f"from analyst-rating migration and insider transaction patterns. "
        f"What are informed participants doing?\nData:\n{flow_data}"))

    stage("news", lambda: llm(
        f"As the News Analyst for {ticker}, extract the catalysts, risks, "
        f"and narrative direction from these headlines. Flag anything with "
        f"earnings, legal, regulatory, or guidance implications.\n"
        f"{news_data}"))

    stage("fundamentals", lambda: llm(
        f"As the Fundamentals Analyst for {ticker}, assess valuation vs "
        f"quality: growth, margins, returns on capital, balance sheet, and "
        f"how the multiple compares to the growth delivered. State what the "
        f"market appears to be pricing in.\nData:\n{fund_data}"))

    def _debate():
        ctx = (f"MARKET: {reports['market']}\n\nFLOW: {reports['social']}"
               f"\n\nNEWS: {reports['news']}\n\nFUNDAMENTALS: "
               f"{reports['fundamentals']}")
        bull = llm(f"As the Bull Advocate for {ticker}, build the strongest "
                   f"affirmative case from the desk's research. Be concrete "
                   f"and cite the numbers.\n{ctx}")
        bear = llm(f"As the Bear Advocate for {ticker}, build the strongest "
                   f"negative case from the desk's research. Attack the "
                   f"weakest bull assumptions.\n{ctx}\n\nBULL CASE:\n{bull}")
        transcript = f"### Bull opening\n{bull}\n\n### Bear opening\n{bear}"
        for i in range(rounds):
            reb_b = llm(f"As the Bull Advocate, rebut the bear's latest "
                        f"arguments on {ticker} in under 200 words.\n"
                        f"{transcript}", 400)
            reb_r = llm(f"As the Bear Advocate, rebut the bull's latest "
                        f"arguments on {ticker} in under 200 words.\n"
                        f"{transcript}\n\n### Bull rebuttal {i+1}\n{reb_b}",
                        400)
            transcript += (f"\n\n### Bull rebuttal {i+1}\n{reb_b}"
                           f"\n\n### Bear rebuttal {i+1}\n{reb_r}")
        return transcript

    stage("debate", _debate)

    stage("evaluator", lambda: llm(
        f"As the Research Evaluator for {ticker}, judge the debate: which "
        f"arguments were strongest, which were weakest or speculative, and "
        f"where the evidence actually points. End with the balance of "
        f"evidence.\n{reports['debate']}"))

    stage("trader", lambda: llm(
        f"As the Trader for {ticker}, translate the evaluated research into "
        f"a draft trade plan: direction, sizing approach, entry logic, "
        f"invalidation level, and what confirms or breaks the thesis. Use "
        f"actual price levels from the market work.\nMARKET:\n"
        f"{reports['market']}\n\nEVALUATION:\n{reports['evaluator']}"))

    stage("risk", lambda: llm(
        f"As the Risk desk for {ticker}, produce three labeled sections — "
        f"Risky Analyst (aggressive case for the plan), Safe Analyst "
        f"(conservative objections), Neutral Analyst (pragmatic middle) — "
        f"each reacting to the trader's plan.\nPLAN:\n{reports['trader']}",
        1200))

    def _verdict():
        out = llm(
            f"As the Portfolio Manager and debate facilitator for {ticker}, "
            f"issue the final call. First line exactly 'VERDICT: BUY' or "
            f"'VERDICT: HOLD' or 'VERDICT: SELL'. Then: 1. Summary of key "
            f"arguments (per analyst), 2. Rationale for the decision, "
            f"3. Refined plan with concrete levels and staging, 4. What "
            f"would change your mind. Draw on every desk report.\n"
            f"EVALUATION:\n{reports['evaluator']}\n\nTRADER PLAN:\n"
            f"{reports['trader']}\n\nRISK DESK:\n{reports['risk']}", 1400)
        return out

    stage("verdict", _verdict)

    m = re.search(r"VERDICT:\s*(BUY|HOLD|SELL)", reports["verdict"],
                  re.IGNORECASE)
    verdict = m.group(1).upper() if m else "HOLD"
    body = re.sub(r"^.*?VERDICT:\s*(BUY|HOLD|SELL)\s*\n?", "",
                  reports["verdict"], count=1, flags=re.IGNORECASE | re.DOTALL
                  ) if m and reports["verdict"].strip().upper().startswith(
                  "VERDICT") else reports["verdict"]
    reports["verdict_body"] = body

    return {"reports": reports, "verdict": verdict,
            "duration": time.time() - t0, "ticker": ticker,
            "depth": depth, "mode": mode}
