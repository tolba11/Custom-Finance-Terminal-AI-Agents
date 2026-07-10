"""Curated ETF peer groups for cost comparison."""

PEER_GROUPS = {
    "us_large_blend": ["SPY", "VOO", "IVV", "SPLG", "SCHX", "ITOT", "VTI"],
    "nasdaq_growth": ["QQQ", "QQQM", "ONEQ", "VUG", "SCHG", "IWY"],
    "us_small_cap": ["IWM", "VB", "SCHA", "IJR", "VBR"],
    "dividend": ["SCHD", "VYM", "VIG", "DVY", "HDV", "SDY", "NOBL"],
    "intl_developed": ["EFA", "VEA", "IEFA", "SCHF", "SPDW"],
    "emerging": ["VWO", "IEMG", "EEM", "SCHE", "SPEM"],
    "total_bond": ["AGG", "BND", "SCHZ", "SPAB", "IUSB"],
    "long_treasury": ["TLT", "VGLT", "SPTL", "EDV"],
    "corporate_bond": ["LQD", "VCIT", "SPBO", "IGIB"],
    "high_yield": ["HYG", "JNK", "SPHY", "USHY"],
    "gold": ["GLD", "IAU", "GLDM", "SGOL"],
    "real_estate": ["VNQ", "SCHH", "XLRE", "IYR", "RWR"],
    "semiconductors": ["SMH", "SOXX", "PSI", "XSD"],
    "tech_sector": ["XLK", "VGT", "IYW", "FTEC"],
    "financials": ["XLF", "VFH", "IYF", "FNCL"],
    "health_care": ["XLV", "VHT", "IYH", "FHLC"],
    "energy": ["XLE", "VDE", "IYE", "FENY"],
    "thematic_innovation": ["ARKK", "ARKW", "BOTZ", "ROBO"],
}


def find_peers(ticker: str) -> list:
    tk = ticker.upper()
    for group in PEER_GROUPS.values():
        if tk in group:
            return group
    return []
