**Autonomous Investment War Room**

Hackathon Project Plan — Track 1: AI Agents & Agentic Workflows

AMD Developer Cloud  |  CrewAI  |  2 Days  |  4 People

# **1\. Project Overview**

A live autonomous investment committee powered by 7 specialized AI agents that debate, disagree, and make investment decisions in real time. This is not a chatbot. It is a living system — agents challenge each other's reasoning, update confidence scores as new data arrives, and react instantly to breaking news events injected mid-debate.

The demo is the pitch. A judge types a ticker. Seven agents argue. A breaking news event fires. The system adapts. A verdict is delivered with a portfolio allocation and confidence score — all in under 90 seconds.

*"This isn't a chatbot. This is an autonomous investment committee — 7 agents with conflicting goals, real data, and memory — making decisions under uncertainty in real time. The same process that takes a human committee 3 hours takes this system 90 seconds."*

## **Track Fit**

* Objective: Multi-agent system automating a complex decision-making workflow

* Tech stack: CrewAI \+ Llama 3.1 70B / DeepSeek-V3 \+ AMD Developer Cloud

* AMD angle: 7 agents running in parallel on MI300X, sub-2s decision cycles, live benchmark panel

* Differentiator: Real agent conflict, evolving memory, live data, and a Bloomberg-style war room UI

# **2\. The 7 Agents**

Each agent has a distinct role, goal, and personality. Agents reference each other's arguments directly and can challenge, agree, or interrupt. The Skeptic Agent adds a meta-layer — detecting weak reasoning and forcing re-evaluation before the Chair decides.

| Agent | Role | Goal |
| :---- | :---- | :---- |
| **News Agent** | Fetches breaking financial news and market sentiment in real time | Surface relevant events that change the investment thesis |
| **Quant Agent** | Analyzes price volatility, momentum indicators, and technical signals | Ground the debate in quantitative data |
| **Bull Agent** | Argues aggressively for the investment with supporting evidence | Present the strongest possible bull case |
| **Bear Agent** | Argues against the investment, challenges bull claims directly | Surface every risk and counterargument |
| **Risk Agent** | Monitors drawdown thresholds and exposure limits | Interrupt and halt the debate when risk exceeds threshold |
| **Skeptic Agent** | Detects weak arguments and potential hallucinations | Force re-evaluation of poorly reasoned claims |
| **Chair Agent** | Synthesizes all agent arguments into a final decision | Deliver a verdict with confidence score and allocation |

# **3\. System Architecture**

## **Data Flow**

* User inputs a ticker symbol (e.g. TSLA) via the frontend

* Backend triggers the CrewAI debate loop — all 7 agents fire

* News Agent fetches live headlines. Quant Agent fetches price and technicals

* Bull and Bear agents receive shared context and argue in sequence

* Risk and Skeptic agents can interrupt at any point in the loop

* Chair synthesizes and produces a structured decision object

* All messages stream via WebSocket to the frontend in real time

* Breaking news events can be injected mid-debate, restarting the cycle

## **Tech Stack**

| Layer | Technology | Purpose |
| :---- | :---- | :---- |
| **Agent Framework** | CrewAI | Multi-agent orchestration, role definitions, inter-agent communication |
| **LLM** | Llama 3.1 70B or DeepSeek-V3 | Core reasoning for all 7 agents |
| **Compute** | AMD MI300X via AMD Developer Cloud | Parallel agent inference at low latency |
| **Backend** | FastAPI \+ WebSockets | Real-time agent message streaming to frontend |
| **Memory** | Redis | Agent confidence scores, decision history, past positions |
| **Market Data** | Yahoo Finance API \+ NewsAPI | Live price data and financial news feed |
| **Frontend** | React \+ Tailwind | Bloomberg-style war room dashboard |

# **4\. Build Plan**

## **Day 1 — Build the Engine**

Goal: Type a ticker into the terminal and watch 7 agents debate, disagree, and reach a decision — even if the UI is ugly. The engine must work before touching design.

**Team split for day 1:**

