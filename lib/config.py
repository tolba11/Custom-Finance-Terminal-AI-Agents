"""Shared configuration and compliance disclosure."""
import os

from dotenv import load_dotenv

load_dotenv()

DISCLOSURE = (
    "This dashboard is for educational and informational purposes only. "
    "It is not financial advice, not a recommendation to buy or sell any "
    "security, and is not personalized to your situation. Consult a licensed "
    "advisor before making investment decisions."
)

APP_NAME = "Stock Market Analyst"


def _sanitize(val):
    """Tolerate common paste mistakes: full URLs, quotes, whitespace."""
    if not val:
        return ""
    val = str(val).strip().strip('"').strip("'")
    if "api_key=" in val:  # someone pasted a whole URL
        val = val.split("api_key=")[1].split("&")[0]
    return val.strip()


def _get_key(name):
    """Env var first (local .env), then Streamlit Cloud secrets."""
    val = os.getenv(name)
    if not val:
        try:
            import streamlit as st
            val = st.secrets.get(name, "")
        except Exception:
            val = ""
    return _sanitize(val)


def get_anthropic_key():
    return _get_key("ANTHROPIC_API_KEY")


def get_fred_key():
    return _get_key("FRED_API_KEY")


def render_footer(st):
    """Render the compliance disclosure footer on a page."""
    st.divider()
    st.caption(DISCLOSURE)


def render_sidebar(st):
    """Shared sidebar branding for every page."""
    st.sidebar.markdown("## 📊 Market Analyst")
    st.sidebar.caption("Personal research • Educational use only")


def apply_base_style(st):
    """Larger base font + dark-mode friendly tweaks."""
    st.markdown(
        """
        <style>
        .main .block-container { font-size: 17px; }
        [data-testid="stMetricValue"] { font-size: 1.6rem; }
        </style>
        """,
        unsafe_allow_html=True,
    )
