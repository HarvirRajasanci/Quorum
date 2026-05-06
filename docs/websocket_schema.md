# War Room WebSocket Schema Contract

Ticket: P3-00  
Owners: P3 Backend + P4 Frontend  
Status: Pending P3/P4 sign-off

This document defines the WebSocket message contract between the FastAPI backend and the React frontend.

P3 and P4 should agree to this document before implementing WebSocket-dependent code.

---

## WebSocket Endpoint

```txt
ws://localhost:8000/ws/{session_id}
```

The frontend should open this WebSocket after calling:

```txt
POST /analyze
```

and receiving:

```json
{
  "session_id": "uuid-string",
  "status": "started"
}
```

---

## Global Message Envelope

Every WebSocket message MUST be a JSON object with this top-level shape:

```json
{
  "type": "agent_message",
  "timestamp": "2026-05-05T14:32:01Z",
  "payload": {}
}
```

### Top-level fields

| Field       |   Type | Required | Notes                                                              |
| ----------- | -----: | -------: | ------------------------------------------------------------------ |
| `type`      | string |      yes | One of `status`, `agent_message`, `decision`, `benchmark`, `error` |
| `timestamp` | string |      yes | ISO 8601 UTC timestamp                                             |
| `payload`   | object |      yes | Shape depends on `type`                                            |

Do not put agent fields such as `agent`, `content`, `confidence`, or `flag` at the top level. They belong inside `payload`.

---

## Message Type: `status`

Used for lifecycle updates such as debate start, completion, injection, and re-evaluation.

```json
{
  "type": "status",
  "timestamp": "2026-05-05T14:32:01Z",
  "payload": {
    "session_id": "uuid-string",
    "ticker": "TSLA",
    "status": "debate_started",
    "message": "Debate started for TSLA"
  }
}
```

### Payload fields

| Field        |   Type | Required | Notes                           |
| ------------ | -----: | -------: | ------------------------------- |
| `session_id` | string |      yes | Backend-generated UUID          |
| `ticker`     | string |       no | Uppercase ticker when available |
| `status`     | string |      yes | Machine-readable status         |
| `message`    | string |      yes | Human-readable status message   |

### Allowed `payload.status` values

```txt
debate_started
debate_completed
injection_received
reevaluation_scheduled
reevaluation_started
```

### Note

The Tech Spec lists `status` as a valid top-level `type`, but does not fully define the `status.payload` shape. This document defines it for P3/P4 integration.

---

## Message Type: `agent_message`

Used whenever one agent completes and emits an update for the debate stream.

```json
{
  "type": "agent_message",
  "timestamp": "2026-05-05T14:32:01Z",
  "payload": {
    "agent": "bull",
    "content": "Bull argues upside based on strong momentum and improving margins.",
    "confidence": 72,
    "flag": null,
    "raw": {
      "position": "INVEST",
      "claim": "The market is underpricing upside from momentum and positive news.",
      "evidence": [
        "Positive headline sentiment",
        "RSI remains constructive",
        "Momentum is bullish"
      ],
      "rebuttal": null,
      "confidence": 72
    }
  }
}
```

### Payload fields

| Field        |            Type | Required | Notes                                      |
| ------------ | --------------: | -------: | ------------------------------------------ |
| `agent`      |          string |      yes | Lowercase agent ID                         |
| `content`    |          string |      yes | Human-readable summary for the UI          |
| `confidence` | integer or null |      yes | `0-100`; `null` for `news` and `quant`     |
| `flag`       |  string or null |      yes | Special visual/event flag                  |
| `raw`        |          object |      yes | Full structured JSON output from the agent |

### Allowed `payload.agent` values

```txt
news
quant
bull
bear
risk
skeptic
chair
```

### Allowed `payload.flag` values

```txt
null
INTERRUPT
WEAK_ARG
REEVAL
```

### Agent stream order

For a normal debate cycle, backend should stream agents in this order:

```txt
news -> quant -> bull -> bear -> risk -> skeptic -> chair
```

---

## Message Type: `decision`

Used for the final Chair decision.

```json
{
  "type": "decision",
  "timestamp": "2026-05-05T14:32:01Z",
  "payload": {
    "verdict": "HOLD",
    "allocation_pct": 35,
    "confidence": 68,
    "risk_level": "MEDIUM",
    "reasoning": "The upside case is credible, but Bear and Risk flagged valuation and volatility concerns.",
    "reeval_seconds": 30
  }
}
```

### Payload fields

| Field            |    Type | Required | Notes                                                      |
| ---------------- | ------: | -------: | ---------------------------------------------------------- |
| `verdict`        |  string |      yes | One of `INVEST`, `HOLD`, `REJECT`                          |
| `allocation_pct` | integer |      yes | `0-100`                                                    |
| `confidence`     | integer |      yes | `0-100`                                                    |
| `risk_level`     |  string |      yes | One of `LOW`, `MEDIUM`, `HIGH`                             |
| `reasoning`      |  string |      yes | Human-readable Chair rationale                             |
| `reeval_seconds` | integer |      yes | Delay before automatic re-evaluation; `0` means no re-eval |

### Allowed `payload.verdict` values

```txt
INVEST
HOLD
REJECT
```

### Allowed `payload.risk_level` values

```txt
LOW
MEDIUM
HIGH
```

---

## Message Type: `benchmark`

Sent after the Chair decision.

