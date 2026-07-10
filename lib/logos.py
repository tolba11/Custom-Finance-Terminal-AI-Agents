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


def logo_img_html(ticker: str, size: int = 28) -> str:
    """<img> tag for the ticker logo, or a neutral placeholder circle."""
    url = get_logo_data_url(ticker)
    if url:
        return (f'<img src="{url}" width="{size}" height="{size}" '
                f'style="border-radius:6px;object-fit:contain;'
                f'vertical-align:middle;background:#f4f4f5;padding:2px;"/>')
    letter = (ticker or "?")[0].upper()
    return (f'<span style="display:inline-flex;width:{size}px;height:{size}px;'
            f'border-radius:6px;background:#e4e4e7;color:#3f3f46;'
            f'align-items:center;justify-content:center;font-size:{size//2}px;'
            f'vertical-align:middle;">{letter}</span>')
