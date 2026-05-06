from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class SessionState:
    session_id: str
    ticker: str
    status: str = "started"
    messages: list[dict[str, Any]] = field(default_factory=list)
    benchmark: dict[str, Any] | None = None


class SessionManager:
    def __init__(self) -> None:
        self._sessions: dict[str, SessionState] = {}

    def create_session(self, session_id: str, ticker: str) -> SessionState:
        state = SessionState(session_id=session_id, ticker=ticker)
        self._sessions[session_id] = state
        return state

    def get_session(self, session_id: str) -> SessionState | None:
        return self._sessions.get(session_id)

    def mark_completed(self, session_id: str) -> None:
        state = self.get_session(session_id)
        if state:
            state.status = "completed"

    def mark_failed(self, session_id: str, error: str) -> None:
        state = self.get_session(session_id)
        if state:
            state.status = "failed"
            state.messages.append(
                {
                    "type": "error",
                    "payload": {
                        "session_id": session_id,
                        "code": "AGENT_RUN_FAILED",
                        "message": error,
                        "recoverable": True,
                    },
                }
            )