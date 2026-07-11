"""Shared configuration, branding, and terminal styling."""
import os

from dotenv import load_dotenv

load_dotenv()

APP_NAME = "Tolba Terminal"


def _sanitize(val):
    """Tolerate common paste mistakes: full URLs, quotes, whitespace."""
    if not val:
        return ""
    val = str(val).strip().strip('"').strip("'")
    if "api_key=" in val:
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


def get_finnhub_key():
    return _get_key("FINNHUB_API_KEY")


def render_footer(st):
    """Thin terminal footer."""
    st.markdown(
        '<div class="tt-footer">TOLBA TERMINAL — market data may be '
        'delayed</div>', unsafe_allow_html=True)


def render_sidebar(st):
    """Terminal brand block in the sidebar."""
    st.sidebar.markdown(
        '<div class="tt-brand"><span class="tt-brand-mark"></span>'
        'TOLBA<br>TERMINAL</div>',
        unsafe_allow_html=True)


def apply_base_style(st):
    """Bloomberg-inspired light terminal styling."""
    st.markdown(
        """
        <style>
        @import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;500;600;700&display=swap');
        html, body, [class*="css"], .main .block-container {
            font-family: 'Segoe UI', 'Liberation Sans', 'DejaVu Sans', Arial, sans-serif;
            font-size: 15px;
            color: #18181b;
        }
        .main .block-container { padding-top: 1.2rem; max-width: 1500px; }

        /* headings: compact, uppercase, tracked */
        h1 {
            font-family: 'IBM Plex Mono', 'Consolas', 'Liberation Mono', 'DejaVu Sans Mono', monospace !important;
            text-transform: uppercase;
            letter-spacing: 0.06em;
            font-size: 1.55rem !important;
            border-bottom: 3px solid #c2410c;
            padding-bottom: 0.35rem;
        }
        h2, h3 {
            font-family: 'IBM Plex Mono', 'Consolas', 'Liberation Mono', 'DejaVu Sans Mono', monospace !important;
            text-transform: uppercase;
            letter-spacing: 0.05em;
            font-size: 1.02rem !important;
            color: #3f3f46;
        }

        /* metrics: mono numerals, dense */
        [data-testid="stMetricValue"] {
            font-family: 'IBM Plex Mono', 'Consolas', 'Liberation Mono', 'DejaVu Sans Mono', monospace;
            font-size: 1.45rem;
            font-weight: 600;
        }
        [data-testid="stMetricLabel"] {
            font-family: 'IBM Plex Mono', 'Consolas', 'Liberation Mono', 'DejaVu Sans Mono', monospace;
            font-size: 0.72rem;
            letter-spacing: 0.08em;
            color: #71717a;
        }
        [data-testid="stMetric"] {
            background: #ffffff;
            border: 1px solid #e4e4e7;
            border-left: 3px solid #c2410c;
            padding: 0.45rem 0.7rem;
        }

        /* tables + dataframes: dense terminal grid */
        [data-testid="stDataFrame"] { border: 1px solid #e4e4e7; }
        [data-testid="stDataFrame"] * {
            font-family: 'IBM Plex Mono', 'Consolas', 'Liberation Mono', 'DejaVu Sans Mono', monospace !important;
            font-size: 12.5px !important;
        }

        /* sidebar: flat, bordered */
        [data-testid="stSidebar"] {
            background: #f7f7f5;
            border-right: 1px solid #e4e4e7;
        }
        [data-testid="stSidebarNav"] a span,
        [data-testid="stSidebarNav"] span {
            font-family: 'IBM Plex Mono', 'Consolas', 'Liberation Mono', 'DejaVu Sans Mono', monospace !important;
            text-transform: uppercase;
            letter-spacing: 0.05em;
            font-size: 0.8rem !important;
        }

        .tt-brand {
            font-family: 'IBM Plex Mono', 'Consolas', 'Liberation Mono', 'DejaVu Sans Mono', monospace;
            font-weight: 700;
            font-size: 1.05rem;
            letter-spacing: 0.12em;
            line-height: 1.35;
            color: #18181b;
            padding: 0.4rem 0 0.8rem 0;
            border-bottom: 2px solid #c2410c;
            margin-bottom: 0.6rem;
        }
        .tt-brand-mark {
            display: inline-block; width: 11px; height: 11px;
            background: #c2410c; margin-right: 8px;
        }
        .tt-subtitle {
            font-family: 'IBM Plex Mono', 'Consolas', 'Liberation Mono', 'DejaVu Sans Mono', monospace;
            font-size: 0.75rem; letter-spacing: 0.14em;
            color: #71717a; margin: 0.2rem 0 0.8rem 0;
        }
        .tt-footer {
            font-family: 'IBM Plex Mono', 'Consolas', 'Liberation Mono', 'DejaVu Sans Mono', monospace;
            font-size: 0.68rem; letter-spacing: 0.1em; color: #a1a1aa;
            border-top: 1px solid #e4e4e7;
            padding-top: 0.5rem; margin-top: 2rem;
        }
        .tt-func {
            border: 1px solid #e4e4e7; border-left: 3px solid #c2410c;
            padding: 0.7rem 0.9rem; margin-bottom: 0.6rem; background: #fff;
        }
        .tt-func-name {
            font-family: 'IBM Plex Mono', 'Consolas', 'Liberation Mono', 'DejaVu Sans Mono', monospace; font-weight: 600;
            text-transform: uppercase; letter-spacing: 0.06em;
            font-size: 0.85rem;
        }
        .tt-func-desc { color: #71717a; font-size: 0.82rem; }

        /* segmented controls / buttons: square terminal chips */
        button[kind] { border-radius: 2px !important; }
        [data-testid="stSegmentedControl"] button {
            font-family: 'IBM Plex Mono', 'Consolas', 'Liberation Mono', 'DejaVu Sans Mono', monospace !important;
            font-size: 0.78rem !important; border-radius: 2px !important;
        }
        div[data-testid="stExpander"] summary p {
            font-family: 'IBM Plex Mono', 'Consolas', 'Liberation Mono', 'DejaVu Sans Mono', monospace;
            text-transform: uppercase; font-size: 0.8rem;
            letter-spacing: 0.05em;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def get_alpha_vantage_key():
    return _get_key("ALPHA_VANTAGE_API_KEY")


def get_perplexity_key():
    return _get_key("PERPLEXITY_API_KEY")


def get_perplexity_search_key():
    return _get_key("PERPLEXITY_SEARCH_API_KEY") or _get_key(
        "PERPLEXITY_API_KEY")