* Person 1 (P1) — CrewAI agent setup: all 7 agents, roles, goals, inter-agent communication, debate loop logic

* Person 2 (P2) — Data pipelines: Yahoo Finance, NewsAPI, AMD cloud setup, Redis memory layer

* Person 3 (P3) — FastAPI backend, WebSocket server, /analyze and /inject endpoints

* Person 4 (P4) — Frontend scaffold: React app structure, WebSocket connection, basic message display

**End-of-day milestone: Input 'TSLA' in CLI. All 7 agents fire. Chair produces Invest/Hold/Reject with confidence score. Messages stream to basic frontend.**

## **Day 1 Tickets**

| Ticket ID | Title | Description | Owner | Priority |
| :---- | :---- | :---- | :---- | :---- |
| D1-01 | **AMD Cloud setup & model deploy** | Provision MI300X instance on AMD Developer Cloud. Deploy Llama 3.1 70B or DeepSeek-V3 via vLLM. Confirm inference endpoint is live. | P2 | **P0** |
| D1-02 | **CrewAI project scaffold** | Initialize CrewAI project. Define base Agent class. Set up config files for all 7 agent roles. Confirm agents can be instantiated. | P1 | **P0** |
| D1-03 | **News Agent implementation** | Wire NewsAPI or Alpaca to News Agent. Agent fetches headlines for a given ticker and summarizes sentiment. Output: structured sentiment object. | P1 | **P0** |
| D1-04 | **Quant Agent implementation** | Wire Yahoo Finance API to Quant Agent. Fetch price, volume, volatility, RSI, and momentum for a ticker. Output: structured quant object. | P2 | **P0** |
| D1-05 | **Bull & Bear Agent implementation** | Implement Bull and Bear agents. Each receives News \+ Quant context and generates a structured argument for or against investment. Agents must reference each other's prior arguments. | P1 | **P0** |
| D1-06 | **Risk & Skeptic Agent implementation** | Risk Agent monitors drawdown threshold (configurable). Skeptic Agent evaluates argument quality and flags weak reasoning. Both can interrupt the debate loop. | P1 | **P1** |
| D1-07 | **Chair Agent \+ decision output** | Chair synthesizes all agent inputs. Outputs: Invest/Hold/Reject, % allocation, confidence score (0-100), one-line reasoning, re-evaluation timer. | P1 | **P0** |
| D1-08 | **Inter-agent memory with Redis** | Connect Redis for agent memory. Store: confidence scores per cycle, past decisions per ticker, agent position history. Agents must reference memory in arguments. | P2 | **P1** |
| D1-09 | **FastAPI backend \+ WebSocket server** | Build FastAPI app. POST /analyze endpoint triggers the agent debate. WebSocket /ws streams agent messages to frontend in real time as they are generated. | P3 | **P0** |
| D1-10 | **Market data pipeline** | Unified data fetcher for Yahoo Finance (price, technicals) and NewsAPI (headlines). Returns standardized JSON consumed by News and Quant agents. | P2 | **P0** |
| D1-11 | **CLI smoke test** | End-to-end test: input 'TSLA' via CLI. All 7 agents fire in sequence. Chair produces a decision. Verify output structure and agent message flow. | P1 | **P0** |
| D1-12 | **Breaking news injection endpoint** | POST /inject endpoint accepts an event string (e.g. 'CEO resigns'). Triggers News Agent re-evaluation and injects event into active debate context. | P3 | **P1** |

## **Day 2 — Build the War Room**

Goal: Full Bloomberg-style war room running live. Type a ticker. Agents argue visually. Inject breaking news. Watch the system adapt. Chair delivers verdict. Allocation bar updates.

**Team split for day 2:**

* Person 1 (P1) — Agent prompt tuning, conflict quality, memory accuracy, edge case hardening

* Person 2 (P2) — API reliability, Redis stability, AMD benchmark data collection, re-evaluation timer backend

* Person 3 (P3) — WebSocket frontend integration, /inject endpoint polish, latency optimization

* Person 4 (P4) — Full war room UI: all 4 panels, agent avatars, confidence meters, injection buttons, demo script

