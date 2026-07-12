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
        
        /* ===== control chrome: terminal-grade ===== */
        /* tabs: flat list, orange active underline */
        div[data-baseweb="tab-list"] {
            gap: 0; border-bottom: 2px solid #e4e4e7;
            background: transparent;
        }
        button[data-baseweb="tab"] {
            font-family: 'IBM Plex Mono', 'Consolas', 'Liberation Mono', 'DejaVu Sans Mono', monospace !important;
            text-transform: uppercase; letter-spacing: 0.07em;
            font-size: 0.78rem !important; font-weight: 600;
            color: #71717a; background: transparent !important;
            border-radius: 0 !important; padding: 0.55rem 1.1rem;
            margin-bottom: -2px; border-bottom: 3px solid transparent;
        }
        button[data-baseweb="tab"]:hover { color: #18181b; background: #f7f7f5 !important; }
        button[data-baseweb="tab"][aria-selected="true"] {
            color: #c2410c !important; border-bottom: 3px solid #c2410c;
        }
        div[data-baseweb="tab-highlight"], div[data-baseweb="tab-border"] { display: none; }
        button[data-baseweb="tab"] p { font-size: 0.78rem !important; font-weight: 600; }

        /* buttons: square, mono, orange hover fill */
        .stButton > button, .stDownloadButton > button,
        [data-testid^="stBaseButton-secondary"], [data-testid^="stBaseButton-primary"] {
            font-family: 'IBM Plex Mono', 'Consolas', 'Liberation Mono', 'DejaVu Sans Mono', monospace !important;
            text-transform: uppercase; letter-spacing: 0.08em;
            font-size: 0.75rem !important; font-weight: 600;
            border-radius: 0 !important; border: 1px solid #18181b !important;
            color: #18181b; background: #ffffff;
            padding: 0.35rem 1.1rem; transition: all .12s ease;
        }
        .stButton > button:hover, .stDownloadButton > button:hover {
            background: #c2410c !important; border-color: #c2410c !important;
            color: #ffffff !important;
        }
        .stButton > button:focus:not(:active) { border-color: #c2410c !important; color: #c2410c; }

        /* segmented control: joined square group, orange active */
        [data-testid="stSegmentedControl"] button,
        [data-testid="stButtonGroup"] button {
            font-family: 'IBM Plex Mono', 'Consolas', 'Liberation Mono', 'DejaVu Sans Mono', monospace !important;
            font-size: 0.74rem !important; font-weight: 600;
            letter-spacing: 0.05em; border-radius: 0 !important;
            border: 1px solid #d4d4d8 !important; margin-left: -1px;
            color: #52525b; background: #ffffff; padding: 0.25rem 0.8rem;
        }
        [data-testid="stSegmentedControl"] button:hover,
        [data-testid="stButtonGroup"] button:hover { background: #f7f7f5; color: #18181b; }
        [data-testid="stSegmentedControl"] button[aria-checked="true"],
        [data-testid="stSegmentedControl"] button[kind="segmented_controlActive"],
        [data-testid="stButtonGroup"] button[aria-checked="true"],
        [data-testid^="stBaseButton-segmented_controlActive"] {
            background: #18181b !important; color: #ffffff !important;
            border-color: #18181b !important;
        }

        /* inputs + selects: square, mono, orange focus */
        [data-baseweb="input"], [data-baseweb="base-input"],
        [data-baseweb="select"] > div, .stTextInput input, .stNumberInput input {
            border-radius: 0 !important;
            font-family: 'IBM Plex Mono', 'Consolas', 'Liberation Mono', 'DejaVu Sans Mono', monospace !important;
            font-size: 0.85rem !important;
        }
        [data-baseweb="input"]:focus-within, [data-baseweb="select"] > div:focus-within {
            border-color: #c2410c !important; box-shadow: none !important;
        }
        [data-baseweb="popover"] li {
            font-family: 'IBM Plex Mono', 'Consolas', 'Liberation Mono', 'DejaVu Sans Mono', monospace !important;
            font-size: 0.82rem !important;
        }
        .stTextInput label, .stSelectbox label, .stNumberInput label,
        [data-testid="stWidgetLabel"] p {
            font-family: 'IBM Plex Mono', 'Consolas', 'Liberation Mono', 'DejaVu Sans Mono', monospace !important;
            text-transform: uppercase; letter-spacing: 0.07em;
            font-size: 0.68rem !important; color: #71717a !important;
        }

        /* expanders: bordered square panels, mono header */
        [data-testid="stExpander"] {
            border: 1px solid #e4e4e7 !important; border-radius: 0 !important;
            background: #ffffff;
        }
        [data-testid="stExpander"] summary {
            font-family: 'IBM Plex Mono', 'Consolas', 'Liberation Mono', 'DejaVu Sans Mono', monospace !important;
            text-transform: uppercase; letter-spacing: 0.07em;
            font-size: 0.75rem !important; font-weight: 600;
        }
        [data-testid="stExpander"] summary:hover { color: #c2410c !important; }

        /* alerts: square, accent bar */
        [data-testid="stAlert"] {
            border-radius: 0 !important; border: 1px solid #e4e4e7;
            border-left: 3px solid #c2410c;
            font-size: 0.85rem;
        }

        /* dividers tighter, captions mono */
        hr { border-color: #e4e4e7 !important; margin: 0.8rem 0 !important; }
        [data-testid="stCaptionContainer"] p {
            font-family: 'IBM Plex Mono', 'Consolas', 'Liberation Mono', 'DejaVu Sans Mono', monospace !important;
            font-size: 0.68rem !important; letter-spacing: 0.04em;
            color: #a1a1aa !important;
        }

        /* chat input square */
        [data-testid="stChatInput"] { border-radius: 0 !important; }
        [data-testid="stChatInput"] textarea {
            font-family: 'IBM Plex Mono', 'Consolas', 'Liberation Mono', 'DejaVu Sans Mono', monospace !important;
        }

        /* plotly: hide floating toolbar for a cleaner board */
        .modebar { display: none !important; }

        /* sidebar nav: active page orange marker */
        [data-testid="stSidebarNav"] a {
            border-radius: 0 !important; border-left: 3px solid transparent;
        }
        [data-testid="stSidebarNav"] a:hover { border-left: 3px solid #d4d4d8; }
        [data-testid="stSidebarNav"] a[aria-current="page"] {
            border-left: 3px solid #c2410c; background: #ffffff !important;
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
