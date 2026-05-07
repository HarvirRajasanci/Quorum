# Agent Architecture

P1 reference document — debate flow, agent specs, integration contracts, tuning guide.

---

## Debate flow

```
                    ┌─────────┐   ┌──────────┐
                    │  News   │   │  Quant   │   (run concurrently)
                    └────┬────┘   └────┬─────┘
                         └──────┬──────┘
                                ▼
                    ┌───────────────────────┐
                    │  Bull  ◄──── Bear     │   (Bull first, Bear rebuts)
                    └───────────┬───────────┘
                                │
                                ▼
                          ┌───────────┐
                          │   Risk    │
                          └─────┬─────┘
                                │
                    interrupt?  │  no interrupt
                        ┌───────┴────────┐
                        ▼                ▼
                   ┌─────────┐     ┌──────────┐
                   │  Chair  │     │ Skeptic  │
                   │ (HALT)  │     └────┬─────┘
                   └────┬────┘          │
                        │    force_reeval? ──► restart Bull/Bear (max 1×)
                        │         │ no
                        │         ▼
                        │    ┌─────────┐
                        └───►│  Chair  │
                             └─────────┘
```

Each node yields a `WSMessage` to the frontend the moment it completes.

---

## Agent I/O reference

### News Agent

**Input:** ticker (str), optional injected_event (str)  
**Output:** `SentimentObject`

```python
{
  "headline": str,
  "source": str,
  "sentiment": "BULLISH" | "BEARISH" | "NEUTRAL",
  "score": float,          # -1.0 to 1.0
  "reasoning": str
}
```

**Tuning notes:** Low temperature (0.3). Prioritise specificity — "Tesla Q2 deliveries miss by 8%" beats "Tesla faces challenges". If injected_event is set, it becomes headline #1.

---

### Quant Agent

**Input:** ticker (str)  
**Output:** `QuantObject`

```python
{
  "price": float,
  "change_pct": float,
  "rsi": float,
  "volatility": "LOW" | "MEDIUM" | "HIGH",
  "momentum": "BULLISH" | "BEARISH" | "NEUTRAL",
  "key_signal": str        # one sentence with numbers
}
```

**Tuning notes:** Very low temperature (0.2). `volatility` and `momentum` are also enforced by the Quant task prompt rules, so the LLM classification is redundant — but it formats `key_signal` well.

---

### Bull Agent

**Input:** ticker, news (SentimentObject), quant (QuantObject), bear_output (optional), reeval (bool)  
**Output:** `ArgumentObject`

```python
{
  "position": "INVEST",
  "claim": str,            # 1-2 sentences
  "evidence": [str, str, str],
  "rebuttal": str | None,  # must name Bear's weakest point explicitly when bear_output is set
  "confidence": int        # 0-100
}
```

**Tuning notes:** High temperature (0.8) for combativeness. The `rebuttal` field is where most quality issues arise — if it's vague ("Bear's argument is weak"), tighten the prompt to force it to quote Bear's claim verbatim before attacking it.

---

### Bear Agent

**Input:** ticker, news, quant, bull_output (required), reeval (bool)  
**Output:** `ArgumentObject`

```python
{
  "position": "REJECT",
  "claim": str,
  "evidence": [str, str, str],
  "rebuttal": str,         # always set — must name Bull's specific evidence point
  "confidence": int
}
```

**Tuning notes:** Same high temperature (0.8). Bear always has Bull's output, so `rebuttal` is always expected. Weak rebuttals ("Bull's case is optimistic") should be caught by Skeptic and trigger re-eval.

---

### Risk Agent

**Input:** quant (QuantObject), bull (ArgumentObject), bear (ArgumentObject)  
**Output:** `RiskObject`

```python
{
  "drawdown_risk": float,  # 0.0-1.0, LLM estimate
  "interrupt": bool,
  "threshold_breached": bool,
  "risk_note": str
}
```

**Important:** `interrupt` is enforced deterministically in Python after the LLM call:

```python
if quant.volatility == "HIGH" and obj.drawdown_risk > DRAWDOWN_THRESHOLD:
    obj.interrupt = True
```

The LLM cannot hallucinate `interrupt: false` when the hard condition is met. `DRAWDOWN_THRESHOLD` defaults to 0.15, set via `DRAWDOWN_THRESHOLD` env var.

**Tuning notes:** Low temperature (0.2). The note field should be terse and dramatic for the demo — "HIGH volatility breaches 15% drawdown threshold. Halting." not a paragraph.

---

### Skeptic Agent

**Input:** bull (ArgumentObject), bear (ArgumentObject), risk (RiskObject)  
**Output:** `SkepticObject`

```python
{
  "weak_arguments": [
    {"agent": "bull" | "bear", "claim": str, "reason_weak": str}
  ],
  "hallucination_flags": [str],
  "force_reeval": bool,
  "verdict_on_debate_quality": "STRONG" | "ADEQUATE" | "WEAK"
}
```

**Tuning notes:** Medium temperature (0.5). `force_reeval` is only set when quality is genuinely WEAK — too aggressive and the loop spins. Test with intentionally bad inputs (vague claims, made-up statistics) to verify it fires. The `weak_arguments` list must be non-empty for `force_reeval: true` to be meaningful for the demo.

