from __future__ import annotations

from agents.base import BaseAgent
from agents.schemas import QuantObject
from data.fetcher import get_quant


class QuantAgent(BaseAgent):
    role = "Quant Agent"
    goal = (
        "Retrieve and interpret quantitative market data for the given ticker. "
        "Identify the most significant technical signal — bullish or bearish. "
        "Speak in numbers. Every claim must have a data point behind it."
    )
    backstory = (
        "You are a quantitative analyst at a hedge fund. You distrust narratives and trust only numbers. "
        "You have built volatility models for 10 years. "
        "You are brief, precise, and always cite your figures."
    )

    async def run(self, ticker: str) -> QuantObject:
        data = get_quant(ticker)

        task = f"""Ticker: {ticker}

Raw market data:
- Price: ${data['price']}
- 24h change: {data['change_pct']:+.2f}%
- RSI (14-period): {data['rsi']}
- Volume: {data['volume']:,}

Classify and interpret this data. Return JSON with exactly these fields:
{{
  "price": {data['price']},
  "change_pct": {data['change_pct']},
  "rsi": {data['rsi']},
  "volatility": "LOW" | "MEDIUM" | "HIGH",
  "momentum": "BULLISH" | "BEARISH" | "NEUTRAL",
  "key_signal": "<one sentence — the single most important technical fact, cite actual numbers>"
}}

Classification rules:
- volatility: HIGH if |change_pct| > 3%, MEDIUM if > 1%, LOW otherwise
- momentum: BULLISH if rsi > 60, BEARISH if rsi < 45, NEUTRAL otherwise"""

        raw = await self._call(task, temperature=0.2)
        return QuantObject.model_validate(raw)
