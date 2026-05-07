# War Room Backend

FastAPI backend + agent engine for the Quorum War Room.

**P3 owns** `app/` (FastAPI, WebSocket server, endpoints).  
**P1 owns** `agents/`, `debate_runner.py` (all agent logic).  
**P2 owns** `data/fetcher.py` (market data), Redis, AMD Cloud.

---

## Setup

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env       # then fill in secrets — never commit .env
```

---

## Running

### FastAPI server (P3)

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Health check: `curl localhost:8000/health` → `{"status": "ok"}`

### Agent CLI smoke test (P1)

```bash
python cli_test.py TSLA
python cli_test.py NVDA
python cli_test.py AAPL
python cli_test.py TSLA --inject "CEO resigns effective immediately"
```

Runs the full 7-agent debate in the terminal with coloured output. No server required.

---

## Environment variables

Copy `.env.example` to `.env` and fill in secrets. All required vars:

```bash
# LLM — swap to AMD when P2 provisions the instance (no code changes needed)
LLM_BASE_URL=https://api.deepseek.com    # or http://AMD_ENDPOINT/v1
LLM_API_KEY=your_key_here
LLM_MODEL=deepseek-chat                  # or llama-3.1-70b

# Market data (P2)
NEWS_API_KEY=your_newsapi_key

# Redis (P2)
REDIS_URL=redis://localhost:6379

# Debate config
DRAWDOWN_THRESHOLD=0.15
MAX_DEBATE_CYCLES=3
```

---

## Directory structure

```
backend/
  agents/
    schemas.py          Pydantic models for all agent I/O and WebSocket messages
    base.py             LLM client (openai SDK) + BaseAgent class
    news.py             NewsAgent
    quant.py            QuantAgent
    bull.py             BullAgent
    bear.py             BearAgent
    risk.py             RiskAgent
    skeptic.py          SkepticAgent
    chair.py            ChairAgent
  data/
    fetcher.py          get_news() + get_quant() — mock now, P2 replaces with real APIs
  app/
    main.py             FastAPI app, /health, /analyze endpoints
    schemas.py          Request/response models for HTTP endpoints
    session_manager.py  In-memory session state
  debate_runner.py      Debate orchestration — async generator, yields WSMessage
  cli_test.py           Terminal smoke test for P1
  requirements.txt
  .env.example
```

---

## P3 integration — wiring the debate to WebSocket

`DebateRunner.run()` is an async generator. Each `await` inside it resolves one agent call, and the generator immediately `yield`s a `WSMessage` — so the frontend gets each agent's output the moment it finishes, not after the whole debate.

```python
from debate_runner import DebateRunner

runner = DebateRunner()   # instantiate once at app startup, re-use across requests

# Inside your WebSocket handler:
async for msg in await runner.run(ticker, injected_event=None, memory=[]):
    await websocket.send_json(msg.model_dump())
```

For the `/inject` endpoint, pass the event string:

```python
async for msg in await runner.run(ticker, injected_event="CEO resigns"):
    await websocket.send_json(msg.model_dump())
```

The `WSMessage` shape every message follows:

```json
{
  "type": "agent_message" | "decision" | "status" | "benchmark" | "error",
  "timestamp": "2026-05-07T10:00:00+00:00",
  "payload": { ... }
}
```

Full schema: [docs/websocket_schema.md](../docs/websocket_schema.md)

---

## P2 integration — replacing the mock data fetcher

`data/fetcher.py` currently returns hardcoded data for TSLA, NVDA, AAPL. P2 replaces the two functions with real implementations. **The interface contract must not change** — agents depend on it.

```python
def get_news(ticker: str) -> list[dict]:
    # Must return a list of dicts, each with 'title' (str) and 'source' (str)
    # Aim for 5 items; fewer is fine; empty list falls back gracefully
    ...

def get_quant(ticker: str) -> dict:
    # Must return a dict with these keys (types must match):
    # price: float, change_pct: float, rsi: float,
    # volatility: "LOW"|"MEDIUM"|"HIGH", momentum: "BULLISH"|"BEARISH"|"NEUTRAL",
    # volume: int
    ...
```

P2 should also add retry + cache fallback as documented in ticket P2-07.

---

## Dependencies

| Package | Purpose |
|---------|---------|
| `fastapi` | HTTP + WebSocket server |
| `uvicorn` | ASGI server |
| `pydantic` | Agent I/O validation, schema enforcement |
| `openai` | LLM client (works with DeepSeek, AMD vLLM, OpenAI) |
| `python-dotenv` | `.env` loading |
| `redis` | Agent memory (past decisions per ticker) |
