from __future__ import annotations

from agents.base import BaseAgent
from agents.schemas import ArgumentObject, RiskObject, SkepticObject


class SkepticAgent(BaseAgent):
    role = "Skeptic Agent"
    goal = (
        "Read all prior arguments and identify logical weaknesses, unsupported claims, or potential hallucinations. "
        "Call out specific claims by agent name. "
        "If arguments are poor quality, set force_reeval to true."
    )
    backstory = (
        "You are an epistemologist and former auditor. You do not take sides. "
        "You evaluate argument quality ruthlessly. "
        "You can smell a weak inference from a mile away. "
        "You name names when you call out bad reasoning."
    )

    async def run(
        self,
        bull: ArgumentObject,
        bear: ArgumentObject,
        risk: RiskObject,
    ) -> SkepticObject:
        task = f"""Bull Agent argument:
- Claim: "{bull.claim}"
- Evidence: {bull.evidence}
- Confidence: {bull.confidence}/100
- Rebuttal: {bull.rebuttal}

Bear Agent argument:
- Claim: "{bear.claim}"
- Evidence: {bear.evidence}
- Confidence: {bear.confidence}/100
- Rebuttal: {bear.rebuttal}

Risk Agent assessment:
- Drawdown risk: {risk.drawdown_risk:.2f}
- Note: "{risk.risk_note}"

Evaluate argument quality ruthlessly. Flag weak inferences, unsupported claims, or circular reasoning.
Set force_reeval to true only if at least one argument is clearly WEAK — vague, unsupported, or self-contradictory.

Return JSON with exactly these fields:
{{
  "weak_arguments": [
    {{"agent": "bull" | "bear", "claim": "<the specific weak claim text>", "reason_weak": "<why it fails>"}}
  ],
  "hallucination_flags": ["<any claim that appears fabricated or unverifiable>"],
  "force_reeval": <true | false>,
  "verdict_on_debate_quality": "STRONG" | "ADEQUATE" | "WEAK"
}}
If no weak arguments exist, return an empty list for weak_arguments and an empty list for hallucination_flags."""

        raw = await self._call(task, temperature=0.5)
        return SkepticObject.model_validate(raw)
