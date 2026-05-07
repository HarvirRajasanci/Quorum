from __future__ import annotations

import json
import logging
import os
import time
from pathlib import Path
from typing import Any

import httpx
import yfinance as yf
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger("quorum.data.fetcher")

_NEWS_API_KEY = os.getenv("NEWS_API_KEY", "")
_NEWS_API_URL = "https://newsapi.org/v2/everything"
_CACHE_DIR = Path(__file__).resolve().parent / "cache"
_REQUEST_TIMEOUT = 5.0
_MAX_RETRIES = 3
_RETRY_BACKOFF = 1.0

_FALLBACK_NEWS = [{"title": "No significant recent news found.", "source": "NewsAPI Fallback"}]

_FALLBACK_QUANT: dict[str, Any] = {
    "price": 100.0,
    "change_pct": 0.0,
    "rsi": 50.0,
    "volatility": "MEDIUM",
    "momentum": "NEUTRAL",
    "volume": 0,
    "key_signal": "No data available — using neutral defaults.",
}

_DEFAULT_QUANT: dict[str, Any] = {
    "price": 100.0,
    "change_pct": 0.0,
    "rsi": 50.0,
    "volatility": "MEDIUM",
    "momentum": "NEUTRAL",
    "key_signal": "No data available — using neutral defaults.",
}


def _load_cache(ticker: str) -> list[dict] | None:
    path = _CACHE_DIR / f"{ticker.upper()}.json"
    if not path.exists():
        return None
    try:
        with open(path) as f:
            articles: list[dict] = json.load(f)
        return [
            {
                "title": a.get("headline") or a.get("title", "No headline"),
                "source": a.get("source", "Cache"),
                "sentiment_guess": a.get("sentiment_guess"),
            }
            for a in articles
        ]
    except (json.JSONDecodeError, OSError) as exc:
        logger.warning("Failed to read cache %s: %s", path, exc)
        return None


def _fetch_newsapi(ticker: str) -> list[dict] | None:
    if not _NEWS_API_KEY:
        logger.info("No NEWS_API_KEY set — skipping NewsAPI")
        return None

    params = {
        "q": ticker,
        "language": "en",
        "pageSize": 5,
        "sortBy": "publishedAt",
        "apiKey": _NEWS_API_KEY,
    }

    last_exc: Exception | None = None
    for attempt in range(1, _MAX_RETRIES + 1):
        try:
            with httpx.Client(timeout=_REQUEST_TIMEOUT) as client:
                resp = client.get(_NEWS_API_URL, params=params)
                resp.raise_for_status()
                data = resp.json()

            if data.get("status") != "ok":
                logger.warning("NewsAPI returned non-ok status: %s", data.get("status"))
                return None

            articles = data.get("articles", [])
            if not articles:
                logger.info("NewsAPI returned 0 articles for %s", ticker)
                return None

            return [
                {
                    "title": a.get("title", "Untitled"),
                    "source": (a.get("source") or {}).get("name", "NewsAPI"),
                }
                for a in articles[:5]
            ]

        except httpx.TimeoutException as exc:
            logger.warning("NewsAPI timeout (attempt %d/%d) for %s", attempt, _MAX_RETRIES, ticker)
            last_exc = exc
        except httpx.HTTPStatusError as exc:
            logger.warning("NewsAPI HTTP %s (attempt %d/%d) for %s", exc.response.status_code, attempt, _MAX_RETRIES, ticker)
            last_exc = exc
        except Exception as exc:
            logger.warning("NewsAPI error (attempt %d/%d) for %s: %s", attempt, _MAX_RETRIES, ticker, exc)
            last_exc = exc

        if attempt < _MAX_RETRIES:
            time.sleep(_RETRY_BACKOFF)

    logger.error("NewsAPI failed after %d attempts for %s: %s", _MAX_RETRIES, ticker, last_exc)
    return None


