# Quorum — Autonomous Investment War Room

A live autonomous investment committee powered by 7 specialized AI agents that debate, disagree, and make investment decisions in real time.

**Hackathon:** AMD Developer Cloud — Track 1: AI Agents & Agentic Workflows  
**Team:** 4 people, 2 days  
**Demo:** Type a ticker → 7 agents argue → inject breaking news → Chair delivers a verdict in under 90 seconds

---

## What it does

A user inputs a ticker (e.g. `TSLA`). Seven agents fire in sequence:

1. **News Agent** — fetches the most market-moving headline, scores sentiment
2. **Quant Agent** — interprets price, RSI, volatility, momentum
3. **Bull Agent** — argues aggressively for the investment, rebuts Bear by name
4. **Bear Agent** — argues against, attacks Bull's weakest evidence point
5. **Risk Agent** — can halt the debate if drawdown risk exceeds threshold
6. **Skeptic Agent** — flags weak arguments, can force a re-evaluation round
7. **Chair Agent** — synthesises everything into a structured verdict

All agent outputs stream to the frontend via WebSocket in real time. Mid-debate, a "breaking news" event can be injected — the system re-evaluates and the Chair's verdict changes.

---

## Team & ownership

| Person | Role | Owns |
|--------|------|------|
| **P1** | Agent Engineer | `backend/agents/`, `backend/debate_runner.py` |
| **P2** | Data & Infra | `backend/data/fetcher.py`, Redis memory, AMD Cloud |
| **P3** | Backend | `backend/app/`, FastAPI WebSocket, `/inject` endpoint |
| **P4** | Frontend | React war room UI, WebSocket consumer |

---

## Repository layout

```
Quorum/
  backend/                  FastAPI + agent engine
    agents/                 7 agent implementations + shared schemas
    data/                   Market data fetcher (mock → real)
    app/                    FastAPI app, WebSocket server
    debate_runner.py        Debate orchestration (async generator)
    cli_test.py             P1 smoke test — runs a full debate in terminal
  docs/
    websocket_schema.md     WS message contract between P3 and P4
  WarRoom_ProjectPlan.md    Full project plan and day-by-day tickets
  WarRoom_TechSpec.md       Agent prompts, schemas, component specs
  WarRoom_Storyboard.md     Per-person ticket breakdown
```

---

## Quick start — by role

### P1 — Agent Engineer

```bash
cd backend
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env          # fill in LLM_API_KEY
python cli_test.py TSLA
python cli_test.py NVDA --inject "CEO resigns effective immediately"
```

See [backend/AGENT_ARCHITECTURE.md](backend/AGENT_ARCHITECTURE.md) for the full debate flow and tuning guide.

### P2 — Data & Infrastructure

1. Implement `get_news(ticker)` and `get_quant(ticker)` in `backend/data/fetcher.py`  
   (replace mock data with real NewsAPI + yfinance calls — interface contract must not change)
2. Provision AMD MI300X on AMD Developer Cloud, deploy Llama 3.1 70B via vLLM
3. Update `.env`: set `LLM_BASE_URL`, `LLM_API_KEY`, `LLM_MODEL` to the AMD endpoint
4. Spin up Redis: `docker run -d -p 6379:6379 redis`
5. Expose benchmark data via `GET /benchmark/{session_id}`

### P3 — Backend

```bash
cd backend
source .venv/bin/activate
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Wire `DebateRunner` into the WebSocket endpoint:
```python
from debate_runner import DebateRunner

runner = DebateRunner()
async for msg in await runner.run(ticker):
    await websocket.send_json(msg.model_dump())
```

See [docs/websocket_schema.md](docs/websocket_schema.md) for the full message contract.

### P4 — Frontend

```bash
cd frontend          # (scaffold pending)
npm install
npm run dev
```

WebSocket connects to `ws://localhost:8000/ws/{session_id}` after `POST /analyze`.  
See [docs/websocket_schema.md](docs/websocket_schema.md) for message shapes.

---

## LLM configuration

The agent engine uses the `openai` Python SDK with a configurable endpoint — switching from the DeepSeek fallback to AMD vLLM requires only env var changes, no code changes.

| Env var | Fallback (now) | AMD (when ready) |
|---------|---------------|-----------------|
| `LLM_BASE_URL` | `https://api.deepseek.com` | `http://YOUR_MI300X/v1` |
| `LLM_API_KEY` | DeepSeek API key | AMD token |
| `LLM_MODEL` | `deepseek-chat` | `llama-3.1-70b` |

---

## Key documents

| Document | Purpose |
|----------|---------|
| [WarRoom_ProjectPlan.md](WarRoom_ProjectPlan.md) | Day-by-day plan, all tickets, risk register |
| [WarRoom_TechSpec.md](WarRoom_TechSpec.md) | Agent prompts, schemas, frontend component spec |
| [WarRoom_Storyboard.md](WarRoom_Storyboard.md) | Per-person ticket storyboard |
| [backend/AGENT_ARCHITECTURE.md](backend/AGENT_ARCHITECTURE.md) | Debate flow, integration contracts, tuning guide |
| [docs/websocket_schema.md](docs/websocket_schema.md) | WebSocket message schema (P3 ↔ P4 contract) |
