from __future__ import annotations

from agents.base import BaseAgent
from agents.schemas import ArgumentObject, QuantObject, SentimentObject


class BearAgent(BaseAgent):
    role = "Bear Agent"
    goal = (
        "Argue aggressively AGAINST the investment. Expose every risk. "
        "Attack the Bull Agent's weakest evidence point by name. "
        "Be specific about what could go wrong and why."
    )
    backstory = (
        "You are a short-seller with a track record of calling market tops. "
        "You are deeply skeptical of hype and always look for what the market is ignoring. "
        "You have seen too many bull cases collapse. "
        "You are blunt, specific, and relentless in exposing weaknesses."
    )

    async def run(
        self,
        ticker: str,
        news: SentimentObject,
        quant: QuantObject,
        bull_output: ArgumentObject,
        reeval: bool = False,
    ) -> ArgumentObject:
        reeval_note = (
            "\n[RE-EVALUATION ROUND: The Skeptic flagged weak arguments. "
            "Sharpen your bear case with harder, more specific evidence.]\n"
            if reeval
            else ""
        )

        task = f"""Ticker: {ticker}{reeval_note}

News: {news.headline} (sentiment: {news.sentiment}, score: {news.score:+.2f})
Quant: {quant.key_signal} | RSI: {quant.rsi} | Volatility: {quant.volatility}

Bull Agent's argument to attack:
- Claim: "{bull_output.claim}"
- Evidence: {bull_output.evidence}
You MUST name and attack their weakest evidence point explicitly in your rebuttal field.

Build the strongest possible bear case. Return JSON with exactly these fields:
{{
  "position": "REJECT",
  "claim": "<your main argument, 1-2 sentences, be specific>",
  "evidence": ["<specific risk 1>", "<specific risk 2>", "<specific risk 3>"],
  "rebuttal": "<name the specific Bull evidence point you are attacking and why it fails>",
  "confidence": <integer 0-100>
}}"""

        raw = await self._call(task, temperature=0.8)
        raw.setdefault("position", "REJECT")
        return ArgumentObject.model_validate(raw)
