from __future__ import annotations

import logging
import time
from uuid import uuid4

from fastapi import BackgroundTasks, FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.schemas import AnalyzeRequest, AnalyzeResponse
from app.session_manager import SessionManager

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("quorum.backend")

app = FastAPI(title="Quorum Backend")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Tighten later if needed
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

sessions = SessionManager()


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


async def run_debate_background(session_id: str, ticker: str) -> None:
    """
    Placeholder background job.

    This intentionally does not run the real CrewAI debate yet.
    Later, this function should call P1's real debate runner.
    """
    logger.info("Background debate started: session_id=%s ticker=%s", session_id, ticker)

    try:
        # Simulate a tiny amount of background work so we can verify
        # that /analyze returns immediately and work continues after response.
        time.sleep(0.1)

        state = sessions.get_session(session_id)
        if state:
            state.messages.append(
                {
                    "type": "status",
                    "payload": {
                        "session_id": session_id,
                        "ticker": ticker,
                        "status": "debate_started",
                        "message": f"Debate started for {ticker}",
                    },
                }
            )

        sessions.mark_completed(session_id)
        logger.info("Background debate completed: session_id=%s ticker=%s", session_id, ticker)

    except Exception as exc:
        logger.exception("Background debate failed: session_id=%s ticker=%s", session_id, ticker)
        sessions.mark_failed(session_id, str(exc))


@app.post("/analyze", response_model=AnalyzeResponse)
async def analyze(
    request: AnalyzeRequest,
    background_tasks: BackgroundTasks,
) -> AnalyzeResponse:
    """
    Start a debate session.
    - Accept {ticker: str}
    - Generate uuid4 session_id
    - Start debate in FastAPI BackgroundTasks
    - Return immediately with {session_id, status: "started"}
    """
    session_id = str(uuid4())
    ticker = request.ticker

    sessions.create_session(session_id=session_id, ticker=ticker)

    background_tasks.add_task(run_debate_background, session_id, ticker)

    logger.info("Created analysis session: session_id=%s ticker=%s", session_id, ticker)

    return AnalyzeResponse(session_id=session_id, status="started")