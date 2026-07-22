"""Ticker -> domain map + base64 data-URL loader from assets/logos/."""
import base64
import os

ASSETS_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)),
                          "assets", "logos")

TICKER_DOMAINS = {
    "AAPL": "apple.com", "MSFT": "microsoft.com", "GOOGL": "google.com",
    "GOOG": "google.com", "AMZN": "amazon.com", "NVDA": "nvidia.com",
    "META": "meta.com", "TSLA": "tesla.com", "BRK-B": "berkshirehathaway.com",
    "LLY": "lilly.com", "AVGO": "broadcom.com", "JPM": "jpmorganchase.com",
    "V": "visa.com", "XOM": "exxonmobil.com", "UNH": "unitedhealthgroup.com",
    "MA": "mastercard.com", "PG": "pg.com", "JNJ": "jnj.com",
    "HD": "homedepot.com", "COST": "costco.com", "ORCL": "oracle.com",
    "MRK": "merck.com", "ABBV": "abbvie.com", "CVX": "chevron.com",
    "KO": "coca-cola.com", "PEP": "pepsico.com", "BAC": "bankofamerica.com",
    "ADBE": "adobe.com", "WMT": "walmart.com", "CRM": "salesforce.com",
    "MCD": "mcdonalds.com", "NFLX": "netflix.com", "AMD": "amd.com",
    "TMO": "thermofisher.com", "CSCO": "cisco.com", "ACN": "accenture.com",
    "ABT": "abbott.com", "LIN": "linde.com", "INTC": "intel.com",
    "DIS": "disney.com", "WFC": "wellsfargo.com", "CMCSA": "comcast.com",
    "VZ": "verizon.com", "INTU": "intuit.com", "QCOM": "qualcomm.com",
    "IBM": "ibm.com", "TXN": "ti.com", "PFE": "pfizer.com",
    "NOW": "servicenow.com", "GE": "ge.com", "CAT": "caterpillar.com",
    "UNP": "up.com", "AMAT": "appliedmaterials.com", "SPGI": "spglobal.com",
    "PM": "pmi.com", "HON": "honeywell.com", "UBER": "uber.com",
    "GS": "goldmansachs.com", "MS": "morganstanley.com", "RTX": "rtx.com",
    "BA": "boeing.com", "NKE": "nike.com", "LOW": "lowes.com",
    "T": "att.com", "AXP": "americanexpress.com", "BKNG": "booking.com",
    "SBUX": "starbucks.com", "MDT": "medtronic.com", "BMY": "bms.com",
    "DE": "deere.com", "PLD": "prologis.com", "BLK": "blackrock.com",
    "GILD": "gilead.com", "ADP": "adp.com", "MMC": "marshmclennan.com",
    "AMGN": "amgen.com", "SCHW": "schwab.com", "CI": "thecignagroup.com",
    "C": "citigroup.com", "MO": "altria.com", "SO": "southerncompany.com",
    "DUK": "duke-energy.com", "PYPL": "paypal.com", "ABNB": "airbnb.com",
    "SHOP": "shopify.com", "SQ": "block.xyz", "SNOW": "snowflake.com",
    "PLTR": "palantir.com", "COIN": "coinbase.com", "MRVL": "marvell.com",
    "MU": "micron.com", "PANW": "paloaltonetworks.com", "F": "ford.com",
    "GM": "gm.com", "DAL": "delta.com", "UAL": "united.com",
    "AAL": "aa.com", "CCL": "carnival.com", "MAR": "marriott.com",
    "TGT": "target.com", "CVS": "cvshealth.com", "FDX": "fedex.com",
    "UPS": "ups.com", "DHR": "danaher.com", "ISRG": "intuitive.com",
    "VRTX": "vrtx.com", "REGN": "regeneron.com", "LMT": "lockheedmartin.com",
    "NOC": "northropgrumman.com", "GD": "gd.com", "COP": "conocophillips.com",
    "SLB": "slb.com", "EOG": "eogresources.com", "OXY": "oxy.com",
    "KMI": "kindermorgan.com", "DOW": "dow.com", "FCX": "fcx.com",
    "NEM": "newmont.com", "ETN": "eaton.com", "EMR": "emerson.com",
    "ITW": "itw.com", "APH": "amphenol.com", "KLAC": "kla.com",
    "LRCX": "lamresearch.com", "ASML": "asml.com", "TSM": "tsmc.com",
    "TM": "toyota.com", "SONY": "sony.com", "BABA": "alibabagroup.com",
    # ETFs / issuers
    "SPY": "ssga.com", "VOO": "vanguard.com", "IVV": "ishares.com",
    "QQQ": "invesco.com", "VTI": "vanguard.com", "IWM": "ishares.com",
    "DIA": "ssga.com", "VEA": "vanguard.com", "VWO": "vanguard.com",
    "EFA": "ishares.com", "AGG": "ishares.com", "BND": "vanguard.com",
    "TLT": "ishares.com", "LQD": "ishares.com", "HYG": "ishares.com",
    "GLD": "ssga.com", "SLV": "ishares.com", "VNQ": "vanguard.com",
    "SCHD": "schwab.com", "VIG": "vanguard.com", "VYM": "vanguard.com",
    "ARKK": "ark-funds.com", "SMH": "vaneck.com", "SOXX": "ishares.com",
    "XLK": "ssga.com", "XLF": "ssga.com", "XLV": "ssga.com",
    "XLE": "ssga.com", "XLI": "ssga.com", "XLY": "ssga.com",
    "XLP": "ssga.com", "XLU": "ssga.com", "XLRE": "ssga.com",
    "XLB": "ssga.com", "XLC": "ssga.com",
}