def get_news(ticker: str, override: str | None = None) -> list[dict]:
    ticker = ticker.upper()

    if override:
        logger.info("Override set for %s — returning injected event", ticker)
        return [{"title": override, "source": "Breaking News"}]

    articles = _fetch_newsapi(ticker)
    if articles:
        return articles

    cached = _load_cache(ticker)
    if cached:
        logger.info("Fell back to cache for %s", ticker)
        return cached

    logger.warning("All sources failed for %s — returning fallback news", ticker)
    return list(_FALLBACK_NEWS)


def _compute_rsi(prices: list[float], period: int = 14) -> float:
    if len(prices) < period + 1:
        return 50.0

    deltas = [prices[i] - prices[i - 1] for i in range(1, len(prices))]
    gains = [d if d > 0 else 0.0 for d in deltas]
    losses = [-d if d < 0 else 0.0 for d in deltas]

    avg_gain = sum(gains[:period]) / period
    avg_loss = sum(losses[:period]) / period

    if avg_loss == 0:
        return 100.0

    for i in range(period, len(gains)):
        avg_gain = (avg_gain * (period - 1) + gains[i]) / period
        avg_loss = (avg_loss * (period - 1) + losses[i]) / period

    if avg_loss == 0:
        return 100.0

    rs = avg_gain / avg_loss
    return round(100.0 - (100.0 / (1.0 + rs)), 2)


def _classify_volatility(change_pct: float) -> str:
    if abs(change_pct) > 3.0:
        return "HIGH"
    if abs(change_pct) > 1.0:
        return "MEDIUM"
    return "LOW"


def _classify_momentum(rsi: float) -> str:
    if rsi > 60:
        return "BULLISH"
    if rsi < 45:
        return "BEARISH"
    return "NEUTRAL"


def _build_key_signal(price: float, change_pct: float, rsi: float, volatility: str, momentum: str) -> str:
    parts = []
    parts.append(f"Price at ${price:.2f}")
    parts.append(f"{change_pct:+.2f}% today")

    if momentum == "BULLISH":
        parts.append(f"RSI at {rsi:.1f} signals bullish momentum")
    elif momentum == "BEARISH":
        parts.append(f"RSI at {rsi:.1f} signals bearish momentum")
    else:
        parts.append(f"RSI at {rsi:.1f} is neutral")

    if volatility == "HIGH":
        parts.append("volatility is elevated")
    elif volatility == "LOW":
        parts.append("volatility is low")

    return ". ".join(parts) + "."


def get_quant(ticker: str) -> dict:
    ticker = ticker.upper()

    try:
        stock = yf.Ticker(ticker)
        hist = stock.history(period="1mo", timeout=_REQUEST_TIMEOUT)

        if hist.empty:
            logger.warning("yfinance returned empty history for %s", ticker)
            result = dict(_DEFAULT_QUANT)
            result["volume"] = 0
            return result

        closes = hist["Close"].tolist()
        latest = closes[-1] if closes else 100.0
        prev_close = closes[-2] if len(closes) > 1 else latest

        price = round(float(latest), 2)
        change_pct = round(((latest - prev_close) / prev_close) * 100, 2) if prev_close else 0.0

        rsi = _compute_rsi(closes)
        volatility = _classify_volatility(change_pct)
        momentum = _classify_momentum(rsi)
        volume = int(hist["Volume"].iloc[-1]) if "Volume" in hist.columns else 0
        key_signal = _build_key_signal(price, change_pct, rsi, volatility, momentum)

        return {
            "price": price,
            "change_pct": change_pct,
            "rsi": rsi,
            "volatility": volatility,
            "momentum": momentum,
            "volume": volume,
            "key_signal": key_signal,
        }

    except Exception as exc:
        logger.error("yfinance failed for %s: %s", ticker, exc)
        result = dict(_FALLBACK_QUANT)
        result["volume"] = 0
        return result
