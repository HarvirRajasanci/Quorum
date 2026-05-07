from __future__ import annotations

from agents.base import BaseAgent
from agents.schemas import (
    ArgumentObject,
    DecisionObject,
    QuantObject,
    RiskObject,
    SentimentObject,
    SkepticObject,
)

_VALID_REEVAL_SECONDS = {30, 60, 120, 300}


class ChairAgent(BaseAgent):
    role = "Chair Agent"
    goal = (
        "Synthesize all agent inputs into a final investment decision. "
        "Weigh argument quality from the Skeptic, risk from the Risk Agent, and evidence strength. "
        "Deliver a clear verdict with reasoning that cites specific agents by name. "
        "Set a re-evaluation timer appropriate to the uncertainty level."
    )
    backstory = (
        "You are the managing partner of the fund. You have heard thousands of investment debates. "
        "You cut through noise, weigh evidence fairly, and make decisive calls. "
        "You are accountable for every decision."
    )

    async def run(
        self,
        ticker: str,
        news: SentimentObject,
        quant: QuantObject,
        bull: ArgumentObject,
        bear: ArgumentObject,
        risk: RiskObject,
        skeptic: SkepticObject | None,
        memory: list[dict],
        halt: bool = False,
    ) -> DecisionObject:
        halt_note = (
            "\n[HALT FLAG ACTIVE: Risk Agent interrupted the debate. "
            "You must issue HOLD or REJECT only. Do not issue INVEST.]\n"
            if halt
            else ""
        )

        skeptic_section = ""
        if skeptic:
            skeptic_section = (
                f"\nSceptic verdict on debate quality: {skeptic.verdict_on_debate_quality}\n"
                f"Weak arguments flagged: {[w.model_dump() for w in skeptic.weak_arguments]}\n"
            )

        memory_section = ""
        if memory:
            memory_section = f"\nPast decisions for {ticker} (last {len(memory[-3:])}): {memory[-3:]}\n"

        task = f"""Ticker: {ticker}{halt_note}

News: {news.headline} ({news.sentiment}, score {news.score:+.2f})
Quant: {quant.key_signal}

Bull Agent — "{bull.claim}" (confidence: {bull.confidence}/100)
Evidence: {bull.evidence}

Bear Agent — "{bear.claim}" (confidence: {bear.confidence}/100)
Evidence: {bear.evidence}

Risk Agent — Drawdown risk: {risk.drawdown_risk:.2f}, Interrupt: {risk.interrupt}
Note: "{risk.risk_note}"
{skeptic_section}{memory_section}
Synthesize and decide. Your reasoning MUST cite at least one specific agent by name.
{"You may only return HOLD or REJECT — the Risk Agent triggered a halt." if halt else ""}
reeval_seconds must be one of: 30, 60, 120, 300.

Return JSON with exactly these fields:
{{
  "verdict": "INVEST" | "HOLD" | "REJECT",
  "allocation_pct": <integer 0-100>,
  "confidence": <integer 0-100>,
  "risk_level": "LOW" | "MEDIUM" | "HIGH",
  "reasoning": "<2-3 sentences citing specific agent arguments by name>",
  "reeval_seconds": <30 | 60 | 120 | 300>
}}"""

        raw = await self._call(task, temperature=0.5)
        obj = DecisionObject.model_validate(raw)

        if halt and obj.verdict == "INVEST":
            obj = obj.model_copy(update={"verdict": "HOLD"})
        if obj.reeval_seconds not in _VALID_REEVAL_SECONDS:
            obj = obj.model_copy(update={"reeval_seconds": 60})

        return obj
