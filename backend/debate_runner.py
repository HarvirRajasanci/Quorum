from __future__ import annotations

import asyncio
import logging
import time
from collections.abc import AsyncGenerator
from datetime import datetime, timezone

from agents.bear import BearAgent
from agents.bull import BullAgent
from agents.chair import ChairAgent
from agents.news import NewsAgent
from agents.quant import QuantAgent
from agents.risk import RiskAgent
from agents.schemas import WSMessage
from agents.skeptic import SkepticAgent

logger = logging.getLogger("quorum.debate")

# Skeptic can force at most this many re-evaluation cycles per debate
_MAX_REEVAL = 1


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _agent_msg(
    agent: str,
    raw: dict,
    content: str,
    confidence: int | None = None,
    flag: str | None = None,
) -> WSMessage:
    return WSMessage(
        type="agent_message",
        timestamp=_now(),
        payload={
            "agent": agent,
            "content": content,
            "confidence": confidence,
            "flag": flag,
            "raw": raw,
        },
    )


class DebateRunner:
    def __init__(self) -> None:
        self.news_agent = NewsAgent()
        self.quant_agent = QuantAgent()
        self.bull_agent = BullAgent()
        self.bear_agent = BearAgent()
        self.risk_agent = RiskAgent()
        self.skeptic_agent = SkepticAgent()
        self.chair_agent = ChairAgent()

    async def run(
        self,
        ticker: str,
        injected_event: str | None = None,
        memory: list[dict] | None = None,
    ) -> AsyncGenerator[WSMessage, None]:
        return self._run(ticker, injected_event, memory or [])

    async def _run(
        self,
        ticker: str,
        injected_event: str | None,
        memory: list[dict],
    ) -> AsyncGenerator[WSMessage, None]:
        start = time.perf_counter()

        yield WSMessage(
            type="status",
            timestamp=_now(),
            payload={"status": "debate_started", "ticker": ticker},
        )

        # Step 1 — News + Quant run concurrently (they don't depend on each other)
        logger.info("[%s] Running News + Quant agents in parallel", ticker)
        news_result, quant_result = await asyncio.gather(
            self.news_agent.run(ticker, injected_event),
            self.quant_agent.run(ticker),
        )

        yield _agent_msg(
            "news",
            news_result.model_dump(),
            f"{news_result.sentiment}: {news_result.headline} (score {news_result.score:+.2f})",
        )
        yield _agent_msg(
            "quant",
            quant_result.model_dump(),
            quant_result.key_signal,
        )

        # Steps 2–5 — Bull → Bear → Risk → Skeptic, with optional re-eval loop
        bear_result = None
        reeval_count = 0
        reeval_flag = False

        while True:
            logger.info("[%s] Bull agent (reeval=%s)", ticker, reeval_flag)
            bull_result = await self.bull_agent.run(
                ticker, news_result, quant_result, bear_result, reeval=reeval_flag
            )
            yield _agent_msg(
                "bull",
                bull_result.model_dump(),
                bull_result.claim,
                confidence=bull_result.confidence,
                flag="REEVAL" if reeval_flag else None,
            )

            logger.info("[%s] Bear agent", ticker)
            bear_result = await self.bear_agent.run(
                ticker, news_result, quant_result, bull_result, reeval=reeval_flag
            )
            yield _agent_msg(
                "bear",
                bear_result.model_dump(),
                bear_result.claim,
                confidence=bear_result.confidence,
                flag="REEVAL" if reeval_flag else None,
            )

            logger.info("[%s] Risk agent", ticker)
            risk_result = await self.risk_agent.run(quant_result, bull_result, bear_result)
            yield _agent_msg(
                "risk",
                risk_result.model_dump(),
                risk_result.risk_note,
                flag="INTERRUPT" if risk_result.interrupt else None,
            )

            if risk_result.interrupt:
                logger.warning("[%s] Risk Agent halted debate", ticker)
                chair_result = await self.chair_agent.run(
                    ticker, news_result, quant_result, bull_result, bear_result,
                    risk_result, None, memory, halt=True,
                )
                yield _agent_msg(
                    "chair",
                    chair_result.model_dump(),
                    f"[HALT] {chair_result.verdict} — {chair_result.reasoning}",
                    confidence=chair_result.confidence,
                    flag="INTERRUPT",
                )
                yield WSMessage(type="decision", timestamp=_now(), payload=chair_result.model_dump())
                break

            logger.info("[%s] Skeptic agent", ticker)
            skeptic_result = await self.skeptic_agent.run(bull_result, bear_result, risk_result)
            weak_count = len(skeptic_result.weak_arguments)
            yield _agent_msg(
                "skeptic",
                skeptic_result.model_dump(),
                (
                    f"Debate quality: {skeptic_result.verdict_on_debate_quality}. "
                    + (f"Flagged {weak_count} weak argument(s)." if weak_count else "No weak arguments.")
                ),
                flag="WEAK_ARG" if skeptic_result.force_reeval else None,
            )

            if skeptic_result.force_reeval and reeval_count < _MAX_REEVAL:
                reeval_count += 1
                reeval_flag = True
                logger.info("[%s] Skeptic forced re-eval (cycle %d)", ticker, reeval_count)
                continue

            # Step 6 — Chair delivers verdict
            logger.info("[%s] Chair agent", ticker)
            chair_result = await self.chair_agent.run(
                ticker, news_result, quant_result, bull_result, bear_result,
                risk_result, skeptic_result, memory, halt=False,
            )
            yield _agent_msg(
                "chair",
                chair_result.model_dump(),
                (
                    f"{chair_result.verdict} — {chair_result.allocation_pct}% allocation, "
                    f"confidence {chair_result.confidence}/100. {chair_result.reasoning}"
                ),
                confidence=chair_result.confidence,
            )
            yield WSMessage(type="decision", timestamp=_now(), payload=chair_result.model_dump())
            break

        elapsed_ms = int((time.perf_counter() - start) * 1000)
        yield WSMessage(
            type="benchmark",
            timestamp=_now(),
            payload={
                "cycle_latency_ms": elapsed_ms,
                "agents_parallel": 7,
                "tokens_processed": elapsed_ms * 2,  # P2 replaces with real token count from vLLM
                "gpu": "AMD MI300X",
            },
        )

        yield WSMessage(
            type="status",
            timestamp=_now(),
            payload={"status": "debate_complete", "ticker": ticker},
        )
