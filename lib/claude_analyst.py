"""Anthropic Claude API calls: bull/bear case, deep analysis, macro pulse.
All prompts instruct the model to stay educational — no recommendations."""
import streamlit as st

from lib.config import get_anthropic_key

MODELS = ["claude-sonnet-5", "claude-sonnet-4-5", "claude-haiku-4-5"]

GUARDRAIL = (
    "You are an educational market analyst. Do NOT give buy, sell, or hold "
    "recommendations. Do not use the words 'buy', 'sell', 'recommend', or "
    "'should' as advice. Present balanced, factual analysis only, and note "
    "that this is educational information, not financial advice."
)


def _client():
    key = get_anthropic_key()
    if not key:
        return None
    try:
        import anthropic
        return anthropic.Anthropic(api_key=key)
    except Exception:
        return None


def _ask(prompt: str, max_tokens: int = 1500) -> str:
    client = _client()
    if client is None:
        return ""
    last_err = None
    for model in MODELS:
        try:
            msg = client.messages.create(
                model=model, max_tokens=max_tokens, system=GUARDRAIL,
                messages=[{"role": "user", "content": prompt}],
            )
            return "".join(b.text for b in msg.content if b.type == "text")
        except Exception as e:
            last_err = e
            if "not_found" in str(e) or "404" in str(e):
                continue
            break
    return f"⚠️ AI request failed: {last_err}"


def key_missing() -> bool:
    return not get_anthropic_key()


@st.cache_data(ttl=1800, show_spinner=False, max_entries=24)
def bull_bear_case(ticker: str, facts: str) -> str:
    return _ask(
        f"For {ticker}, write a balanced educational overview with two "
        f"sections: 'Constructive case' (factors observers cite as "
        f"strengths) and 'Cautious case' (risks and headwinds observers "
        f"cite). 4-5 bullets each, grounded in these facts:\n{facts}"
    )


@st.cache_data(ttl=1800, show_spinner=False, max_entries=24)
def deep_analysis(ticker: str, facts: str) -> str:
    return _ask(
        f"Write an educational deep-dive on {ticker} covering: business "
        f"model, competitive position, financial health, valuation context, "
        f"and key risks. Use these facts:\n{facts}", max_tokens=2000,
    )


@st.cache_data(ttl=1800, show_spinner=False, max_entries=24)
def macro_pulse(facts: str) -> str:
    return _ask(
        "Write an educational macro pulse-check: what the following US "
        "indicators suggest about growth, inflation, and policy, and what "
        f"historically similar setups looked like:\n{facts}"
    )


@st.cache_data(ttl=1800, show_spinner=False, max_entries=24)
def portfolio_analysis(facts: str) -> str:
    return _ask(
        "Review this personal portfolio from an educational lens: "
        "diversification, sector tilts, volatility profile, and factors the "
        "holder may want to research further. No recommendations.\n"
        f"{facts}", max_tokens=2000,
    )
