from __future__ import annotations

from pydantic import BaseModel, Field, field_validator


class AnalyzeRequest(BaseModel):
    ticker: str = Field(..., min_length=1, max_length=10)

    @field_validator("ticker")
    @classmethod
    def normalize_ticker(cls, value: str) -> str:
        ticker = value.strip().upper()

        if not ticker:
            raise ValueError("ticker cannot be empty")

        if ticker.isnumeric():
            raise ValueError("ticker cannot be numeric only")

        if not ticker.replace(".", "").replace("-", "").isalnum():
            raise ValueError("ticker may only contain letters, numbers, dots, or hyphens")

        return ticker


class AnalyzeResponse(BaseModel):
    session_id: str
    status: str = "started"