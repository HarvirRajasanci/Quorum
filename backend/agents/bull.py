from __future__ import annotations

from agents.base import BaseAgent
from agents.schemas import ArgumentObject, QuantObject, SentimentObject


class BullAgent(BaseAgent):
    role = "Bull Agent"
    goal = (
        "Argue aggressively FOR the investment. Use the news and quant data as evidence. "
        "If the Bear Agent has already argued, directly rebut their weakest point by name. "
        "Do not be polite. Win the argument."
    )
    backstory = (
        "You are an aggressive growth investor who has made a career finding overlooked opportunities. "
        "You believe markets underreact to positive catalysts. "
        "You are combative in debates and will directly challenge bearish claims. "
        "You always back your position with specific evidence."
    )

    async def run(
        self,
        ticker: str,
        news: SentimentObject,
        quant: QuantObject,
        bear_output: ArgumentObject | None = None,
        reeval: bool = False,
    ) -> ArgumentObject:
        reeval_note = (
            "\n[RE-EVALUATION ROUND: The Skeptic flagged weak arguments. "
            "Strengthen your case with more specific, data-backed evidence.]\n"
            if reeval
            else ""
        )

        bear_section = ""
        if bear_output:
            bear_section = f"""
Bear Agent's argument to rebut:
- Claim: "{bear_output.claim}"
- Evidence: {bear_output.evidence}
You MUST name and attack their single weakest evidence point in your rebuttal field."""

        rebuttal_placeholder = (
            '"<direct attack on Bear\'s weakest evidence point, name it explicitly>"'
            if bear_output
            else "null"
        )
        task = f"""Ticker: {ticker}{reeval_note}

News: {news.headline} (sentiment: {news.sentiment}, score: {news.score:+.2f})
Quant: {quant.key_signal} | RSI: {quant.rsi} | Price: ${quant.price} ({quant.change_pct:+.2f}%)
{bear_section}

Build the strongest possible bull case. Return JSON with exactly these fields:
{{
  "position": "INVEST",
  "claim": "<your main argument, 1-2 sentences, be specific>",
  "evidence": ["<data-backed point 1>", "<data-backed point 2>", "<data-backed point 3>"],
  "rebuttal": {rebuttal_placeholder},
  "confidence": <integer 0-100>
}}"""

        raw = await self._call(task, temperature=0.8)
        raw.setdefault("position", "INVEST")
        return ArgumentObject.model_validate(raw)
