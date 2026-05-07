from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field


class SentimentObject(BaseModel):
    headline: str
    source: str
    sentiment: Literal["BULLISH", "BEARISH", "NEUTRAL"]
    score: float = Field(..., ge=-1.0, le=1.0)
    reasoning: str


class QuantObject(BaseModel):
    price: float
    change_pct: float
    rsi: float
    volatility: Literal["LOW", "MEDIUM", "HIGH"]
    momentum: Literal["BULLISH", "BEARISH", "NEUTRAL"]
    key_signal: str


class ArgumentObject(BaseModel):
    position: Literal["INVEST", "REJECT"]
    claim: str
    evidence: list[str]
    rebuttal: str | None = None
    confidence: int = Field(..., ge=0, le=100)


class RiskObject(BaseModel):
    drawdown_risk: float = Field(..., ge=0.0, le=1.0)
    interrupt: bool
    threshold_breached: bool
    risk_note: str


class WeakArgument(BaseModel):
    agent: str
    claim: str
    reason_weak: str


class SkepticObject(BaseModel):
    weak_arguments: list[WeakArgument]
    hallucination_flags: list[str]
    force_reeval: bool
    verdict_on_debate_quality: Literal["STRONG", "ADEQUATE", "WEAK"]


class DecisionObject(BaseModel):
    verdict: Literal["INVEST", "HOLD", "REJECT"]
    allocation_pct: int = Field(..., ge=0, le=100)
    confidence: int = Field(..., ge=0, le=100)
    risk_level: Literal["LOW", "MEDIUM", "HIGH"]
    reasoning: str
    reeval_seconds: int


class WSMessage(BaseModel):
    type: Literal["agent_message", "decision", "error", "status", "benchmark"]
    timestamp: str
    payload: dict
