"""Load/save user holdings to data/portfolio.json (gitignored)."""
import json
import os

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")
PORTFOLIO_PATH = os.path.join(DATA_DIR, "portfolio.json")


def load_portfolio() -> list:
    """[{'ticker': str, 'shares': float, 'cost_basis': float}, ...]"""
    try:
        with open(PORTFOLIO_PATH, "r") as f:
            data = json.load(f)
        return data if isinstance(data, list) else []
    except (FileNotFoundError, json.JSONDecodeError):
        return []


def save_portfolio(holdings: list) -> None:
    os.makedirs(DATA_DIR, exist_ok=True)
    with open(PORTFOLIO_PATH, "w") as f:
        json.dump(holdings, f, indent=2)