**End-of-day milestone: Full demo runs end-to-end. Backup video recorded. Demo script finalized. AMD benchmark panel shows real latency numbers.**

## **Day 2 Tickets**

| Ticket ID | Title | Description | Owner | Priority |
| :---- | :---- | :---- | :---- | :---- |
| D2-01 | **War room layout — 4-panel grid** | React app with 4-panel Bloomberg-style layout: debate stream (top-left), confidence meters (top-right), portfolio allocation (bottom-left), control panel (bottom-right). Dark terminal aesthetic. | P4 | **P0** |
| D2-02 | **Live debate stream panel** | Real-time agent message feed via WebSocket. Each message shows agent avatar, name, timestamp, and content. Disagreements highlighted amber. Risk Agent interruptions in red. | P4 | **P0** |
| D2-03 | **Agent confidence meters** | 7 animated confidence bars, one per agent. Update in real time as agents post messages. Chair meter is visually dominant. Smooth CSS transitions. | P4 | **P0** |
| D2-04 | **Portfolio allocation bar** | Horizontal allocation bar showing Invest % / Hold % / Reject %. Updates after each Chair decision. Animated transition between states. | P4 | **P1** |
| D2-05 | **Ticker input \+ start debate UI** | Top bar input field for ticker symbol. Submit button triggers POST /analyze. Loading state while agents spin up. Error handling for invalid tickers. | P4 | **P0** |
| D2-06 | **Breaking news injection buttons** | Control panel with 6 pre-scripted event buttons: 'Earnings miss', 'CEO resigns', 'Market crash \-10%', 'Competitor acquired', 'Regulatory probe', 'Record earnings'. Each calls POST /inject. | P4 | **P0** |
| D2-07 | **Decision summary card** | Persistent card showing current Chair verdict: Invest/Hold/Reject badge, % allocation, confidence score, risk level (Low/Med/High), one-line reasoning. Updates each cycle. | P4 | **P0** |
| D2-08 | **Re-evaluation countdown timer** | When Chair sets a re-evaluation window, display a live countdown timer. On expiry, automatically re-trigger the debate with updated market data. | P3 | **P1** |
| D2-09 | **Agent avatar system** | Unique avatar/icon per agent with color coding: News (blue), Quant (amber), Bull (green), Bear (red), Risk (orange), Skeptic (gray), Chair (navy). Used in debate stream and confidence panels. | P4 | **P1** |
| D2-10 | **AMD benchmark panel** | Small stats panel showing: agents running in parallel, decision cycle latency (ms), total tokens processed. Pull real timing data from backend. Highlight MI300X advantage. | P3 | **P1** |
| D2-11 | **WebSocket frontend integration** | Connect React frontend to FastAPI WebSocket. Handle connection, reconnection, message parsing. Render incoming agent messages into debate stream in real time. | P3 | **P0** |
| D2-12 | **Demo script \+ scenario prep** | Write exact demo script: 3 tickers to demo (TSLA, NVDA, AAPL), which injection events to trigger and when, talking points for each agent reaction, 3-minute run of show. | P4 | **P0** |
| D2-13 | **Backup demo video recording** | Record a clean full run-through of the demo. Ticker input → debate → injection event → re-evaluation → final verdict. Keep as backup in case live demo fails on stage. | P4 | **P1** |
| D2-14 | **Edge case hardening** | Handle: invalid ticker, API rate limits, agent timeout, WebSocket disconnect, empty news results. Graceful fallbacks for all failure modes. | P3 | **P1** |

# **5\. UI Specification**

The UI must feel like a Bloomberg Terminal crossed with an AI brain. Dark background, precise typography, real-time updates. Judges should be able to understand what is happening without any explanation.

## **4-Panel Layout**

* Top-left — Live debate stream: agent messages stream in real time with avatars, names, and timestamps. Disagreements highlighted amber. Risk Agent interruptions in red.

* Top-right — Confidence meters: 7 animated bars, one per agent. Numbers tick live. Chair meter is visually dominant.

* Bottom-left — Portfolio allocation: horizontal bar showing Invest / Hold / Reject percentages. Animates on each Chair decision.

