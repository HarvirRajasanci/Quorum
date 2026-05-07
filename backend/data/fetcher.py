"""
Market data fetcher.

P2 replaces get_news() and get_quant() with real NewsAPI + yfinance calls.
The mock data below keeps agents working while the real pipeline is wired up.
Interface contract: shapes returned here must not change — agents depend on them.
"""
from __future__ import annotations

_MOCK_NEWS: dict[str, list[dict]] = {
    "TSLA": [
        {"title": "Tesla cuts Model Y prices in China amid slowing EV demand", "source": "Reuters"},
        {"title": "Tesla Q2 deliveries miss estimates by 8%, shares fall in after-hours", "source": "Bloomberg"},
        {"title": "Elon Musk confirms focus on FSD rollout despite delivery headwinds", "source": "CNBC"},
        {"title": "Chinese EV rivals BYD and NIO gain market share at Tesla's expense", "source": "WSJ"},
        {"title": "Tesla Berlin Gigafactory production ramp slower than expected", "source": "FT"},
    ],
    "NVDA": [
        {"title": "NVIDIA announces next-generation Blackwell GPU architecture for AI data centers", "source": "Reuters"},
        {"title": "NVIDIA Q2 revenue surges 122% YoY driven by AI chip demand", "source": "Bloomberg"},
        {"title": "Microsoft, Google, Meta triple H100 cluster orders from NVIDIA", "source": "WSJ"},
        {"title": "NVIDIA expands Taiwan supply chain to meet AI infrastructure demand", "source": "CNBC"},
        {"title": "Analysts raise NVIDIA price targets after record quarterly guidance", "source": "Barron's"},
    ],
    "AAPL": [
        {"title": "Apple Vision Pro sales disappoint in Q2, below analyst expectations", "source": "Bloomberg"},
        {"title": "Apple Services revenue hits record $24.2B, offsetting iPhone slowdown", "source": "Reuters"},
        {"title": "Apple expands India manufacturing as China supply chain risk persists", "source": "WSJ"},
        {"title": "iPhone 16 pre-orders tracking in line with iPhone 15 cycle", "source": "CNBC"},
        {"title": "Apple shares flat as investors weigh AI integration timeline", "source": "FT"},
    ],
}

_MOCK_QUANT: dict[str, dict] = {
    "TSLA": {
        "price": 247.32,
        "change_pct": -2.8,
        "rsi": 42.1,
        "volatility": "HIGH",
        "momentum": "BEARISH",
        "volume": 92_400_000,
    },
    "NVDA": {
        "price": 895.12,
        "change_pct": 3.2,
        "rsi": 68.4,
        "volatility": "MEDIUM",
        "momentum": "BULLISH",
        "volume": 44_800_000,
    },
    "AAPL": {
        "price": 182.43,
        "change_pct": -0.4,
        "rsi": 51.7,
        "volatility": "LOW",
        "momentum": "NEUTRAL",
        "volume": 53_100_000,
    },
}

_DEFAULT_NEWS = [{"title": "No significant recent news found for this ticker.", "source": "Mock"}]
_DEFAULT_QUANT = {
    "price": 100.00,
    "change_pct": 0.5,
    "rsi": 50.0,
    "volatility": "MEDIUM",
    "momentum": "NEUTRAL",
    "volume": 10_000_000,
}


def get_news(ticker: str) -> list[dict]:
    """Returns up to 5 recent headline dicts with 'title' and 'source' keys."""
    return _MOCK_NEWS.get(ticker.upper(), _DEFAULT_NEWS)


def get_quant(ticker: str) -> dict:
    """Returns price/technical dict with price, change_pct, rsi, volatility, momentum, volume."""
    return dict(_MOCK_QUANT.get(ticker.upper(), _DEFAULT_QUANT))
