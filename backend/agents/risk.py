from __future__ import annotations

import os

from agents.base import BaseAgent
from agents.schemas import ArgumentObject, QuantObject, RiskObject

_DRAWDOWN_THRESHOLD = float(os.environ.get("DRAWDOWN_THRESHOLD", "0.15"))


class RiskAgent(BaseAgent):
    role = "Risk Agent"
    goal = (
        "Monitor portfolio risk. If volatility is HIGH and drawdown risk exceeds the threshold, "
        "set interrupt to true. You do not argue about investment merits. "
        "You only enforce risk limits. Be terse."
    )
    backstory = (
        "You are the chief risk officer. You do not care about upside. "
        "Your only job is to prevent catastrophic loss. "
        "When the numbers exceed threshold, you stop the debate regardless of argument quality."
    )

    async def run(
        self,
        quant: QuantObject,
        bull: ArgumentObject,
        bear: ArgumentObject,
    ) -> RiskObject:
        task = f"""Market data:
- Price change: {quant.change_pct:+.2f}%
- RSI: {quant.rsi}
- Volatility: {quant.volatility}
- Momentum: {quant.momentum}

Debate signals:
- Bull confidence: {bull.confidence}/100
- Bear confidence: {bear.confidence}/100

Drawdown threshold: {_DRAWDOWN_THRESHOLD:.0%}

Assess risk exposure. Estimate maximum drawdown risk as a float between 0.0 and 1.0.
Set interrupt to true ONLY IF volatility is "HIGH" AND your drawdown_risk estimate exceeds {_DRAWDOWN_THRESHOLD}.

Return JSON with exactly these fields:
{{
  "drawdown_risk": <float 0.0 to 1.0>,
  "interrupt": <true | false>,
  "threshold_breached": <true | false>,
  "risk_note": "<one terse sentence>"
}}"""

        raw = await self._call(task, temperature=0.2)
        obj = RiskObject.model_validate(raw)
        # Enforce deterministically — LLM estimate informs drawdown_risk but the rule is hard
        if quant.volatility == "HIGH" and obj.drawdown_risk > _DRAWDOWN_THRESHOLD:
            obj = obj.model_copy(update={"interrupt": True, "threshold_breached": True})
        return obj