---

### Chair Agent

**Input:** all prior outputs, memory (list of past DecisionObjects), halt (bool)  
**Output:** `DecisionObject`

```python
{
  "verdict": "INVEST" | "HOLD" | "REJECT",
  "allocation_pct": int,   # 0-100
  "confidence": int,       # 0-100
  "risk_level": "LOW" | "MEDIUM" | "HIGH",
  "reasoning": str,        # must cite specific agents by name
  "reeval_seconds": int    # 30 | 60 | 120 | 300
}
```

**Important:** When `halt=True`, `verdict` is forced to `HOLD` or `REJECT` in Python even if the LLM returns `INVEST`. `reeval_seconds` is validated and snapped to the nearest valid value.

**Tuning notes:** Medium temperature (0.5). The `reasoning` field is what judges read — it must cite "Bull Agent argued X, but Bear Agent's rebuttal Y, combined with Risk Agent's drawdown assessment of Z, leads to..." not generic text.

---

## Ticket status

| Ticket | Description | Status |
|--------|-------------|--------|
| P1-01 | CrewAI scaffold → custom DebateRunner scaffold | ✅ Done |
| P1-02 | News Agent | ✅ Done |
| P1-03 | Quant Agent | ✅ Done |
| P1-04 | Bull & Bear Agents | ✅ Done |
| P1-05 | Risk Agent + interrupt logic | ✅ Done |
| P1-06 | Skeptic Agent + re-eval logic | ✅ Done |
| P1-07 | Chair Agent + final decision output | ✅ Done |
| P1-08 | Full debate loop end-to-end test | ⏳ Needs real API key — run `python cli_test.py TSLA` |
| P1-09 | Prompt tuning — debate quality pass | ⏳ Day 2 AM |
| P1-10 | Breaking news injection handling | ✅ Wired — `--inject` flag in CLI, `injected_event` param in DebateRunner |
| P1-11 | Demo dry run + agent QA | ⏳ Day 2 PM with P4 |

---

## Adding real LLM calls (P1-08)

1. Get a DeepSeek API key at [platform.deepseek.com](https://platform.deepseek.com)
2. Add to `.env`: `LLM_API_KEY=sk-...`
3. Run: `python cli_test.py TSLA`

Expected output: 7 agent messages in sequence, ending with a Chair verdict and benchmark stats.

When AMD endpoint is live (P2-00), change three env vars — no code changes needed:
```
LLM_BASE_URL=http://YOUR_AMD_INSTANCE/v1
LLM_API_KEY=your_amd_token
LLM_MODEL=llama-3.1-70b
```

---

## Prompt tuning guide (P1-09)

Run 5 debate cycles and watch for these failure modes:

| Failure | Symptom | Fix |
|---------|---------|-----|
| **Generic rebuttal** | Bear says "Bull's argument lacks substance" without naming evidence | Tighten bear.py prompt: require quoting Bull's evidence item by index |
| **Repetitive arguments** | Two TSLA debates produce identical Bull claims | Increase temperature to 0.85, add "Do not repeat arguments from prior cycles" note |
| **Vague Chair reasoning** | Chair says "weighing all factors" without citing agents | Tighten chair.py: "Your reasoning is invalid if it does not name at least one specific agent claim" |
| **Risk never interrupts** | TSLA (HIGH volatility) never triggers interrupt | Check `DRAWDOWN_THRESHOLD` in `.env`; verify mock quant data has `volatility: "HIGH"` |
| **Skeptic always fires force_reeval** | Every debate restarts | Lower Skeptic temperature to 0.4; add "Only set force_reeval if you find concrete evidence of fabrication or circular logic" |

---

## Debate runner — how to use from P3

```python
from debate_runner import DebateRunner

# Instantiate once at app startup
runner = DebateRunner()

# Normal debate
async for msg in await runner.run("TSLA"):
    await websocket.send_json(msg.model_dump())

# With breaking news injection
async for msg in await runner.run("TSLA", injected_event="CEO resigns"):
    await websocket.send_json(msg.model_dump())

# With Redis memory (P2 provides the memory list)
past_decisions = redis_memory.read("TSLA")   # list of DecisionObject dicts
async for msg in await runner.run("TSLA", memory=past_decisions):
    await websocket.send_json(msg.model_dump())
```

`WSMessage` types the runner yields, in order:

| Type | When | Key payload fields |
|------|------|--------------------|
| `status` | Start of debate | `status: "debate_started"`, `ticker` |
| `agent_message` | After each agent | `agent`, `content`, `confidence`, `flag`, `raw` |
| `decision` | After Chair | Full `DecisionObject` fields |
| `benchmark` | After decision | `cycle_latency_ms`, `agents_parallel`, `gpu` |
| `status` | End of debate | `status: "debate_complete"` |

The `flag` field on `agent_message`:
- `"INTERRUPT"` — Risk Agent halted the debate (red border in UI)
- `"WEAK_ARG"` — Skeptic flagged weak arguments (amber border)
- `"REEVAL"` — Bull/Bear are on a re-evaluation round (amber border)
- `null` — normal message
