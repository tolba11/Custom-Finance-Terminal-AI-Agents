"""Shared configuration, branding, and terminal styling."""
import os

from dotenv import load_dotenv

load_dotenv()

APP_NAME = "Pyramid Terminal"


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
        '<div class="tt-footer">PYRAMID TERMINAL — market data may be '
        'delayed</div>', unsafe_allow_html=True)


def render_sidebar(st):
    """Terminal brand block in the sidebar."""
    st.sidebar.markdown(
        '<div class="tt-brand"><span class="tt-brand-mark"></span>'
        'PYRAMID<br>TERMINAL</div>',
        unsafe_allow_html=True)
    q = st.sidebar.text_input("Jump to ticker", key="omni_q",
                              placeholder="AAPL, 7203.T, BTC-USD")
    if q and q.strip():
        t = q.strip().upper()
        if st.session_state.get("omni_last") != t:
            st.session_state["omni_last"] = t
            st.session_state["sa_symbol"] = t
            st.session_state["sa_q"] = t
            try:
                st.switch_page("views/stock_analyzer.py")
            except Exception:
                pass


def apply_base_style(st):
    """Bloomberg-inspired light terminal styling."""
    st.markdown(
        """
        <style>
        @import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;500;600;700&display=swap');
        html, body, [class*="css"], .main .block-container {
            font-family: 'Segoe UI', 'Liberation Sans', 'DejaVu Sans', Arial, sans-serif;
            font-size: 15px;
            color: #dee3ea;
        }
        .main .block-container { padding-top: 1.2rem; max-width: 1500px; }

        /* headings: compact, uppercase, tracked */
        h1 {
            font-family: 'IBM Plex Mono', 'Consolas', 'Liberation Mono', 'DejaVu Sans Mono', monospace !important;
            text-transform: uppercase;
            letter-spacing: 0.06em;
            font-size: 1.55rem !important;
            border-bottom: 3px solid #f97316;
            padding-bottom: 0.35rem;
        }
        h2, h3 {
            font-family: 'IBM Plex Mono', 'Consolas', 'Liberation Mono', 'DejaVu Sans Mono', monospace !important;
            text-transform: uppercase;
            letter-spacing: 0.05em;
            font-size: 1.02rem !important;
            color: #b7c0d0;
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
            color: #8a93a6;
        }
        [data-testid="stMetric"] {
            background: #161b26;
            border: 1px solid #252c3b;
            border-left: 3px solid #f97316;
            padding: 0.45rem 0.7rem;
        }

        /* tables + dataframes: dense terminal grid */
        [data-testid="stDataFrame"] { border: 1px solid #252c3b; }
        [data-testid="stDataFrame"] * {
            font-family: 'IBM Plex Mono', 'Consolas', 'Liberation Mono', 'DejaVu Sans Mono', monospace !important;
            font-size: 12.5px !important;
        }

        /* sidebar: flat, bordered */
        [data-testid="stSidebar"] {
            background: #10141d;
            border-right: 1px solid #252c3b;
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
            color: #dee3ea;
            padding: 0.4rem 0 0.8rem 0;
            border-bottom: 2px solid #f97316;
            margin-bottom: 0.6rem;
        }
        .tt-brand-mark {
            display: inline-block; width: 11px; height: 11px;
            background: #f97316; margin-right: 8px;
        }
        .tt-subtitle {
            font-family: 'IBM Plex Mono', 'Consolas', 'Liberation Mono', 'DejaVu Sans Mono', monospace;
            font-size: 0.75rem; letter-spacing: 0.14em;
            color: #8a93a6; margin: 0.2rem 0 0.8rem 0;
        }
        .tt-footer {
            font-family: 'IBM Plex Mono', 'Consolas', 'Liberation Mono', 'DejaVu Sans Mono', monospace;
            font-size: 0.68rem; letter-spacing: 0.1em; color: #5c6575;
            border-top: 1px solid #252c3b;
            padding-top: 0.5rem; margin-top: 2rem;
        }
        .tt-func {
            border: 1px solid #252c3b; border-left: 3px solid #f97316;
            padding: 0.7rem 0.9rem; margin-bottom: 0.6rem; background: #161b26;
        }
        .tt-func-name {
            font-family: 'IBM Plex Mono', 'Consolas', 'Liberation Mono', 'DejaVu Sans Mono', monospace; font-weight: 600;
            text-transform: uppercase; letter-spacing: 0.06em;
            font-size: 0.85rem;
        }
        .tt-func-desc { color: #8a93a6; font-size: 0.82rem; }

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
            gap: 0; border-bottom: 2px solid #252c3b;
            background: transparent;
        }
        button[data-baseweb="tab"] {
            font-family: 'IBM Plex Mono', 'Consolas', 'Liberation Mono', 'DejaVu Sans Mono', monospace !important;
            text-transform: uppercase; letter-spacing: 0.07em;
            font-size: 0.78rem !important; font-weight: 600;
            color: #8a93a6; background: transparent !important;
            border-radius: 0 !important; padding: 0.55rem 1.1rem;
            margin-bottom: -2px; border-bottom: 3px solid transparent;
        }
        button[data-baseweb="tab"]:hover { color: #dee3ea; background: #10141d !important; }
        button[data-baseweb="tab"][aria-selected="true"] {
            color: #f97316 !important; border-bottom: 3px solid #f97316;
        }
        div[data-baseweb="tab-highlight"], div[data-baseweb="tab-border"] { display: none; }
        button[data-baseweb="tab"] p { font-size: 0.78rem !important; font-weight: 600; }

        /* buttons: square, mono, orange hover fill */
        .stButton > button, .stDownloadButton > button,
        [data-testid^="stBaseButton-secondary"], [data-testid^="stBaseButton-primary"] {
            font-family: 'IBM Plex Mono', 'Consolas', 'Liberation Mono', 'DejaVu Sans Mono', monospace !important;
            text-transform: uppercase; letter-spacing: 0.08em;
            font-size: 0.75rem !important; font-weight: 600;
            border-radius: 0 !important; border: 1px solid #dee3ea !important;
            color: #dee3ea; background: #161b26;
            padding: 0.35rem 1.1rem; transition: all .12s ease;
        }
        .stButton > button:hover, .stDownloadButton > button:hover {
            background: #f97316 !important; border-color: #f97316 !important;
            color: #161b26 !important;
        }
        .stButton > button:focus:not(:active) { border-color: #f97316 !important; color: #f97316; }

        /* segmented control: joined square group, orange active */
        [data-testid="stSegmentedControl"] button,
        [data-testid="stButtonGroup"] button {
            font-family: 'IBM Plex Mono', 'Consolas', 'Liberation Mono', 'DejaVu Sans Mono', monospace !important;
            font-size: 0.74rem !important; font-weight: 600;
            letter-spacing: 0.05em; border-radius: 0 !important;
            border: 1px solid #313a4d !important; margin-left: -1px;
            color: #9aa4b6; background: #161b26; padding: 0.25rem 0.8rem;
        }
        [data-testid="stSegmentedControl"] button:hover,
        [data-testid="stButtonGroup"] button:hover { background: #10141d; color: #dee3ea; }
        [data-testid="stSegmentedControl"] button[aria-checked="true"],
        [data-testid="stSegmentedControl"] button[kind="segmented_controlActive"],
        [data-testid="stButtonGroup"] button[aria-checked="true"],
        [data-testid^="stBaseButton-segmented_controlActive"] {
            background: #dee3ea !important; color: #161b26 !important;
            border-color: #dee3ea !important;
        }

        /* inputs + selects: square, mono, orange focus */
        [data-baseweb="input"], [data-baseweb="base-input"],
        [data-baseweb="select"] > div, .stTextInput input, .stNumberInput input {
            border-radius: 0 !important;
            font-family: 'IBM Plex Mono', 'Consolas', 'Liberation Mono', 'DejaVu Sans Mono', monospace !important;
            font-size: 0.85rem !important;
        }
        [data-baseweb="input"]:focus-within, [data-baseweb="select"] > div:focus-within {
            border-color: #f97316 !important; box-shadow: none !important;
        }
        [data-baseweb="popover"] li {
            font-family: 'IBM Plex Mono', 'Consolas', 'Liberation Mono', 'DejaVu Sans Mono', monospace !important;
            font-size: 0.82rem !important;
        }
        .stTextInput label, .stSelectbox label, .stNumberInput label,
        [data-testid="stWidgetLabel"] p {
            font-family: 'IBM Plex Mono', 'Consolas', 'Liberation Mono', 'DejaVu Sans Mono', monospace !important;
            text-transform: uppercase; letter-spacing: 0.07em;
            font-size: 0.68rem !important; color: #8a93a6 !important;
        }

        /* expanders: bordered square panels, mono header */
        [data-testid="stExpander"] {
            border: 1px solid #252c3b !important; border-radius: 0 !important;
            background: #161b26;
        }
        [data-testid="stExpander"] summary {
            font-family: 'IBM Plex Mono', 'Consolas', 'Liberation Mono', 'DejaVu Sans Mono', monospace !important;
            text-transform: uppercase; letter-spacing: 0.07em;
            font-size: 0.75rem !important; font-weight: 600;
        }
        [data-testid="stExpander"] summary:hover { color: #f97316 !important; }

        /* alerts: square, accent bar */
        [data-testid="stAlert"] {
            border-radius: 0 !important; border: 1px solid #252c3b;
            border-left: 3px solid #f97316;
            font-size: 0.85rem;
        }

        /* dividers tighter, captions mono */
        hr { border-color: #252c3b !important; margin: 0.8rem 0 !important; }
        [data-testid="stCaptionContainer"] p {
            font-family: 'IBM Plex Mono', 'Consolas', 'Liberation Mono', 'DejaVu Sans Mono', monospace !important;
            font-size: 0.68rem !important; letter-spacing: 0.04em;
            color: #5c6575 !important;
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
        [data-testid="stSidebarNav"] a:hover { border-left: 3px solid #313a4d; }
        [data-testid="stSidebarNav"] a[aria-current="page"] {
            border-left: 3px solid #f97316; background: #161b26 !important;
        }
        
        /* widget cards (OpenBB-style) */
        [data-testid="stVerticalBlockBorderWrapper"] {
            background: #11151f; border: 1px solid #252c3b !important;
            border-radius: 0 !important;
        }
        [data-testid="stVerticalBlockBorderWrapper"]:hover {
            border-color: #3a4356 !important;
        }
        /* copilot popover trigger */
        [data-testid="stPopover"] button {
            border: 1px solid #f97316 !important;
            color: #f97316 !important; background: transparent !important;
        }
        [data-testid="stPopover"] button:hover {
            background: #f97316 !important; color: #0e1117 !important;
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