* Bottom-right — Control panel: ticker input, start button, 6 breaking news injection buttons, decision summary card, AMD benchmark stats.

## **Decision Summary Card (always visible)**

* Verdict badge: INVEST (green) / HOLD (amber) / REJECT (red)

* Allocation percentage

* Confidence score 0-100

* Risk level: Low / Medium / High

* One-line reasoning from Chair

* Re-evaluation countdown timer when active

# **6\. Demo Script**

The demo runs exactly 3 minutes. Do not explain the system before running it. Let judges watch first, then speak.

## **Run of Show**

| Time | Action |
| :---- | :---- |
| **0:00** | Type 'TSLA' into the ticker input. Hit enter. Say nothing. |
| **0:05** | Agents begin firing. News Agent surfaces a headline. Quant flags volatility. Let it run. |
| **0:20** | Bull and Bear argue. Point out a direct disagreement on screen. "Watch — they're challenging each other." |
| **0:40** | Chair delivers first verdict. Show the decision card. |
| **0:50** | Hit 'CEO Resigns' injection button. Say nothing. |
| **1:00** | Watch agents react instantly. Bear Agent confidence spikes. Bull retreats. Risk Agent interrupts. |
| **1:30** | Chair delivers new verdict — decision has changed. Show the delta. |
| **1:45** | "This is 7 agents running in parallel on AMD MI300X. Decision cycle: under 2 seconds." Point to benchmark panel. |
| **2:00** | "A human investment committee takes 3 hours to reach this decision. This took 90 seconds." Done. |

## **Key Talking Points**

* "This isn't a chatbot. This is an autonomous investment committee."

* "Watch the agents challenge each other — that disagreement is real, not scripted."

* "The Skeptic Agent just flagged a weak argument. Now the system has to re-evaluate."

* "We just injected a breaking news event. The entire debate context updated in real time."

* "7 agents, parallel inference, sub-2 second decision cycles — that's the MI300X."

# **7\. Risk Register**

| Risk | Likelihood | Mitigation |
| :---- | :---- | :---- |
| AMD Cloud access takes too long to configure | **High** | Set up tonight before day 1\. This is the first task. |
| Agent debate quality is poor or repetitive | **Medium** | Invest in agent prompts on day 1\. Each agent needs a strong backstory and explicit instruction to challenge others. |
| NewsAPI rate limits during live demo | **Medium** | Cache a set of real headlines per ticker. Fall back to cached data if API is slow. |
| UI not finished by end of day 2 | **Medium** | UI polish is last priority. A working engine with a basic UI beats a beautiful UI on a broken engine. |
| Live demo tech failure on stage | **Low** | Record a full backup demo video on day 2 (ticket D2-13). Play it if anything breaks. |

# **8\. Success Criteria**

## **Minimum Viable Demo (must have)**

* 7 agents fire and produce distinct, non-repetitive arguments for any ticker

* Agents reference each other's arguments directly (not just their own context)

* Chair produces a structured decision: verdict, allocation, confidence, reasoning

* Breaking news injection visibly changes the debate and the final decision

* Debate stream renders in real time on the frontend via WebSocket

## **Full War Room (win condition)**

* All 4 UI panels live and updating in real time

* Agent confidence meters animate during the debate

* AMD benchmark panel shows real latency numbers from MI300X

* Re-evaluation timer triggers automatic debate refresh

* Demo runs cleanly end-to-end in under 3 minutes

# **9\. Before Day 1 — Do Tonight**

These three things must be done before the team sits down to code. If AMD Cloud is not running on day 1 morning, you lose half a day.

* Get AMD Developer Cloud access. Provision an MI300X instance. Confirm it is live.

* Deploy Llama 3.1 70B or DeepSeek-V3 via vLLM. Hit the inference endpoint manually and confirm a response.

* Get NewsAPI and Yahoo Finance API keys. Run a test call for TSLA. Confirm data returns.

* Assign the 4 roles from the day 1 team split to specific people. Everyone knows their lane before day 1 starts.