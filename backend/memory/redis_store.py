from __future__ import annotations

import json
import logging
import os
from typing import Any

import redis as redis_lib
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger("quorum.memory.redis")

_REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379")
_MEMORY_KEY_PREFIX = "warroom:memory"
_CONFIDENCE_KEY_PREFIX = "warroom:confidence"
_MAX_DECISIONS = 10

_client: redis_lib.Redis | None = None


def _get_client() -> redis_lib.Redis | None:
    global _client
    if _client is not None:
        return _client
    try:
        _client = redis_lib.from_url(_REDIS_URL, socket_timeout=2.0, decode_responses=True)
        _client.ping()
        logger.info("Redis connected: %s", _REDIS_URL)
        return _client
    except Exception as exc:
        logger.warning("Redis unavailable (%s) — memory ops will be no-ops", exc)
        _client = None
        return None


def read_memory(ticker: str) -> list[dict[str, Any]]:
    client = _get_client()
    if client is None:
        return []

    key = f"{_MEMORY_KEY_PREFIX}:{ticker.upper()}"
    try:
        items = client.lrange(key, 0, _MAX_DECISIONS - 1)
        return [json.loads(item) for item in items]
    except Exception as exc:
        logger.warning("Failed to read memory for %s: %s", ticker, exc)
        return []


def write_memory(ticker: str, decision: dict[str, Any]) -> None:
    client = _get_client()
    if client is None:
        return

    key = f"{_MEMORY_KEY_PREFIX}:{ticker.upper()}"
    try:
        pipe = client.pipeline()
        pipe.lpush(key, json.dumps(decision))
        pipe.ltrim(key, 0, _MAX_DECISIONS - 1)
        pipe.execute()
    except Exception as exc:
        logger.warning("Failed to write memory for %s: %s", ticker, exc)


def get_confidence(ticker: str, agent: str) -> int | None:
    client = _get_client()
    if client is None:
        return None

    key = f"{_CONFIDENCE_KEY_PREFIX}:{ticker.upper()}:{agent}"
    try:
        val = client.get(key)
        return int(val) if val is not None else None
    except Exception as exc:
        logger.warning("Failed to get confidence for %s/%s: %s", ticker, agent, exc)
        return None


def set_confidence(ticker: str, agent: str, confidence: int) -> None:
    client = _get_client()
    if client is None:
        return

    key = f"{_CONFIDENCE_KEY_PREFIX}:{ticker.upper()}:{agent}"
    try:
        client.set(key, str(confidence))
    except Exception as exc:
        logger.warning("Failed to set confidence for %s/%s: %s", ticker, agent, exc)
