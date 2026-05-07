from __future__ import annotations

import json
import logging
import os

from openai import AsyncOpenAI

logger = logging.getLogger("quorum.agents")

_client: AsyncOpenAI | None = None


def get_client() -> AsyncOpenAI:
    global _client
    if _client is None:
        _client = AsyncOpenAI(
            base_url=os.environ.get("LLM_BASE_URL", "https://api.deepseek.com"),
            api_key=os.environ.get("LLM_API_KEY", ""),
        )
    return _client


LLM_MODEL = os.environ.get("LLM_MODEL", "deepseek-chat")


class BaseAgent:
    role: str = ""
    goal: str = ""
    backstory: str = ""

    async def _call(self, task: str, temperature: float = 0.7) -> dict:
        system = (
            f"You are {self.role}.\n\n"
            f"Goal: {self.goal}\n\n"
            f"Background: {self.backstory}\n\n"
            "You must respond with valid JSON only. "
            "No markdown code blocks, no explanation outside the JSON object."
        )
        client = get_client()
        response = await client.chat.completions.create(
            model=LLM_MODEL,
            messages=[
                {"role": "system", "content": system},
                {"role": "user", "content": task},
            ],
            response_format={"type": "json_object"},
            temperature=temperature,
        )
        raw = response.choices[0].message.content
        logger.debug("[%s] raw output: %s", self.role, raw[:200])
        return json.loads(raw)