_MIME = {".svg": "image/svg+xml", ".png": "image/png",
         ".jpg": "image/jpeg", ".jpeg": "image/jpeg", ".ico": "image/x-icon"}


def get_logo_data_url(ticker: str) -> str:
    """Return a base64 data URL for a locally stored logo, or '' if none."""
    tk = ticker.upper().replace("/", "-")
    if not os.path.isdir(ASSETS_DIR):
        return ""
    for ext, mime in _MIME.items():
        path = os.path.join(ASSETS_DIR, f"{tk}{ext}")
        if os.path.exists(path):
            try:
                with open(path, "rb") as f:
                    b64 = base64.b64encode(f.read()).decode()
                return f"data:{mime};base64,{b64}"
            except Exception:
                return ""
    return ""


def _letter_uri(ticker: str, size: int) -> str:
    """Data-URI SVG letter chip — final fallback, always renders."""
    from urllib.parse import quote
    letter = (ticker or "?")[0].upper()
    svg = (f"<svg xmlns='http://www.w3.org/2000/svg' width='{size}' "
           f"height='{size}'><rect width='100%' height='100%' rx='6' "
           f"fill='#252c3b'/><text x='50%' y='55%' "
           f"dominant-baseline='middle' text-anchor='middle' "
           f"font-family='Arial,sans-serif' font-weight='600' "
           f"font-size='{int(size * 0.5)}' fill='#b7c0d0'>{letter}</text>"
           f"</svg>")
    return "data:image/svg+xml;utf8," + quote(svg)


def _clean_domain(domain: str) -> str:
    if not domain:
        return ""
    d = domain.split("//")[-1].split("/")[0].strip()
    return d[4:] if d.startswith("www.") else d


def logo_img_html(ticker: str, size: int = 28, domain: str = None) -> str:
    """Company logo <img> with a browser-side fallback chain:
    local asset -> symbol logo CDN / domain favicon -> letter chip."""
    tk = (ticker or "").upper().replace("/", "-")
    style = (f'width:{size}px;height:{size}px;border-radius:6px;'
             f'object-fit:contain;vertical-align:middle;'
             f'background:#e9edf3;padding:2px;flex-shrink:0;')
    local = get_logo_data_url(tk)
    letter = _letter_uri(tk, size)
    if local:
        primary, fallback = local, letter
    else:
        # High-res brand mark first; tiny upscaled favicons only as backup.
        primary = f"https://assets.parqet.com/logos/symbol/{tk}?format=png"
        dom = _clean_domain(domain) or TICKER_DOMAINS.get(tk, "")
        if dom:
            fallback = ("https://t3.gstatic.com/faviconV2?client=SOCIAL"
                        "&type=FAVICON&fallback_opts=TYPE,SIZE,URL"
                        f"&url=https://{dom}&size=128")
        else:
            fallback = letter
    return (f'<img src="{primary}" style="{style}" loading="lazy" '
            f"onerror=\"this.onerror=function(){{this.onerror=null;"
            f"this.src='{letter}';}};this.src='{fallback}';\"/>")