```json
{
  "type": "benchmark",
  "timestamp": "2026-05-05T14:32:01Z",
  "payload": {
    "cycle_latency_ms": 12345,
    "agents_parallel": 7,
    "tokens_processed": 1200,
    "gpu": "AMD MI300X"
  }
}
```

### Payload fields

| Field              |    Type | Required | Notes                                |
| ------------------ | ------: | -------: | ------------------------------------ |
| `cycle_latency_ms` | integer |      yes | Real measured backend cycle duration |
| `agents_parallel`  | integer |      yes | Use `7` for demo                     |
| `tokens_processed` | integer |      yes | May be estimated from output length  |
| `gpu`              |  string |      yes | Use `"AMD MI300X"`                   |

---

## Message Type: `error`

Used when backend cannot complete a requested action or debate cycle.

```json
{
  "type": "error",
  "timestamp": "2026-05-05T14:32:01Z",
  "payload": {
    "session_id": "uuid-string",
    "code": "AGENT_RUN_FAILED",
    "message": "AMD endpoint unreachable. Debate could not complete.",
    "recoverable": true
  }
}
```

### Payload fields

| Field         |    Type | Required | Notes                                       |
| ------------- | ------: | -------: | ------------------------------------------- |
| `session_id`  |  string |       no | Include when available                      |
| `code`        |  string |      yes | Machine-readable error code                 |
| `message`     |  string |      yes | Human-readable error                        |
| `recoverable` | boolean |      yes | Whether frontend can keep the session alive |

### Suggested error codes

```txt
INVALID_SESSION
INVALID_TICKER
AGENT_RUN_FAILED
AMD_ENDPOINT_UNREACHABLE
WEBSOCKET_DISCONNECTED
INJECTION_FAILED
UNKNOWN_ERROR
```

### Note

The Tech Spec lists `error` as a valid top-level `type`, but does not fully define the `error.payload` shape. This document defines it for P3/P4 integration.

---

## REST API Contracts Relevant to WebSocket Flow

### `GET /health`

Response:

```json
{
  "status": "ok"
}
```

---

### `POST /analyze`

Request:

```json
{
  "ticker": "TSLA"
}
```

Response:

```json
{
  "session_id": "uuid-string",
  "status": "started"
}
```

Behavior:

1. Validate ticker.
2. Create a new `session_id`.
3. Start debate in the background.
4. Return immediately.
5. Frontend connects to `/ws/{session_id}`.

---

### `POST /inject`

Request:

```json
{
  "session_id": "uuid-string",
  "event": "CEO Resigns"
}
```

Response:

```json
{
  "status": "injected"
}
```

Behavior:

1. Find active session.
2. Add injected event to debate context.
3. Trigger new debate messages.
4. Stream new messages over the existing WebSocket connection.

---

### `GET /memory/{ticker}`

Response:

```json
{
  "ticker": "TSLA",
  "decisions": [],
  "confidence_history": []
}
```

Unknown tickers should return empty arrays, not `404`.

---

### `GET /benchmark/{session_id}`

Response after benchmark exists:

```json
{
  "cycle_latency_ms": 12345,
  "agents_parallel": 7,
  "tokens_processed": 1200,
  "gpu": "AMD MI300X"
}
```

---

## P4 Rendering Expectations

| Message type    | Frontend behavior                                                                    |
| --------------- | ------------------------------------------------------------------------------------ |
| `status`        | Render as small system line or update session state                                  |
| `agent_message` | Append `payload` to debate stream; update confidence meter if confidence is not null |
| `decision`      | Update DecisionCard, AllocationBar, and ReevalTimer                                  |
| `benchmark`     | Update BenchmarkPanel                                                                |
| `error`         | Show visible error toast/card                                                        |

---

## Intentional Behavior Decision: WebSocket Lifetime

P3-03 says the WebSocket should close cleanly after the Chair message.

P3-04 and P3-07 require injected and re-evaluation messages to stream over the existing WebSocket connection.

For the demo, P3/P4 agree to keep the WebSocket open after the Chair decision so that:

1. `/inject` can stream new messages into the same session.
2. re-evaluation cycles can stream into the same session.
3. the frontend does not need to reconnect after every decision.

The backend should send:

```json
{
  "type": "status",
  "timestamp": "2026-05-05T14:32:01Z",
  "payload": {
    "session_id": "uuid-string",
    "ticker": "TSLA",
    "status": "debate_completed",
    "message": "Debate completed for TSLA"
  }
}
```

instead of closing immediately.

If P4 prefers strict close-after-Chair behavior, document that here before implementing P3-03.

---

## Sign-off Checklist

P3 and P4 agree that:

- [ ] Every WebSocket message uses `type`, `timestamp`, and `payload`
- [ ] Agent IDs are lowercase: `news`, `quant`, `bull`, `bear`, `risk`, `skeptic`, `chair`
- [ ] Agent confidence is `0-100`, with `null` for `news` and `quant`
- [ ] Frontend reads renderable data from `payload`, not top-level fields
- [ ] `decision.payload` updates the DecisionCard, AllocationBar, and ReevalTimer
- [ ] `benchmark.payload` updates the BenchmarkPanel
- [ ] `error.payload` is shown visibly in the UI
- [ ] WebSocket remains open after Chair unless this document is updated
- [ ] Any deviations from Tech Spec Section 3 are documented in this file

P3 sign-off:

```txt
Name:
Date:
Notes:
```

P4 sign-off:

```txt
Name:
Date:
Notes:
```
