from __future__ import annotations

from agents.base import BaseAgent
from agents.schemas import SentimentObject
from data.fetcher import get_news


class NewsAgent(BaseAgent):
    role = "News Agent"
    goal = (
        "Fetch and analyze the latest financial news for the given ticker. "
        "Surface the single most market-moving headline and assess its sentiment "
        "as BULLISH, BEARISH, or NEUTRAL with a score from -1.0 to 1.0. "
        "Be specific. Do not summarize vaguely. Name the actual event."
    )
    backstory = (
        "You are a former Reuters financial journalist with 15 years covering markets. "
        "You have an instinct for which headlines move markets and which are noise. "
        "You are concise, direct, and never speculate beyond what the data says."
    )

    async def run(self, ticker: str, injected_event: str | None = None) -> SentimentObject:
        headlines = get_news(ticker)
        if injected_event:
            headlines = [{"title": injected_event, "source": "Breaking News"}] + headlines[:4]

        headlines_text = "\n".join(
            f"{i + 1}. [{h['source']}] {h['title']}" for i, h in enumerate(headlines)
        )

        task = f"""Ticker: {ticker}

Headlines:
{headlines_text}

Identify the single most significant market-moving headline.
Return JSON with exactly these fields:
{{
  "headline": "<exact headline text>",
  "source": "<source name>",
  "sentiment": "BULLISH" | "BEARISH" | "NEUTRAL",
  "score": <float from -1.0 to 1.0>,
  "reasoning": "<one sentence explaining why this moves the market>"
}}"""

        raw = await self._call(task, temperature=0.3)
        return SentimentObject.model_validate(raw)
