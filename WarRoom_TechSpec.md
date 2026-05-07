**War Room — Technical Specification**

Engineer reference document — agent prompts, schemas, architecture, component spec

Companion to: WarRoom\_ProjectPlan.docx

# **1\. CrewAI Architecture**

## **Execution Model**

The debate runs as a CrewAI sequential process with interruption hooks. Agents execute in this order per debate cycle:

| Step | Agent | Input | Output |
| :---- | :---- | :---- | :---- |
| **1** | **News Agent** | Ticker symbol | SentimentObject: {headline, sentiment, score, source} |
| **2** | **Quant Agent** | Ticker symbol | QuantObject: {price, change\_pct, rsi, volatility, momentum} |
| **3** | **Bull Agent** | SentimentObject \+ QuantObject \+ debate\_history | ArgumentObject: {position, claim, evidence, confidence} |
| **4** | **Bear Agent** | SentimentObject \+ QuantObject \+ Bull argument | ArgumentObject: {position, claim, evidence, confidence, rebuttal\_to} |
| **5** | **Risk Agent** | QuantObject \+ both arguments | RiskObject: {drawdown\_risk, interrupt: bool, threshold\_breached: bool} |
| **6** | **Skeptic Agent** | All prior outputs | SkepticObject: {weak\_arguments: \[\], hallucination\_flags: \[\], force\_reeval: bool} |
| **7** | **Chair Agent** | All prior outputs \+ memory | DecisionObject: {verdict, allocation\_pct, confidence, risk\_level, reasoning, reeval\_seconds} |

If Risk Agent sets interrupt: true, the debate loop halts immediately after step 5\. Chair is called with a HALT flag and must issue a conservative decision.

If Skeptic Agent sets force\_reeval: true, the loop restarts from step 3 with a flag indicating which arguments were flagged as weak.

## **CrewAI Setup Code**

This is the scaffolding structure. Agent backstories and full goal strings are in Section 2\.

from crewai import Agent, Task, Crew, Process  
from langchain\_openai import ChatOpenAI

llm \= ChatOpenAI(  
    base\_url='http://YOUR\_AMD\_ENDPOINT/v1',  
    api\_key='token',  
    model='llama-3.1-70b'  
)

news\_agent   \= Agent(role='News Agent',   goal=NEWS\_GOAL,    backstory=NEWS\_BS,    llm=llm, verbose=True)  
quant\_agent  \= Agent(role='Quant Agent',  goal=QUANT\_GOAL,   backstory=QUANT\_BS,   llm=llm, verbose=True)  
bull\_agent   \= Agent(role='Bull Agent',   goal=BULL\_GOAL,    backstory=BULL\_BS,    llm=llm, verbose=True)  
bear\_agent   \= Agent(role='Bear Agent',   goal=BEAR\_GOAL,    backstory=BEAR\_BS,    llm=llm, verbose=True)  
risk\_agent   \= Agent(role='Risk Agent',   goal=RISK\_GOAL,    backstory=RISK\_BS,    llm=llm, verbose=True)  
skeptic\_agent= Agent(role='Skeptic Agent',goal=SKEPTIC\_GOAL, backstory=SKEPTIC\_BS, llm=llm, verbose=True)  
chair\_agent  \= Agent(role='Chair Agent',  goal=CHAIR\_GOAL,   backstory=CHAIR\_BS,   llm=llm, verbose=True)

crew \= Crew(  
    agents=\[news\_agent, quant\_agent, bull\_agent, bear\_agent, risk\_agent, skeptic\_agent, chair\_agent\],  
    tasks=\[news\_task, quant\_task, bull\_task, bear\_task, risk\_task, skeptic\_task, chair\_task\],  
    process=Process.sequential,  
    verbose=True  
)

# **2\. Agent System Prompts**

These are the most important strings in the entire project. Spend time on day 1 tuning them. Weak prompts produce repetitive, low-quality debates.

## **News Agent**

**Goal**

NEWS\_GOAL \= """  
Fetch and analyze the latest financial news for the given ticker.  
Surface the single most market-moving headline and assess its  
sentiment as BULLISH, BEARISH, or NEUTRAL with a score from \-1.0 to 1.0.  
Be specific. Do not summarize vaguely. Name the actual event.  
"""

**Backstory**

NEWS\_BS \= """  
You are a former Reuters financial journalist with 15 years covering  
markets. You have an instinct for which headlines move markets and which  
are noise. You are concise, direct, and never speculate beyond what the  
data says. You output structured JSON only.  
"""

**Task description**

news\_task \= Task(  
    description=f"""  
    Ticker: {ticker}  
    1\. Fetch the 5 most recent headlines for this ticker.  
    2\. Identify the single most significant market-moving headline.  
    3\. Return a JSON object: {{  
         'headline': str,  
         'source': str,  
         'sentiment': 'BULLISH' | 'BEARISH' | 'NEUTRAL',  
         'score': float (-1.0 to 1.0),  
         'reasoning': str (1 sentence)  
       }}  
    """,  
    agent=news\_agent,  
    expected\_output='JSON object with headline, source, sentiment, score, reasoning'  
)

## **Quant Agent**

**Goal**

QUANT\_GOAL \= """  
Retrieve and interpret quantitative market data for the given ticker.  
Identify the most significant technical signal — bullish or bearish.  
Speak in numbers. Every claim must have a data point behind it.  
"""

**Backstory**

QUANT\_BS \= """  
You are a quantitative analyst at a hedge fund. You distrust narratives  
and trust only numbers. You have built volatility models for 10 years.  
You are brief, precise, and always cite your figures. You output JSON only.  
"""

**Task description**

quant\_task \= Task(  
    description=f"""  
    Ticker: {ticker}  
    Fetch and return: {{  
      'price': float,  
      'change\_pct': float (24h),  
      'rsi': float,  
      'volatility': 'LOW' | 'MEDIUM' | 'HIGH',  
      'momentum': 'BULLISH' | 'BEARISH' | 'NEUTRAL',  
      'key\_signal': str (1 sentence — the most important technical fact)  
    }}  
    """,  
    agent=quant\_agent,  
    expected\_output='JSON object with price, change\_pct, rsi, volatility, momentum, key\_signal'  
)

## **Bull Agent**

**Goal**

BULL\_GOAL \= """  
Argue aggressively FOR the investment. Use the news and quant data as  
evidence. If the Bear Agent has already argued, directly rebut their  
weakest point by name. Do not be polite. Win the argument.  
"""

**Backstory**

BULL\_BS \= """  
You are an aggressive growth investor who has made a career finding  
overlooked opportunities. You believe markets underreact to positive  
catalysts. You are combative in debates and will directly challenge  
bearish claims. You always back your position with specific evidence.  
"""

**Task description**

bull\_task \= Task(  
    description=f"""  
    Ticker: {ticker}  
    News context: {news\_output}  
    Quant context: {quant\_output}  
    Bear argument (if exists): {bear\_output}

    Build the strongest possible bull case. Return JSON: {{  
      'position': 'INVEST',  
      'claim': str (your main argument, 1-2 sentences),  
      'evidence': \[str, str, str\] (3 specific data-backed points),  
      'rebuttal': str | null (direct rebuttal to bear if bear argued first),  
      'confidence': int (0-100)  
    }}  
    """,  
    agent=bull\_agent,  
    expected\_output='JSON ArgumentObject'  
)

## **Bear Agent**

**Goal**

BEAR\_GOAL \= """  
Argue aggressively AGAINST the investment. Expose every risk.  
If the Bull Agent has argued, attack their weakest evidence point  
by name. Be specific about what could go wrong and why.  
"""

**Backstory**

BEAR\_BS \= """  
You are a short-seller with a track record of calling market tops.  
You are deeply skeptical of hype and always look for what the market  
is ignoring. You have seen too many bull cases collapse. You are  
blunt, specific, and relentless in exposing weaknesses.  
"""

**Task description**

bear\_task \= Task(  
    description=f"""  
    Ticker: {ticker}  
    News context: {news\_output}  
    Quant context: {quant\_output}  
    Bull argument: {bull\_output}

    Build the strongest possible bear case. Directly attack the bull's  
    weakest evidence point. Return JSON: {{  
      'position': 'REJECT',  
      'claim': str (your main argument, 1-2 sentences),  
      'evidence': \[str, str, str\] (3 specific risk points),  
      'rebuttal': str (name the specific bull claim you are attacking),  
      'confidence': int (0-100)  
    }}  
    """,  
    agent=bear\_agent,  
    expected\_output='JSON ArgumentObject'  
)

## **Risk Agent**

**Goal**

RISK\_GOAL \= """  
Monitor portfolio risk. If volatility is HIGH and drawdown risk exceeds  
the threshold, set interrupt: true. You do not argue about the investment  
merits. You only enforce risk limits. Be terse.  
"""

**Backstory**

RISK\_BS \= """  
You are the chief risk officer. You do not care about upside.  
Your only job is to prevent catastrophic loss. When the numbers  
exceed threshold, you stop the debate regardless of the argument quality.  
"""

**Task \+ interrupt logic**

DRAWDOWN\_THRESHOLD \= 0.15  \# 15% — configurable

risk\_task \= Task(  
    description=f"""  
    Quant data: {quant\_output}  
    Bull confidence: {bull\_output\['confidence'\]}  
    Bear confidence: {bear\_output\['confidence'\]}  
    Drawdown threshold: {DRAWDOWN\_THRESHOLD}

    Assess risk. Return JSON: {{  
      'drawdown\_risk': float (estimated max drawdown 0.0-1.0),  
      'interrupt': bool (true if drawdown\_risk \> threshold AND volatility is HIGH),  
      'threshold\_breached': bool,  
      'risk\_note': str (1 sentence explanation)  
    }}  
    """,  
    agent=risk\_agent,  
    expected\_output='JSON RiskObject'  
)

## **Skeptic Agent**

**Goal**

SKEPTIC\_GOAL \= """  
Read all prior arguments and identify logical weaknesses, unsupported  
claims, or potential hallucinations. Call out specific claims by agent name.  
If arguments are poor quality, set force\_reeval: true.  
"""

**Backstory**

SKEPTIC\_BS \= """  
You are an epistemologist and former auditor. You do not take sides.  
You evaluate argument quality ruthlessly. You can smell a weak inference  
from a mile away. You name names when you call out bad reasoning.  
"""

**Task description**

skeptic\_task \= Task(  
    description=f"""  
    Bull argument: {bull\_output}  
    Bear argument: {bear\_output}  
    Risk assessment: {risk\_output}

    Evaluate argument quality. Return JSON: {{  
      'weak\_arguments': \[  
        {{'agent': str, 'claim': str, 'reason\_weak': str}}  
      \],  
      'hallucination\_flags': \[str\],  
      'force\_reeval': bool,  
      'verdict\_on\_debate\_quality': 'STRONG' | 'ADEQUATE' | 'WEAK'  
    }}  
    """,  
    agent=skeptic\_agent,  
    expected\_output='JSON SkepticObject'  
)

## **Chair Agent**

**Goal**

CHAIR\_GOAL \= """  
Synthesize all agent inputs into a final investment decision.  
Weigh argument quality (from Skeptic), risk (from Risk Agent),  
and evidence strength. Deliver a clear verdict with reasoning.  
Set a re-evaluation timer appropriate to the uncertainty level.  
"""

**Backstory**

CHAIR\_BS \= """  
You are the managing partner of the fund. You have heard thousands  
of investment debates. You cut through noise, weigh evidence fairly,  
and make decisive calls. You are accountable for every decision.  
"""

**Task description**

chair\_task \= Task(  
    description=f"""  
    All prior outputs: {all\_outputs}  
    Memory (past decisions for this ticker): {memory}  
    Halt flag: {risk\_output\['interrupt'\]}

    Synthesize and decide. Return JSON: {{  
      'verdict': 'INVEST' | 'HOLD' | 'REJECT',  
      'allocation\_pct': int (0-100, how much of budget to allocate),  
      'confidence': int (0-100),  
      'risk\_level': 'LOW' | 'MEDIUM' | 'HIGH',  
      'reasoning': str (2-3 sentences — cite specific agent arguments),  
      'reeval\_seconds': int (when to re-evaluate: 30 | 60 | 120 | 300\)  
    }}  
    """,  
    agent=chair\_agent,  
    expected\_output='JSON DecisionObject'  
)

# **3\. Data Schemas & API Contracts**

## **Market Data Fetcher**

Single module consumed by both News Agent and Quant Agent. Returns standardized objects.

\# data/fetcher.py

import yfinance as yf  
import requests

NEWS\_API\_KEY \= os.environ\['NEWS\_API\_KEY'\]

def get\_news(ticker: str) \-\> list\[dict\]:  
    url \= f'https://newsapi.org/v2/everything?q={ticker}\&sortBy=publishedAt\&pageSize=5'  
    headers \= {'Authorization': f'Bearer {NEWS\_API\_KEY}'}  
    res \= requests.get(url, headers=headers, timeout=5)  
    return res.json().get('articles', \[\])

def get\_quant(ticker: str) \-\> dict:  
    t \= yf.Ticker(ticker)  
    hist \= t.history(period='5d')  
    info \= t.fast\_info  
    close \= hist\['Close'\]  
    change\_pct \= (close.iloc\[-1\] \- close.iloc\[-2\]) / close.iloc\[-2\] \* 100  
    \# RSI calculation (14-period)  
    delta \= close.diff()  
    gain \= delta.clip(lower=0).rolling(14).mean()  
    loss \= \-delta.clip(upper=0).rolling(14).mean()  
    rsi \= 100 \- (100 / (1 \+ gain.iloc\[-1\] / loss.iloc\[-1\]))  
    return {  
        'price': round(info.last\_price, 2),  
        'change\_pct': round(change\_pct, 2),  
        'rsi': round(rsi, 1),  
        'volatility': 'HIGH' if abs(change\_pct) \> 3 else 'MEDIUM' if abs(change\_pct) \> 1 else 'LOW',  
        'volume': info.three\_month\_average\_volume  
    }

## **WebSocket Message Schema**

P3 (backend) and P4 (frontend) must agree on this schema before building. Every message sent over the WebSocket follows this structure.

\# Every WebSocket message is a JSON object with this shape:  
{  
  'type': 'agent\_message' | 'decision' | 'error' | 'status' | 'benchmark',  
  'timestamp': '2026-05-05T14:32:01Z',  // ISO 8601  
  'payload': { ... }  // shape depends on type  
}

\# type: 'agent\_message'  
{  
  'type': 'agent\_message',  
  'timestamp': str,  
  'payload': {  
    'agent': 'news' | 'quant' | 'bull' | 'bear' | 'risk' | 'skeptic' | 'chair',  
    'content': str,         // human-readable summary of output  
    'confidence': int,      // 0-100, null for news/quant  
    'flag': null | 'INTERRUPT' | 'WEAK\_ARG' | 'REEVAL',  // special states  
    'raw': {}               // full JSON output from agent  
  }  
}

\# type: 'decision'  (Chair output)  
{  
  'type': 'decision',  
  'timestamp': str,  
  'payload': {  
    'verdict': 'INVEST' | 'HOLD' | 'REJECT',  
    'allocation\_pct': int,  
    'confidence': int,  
    'risk\_level': 'LOW' | 'MEDIUM' | 'HIGH',  
    'reasoning': str,  
    'reeval\_seconds': int  
  }  
}

\# type: 'benchmark'  (AMD stats)  
{  
  'type': 'benchmark',  
  'timestamp': str,  
  'payload': {  
    'cycle\_latency\_ms': int,  
    'agents\_parallel': int,  
    'tokens\_processed': int,  
    'gpu': 'AMD MI300X'  
  }  
}

## **FastAPI Endpoints**

\# POST /analyze  
\# Triggers a full debate cycle for a given ticker  
Request:  { 'ticker': str }  
Response: { 'session\_id': str, 'status': 'started' }  
\# Messages stream via WebSocket after this call

\# POST /inject  
\# Injects a breaking news event into the active debate  
Request:  { 'session\_id': str, 'event': str }  
Response: { 'status': 'injected' }

\# GET /memory/{ticker}  
\# Returns past decisions for a ticker from Redis  
Response: { 'ticker': str, 'decisions': \[DecisionObject\], 'confidence\_history': \[int\] }

\# WebSocket: ws://host/ws/{session\_id}  
\# Streams all agent messages in real time as they are generated  
\# Client connects immediately after POST /analyze

## **Redis Memory Schema**

\# Key pattern: warroom:memory:{ticker}  
\# Value: JSON array of past DecisionObjects (last 10\)

\# Key pattern: warroom:confidence:{ticker}:{agent}  
\# Value: JSON array of confidence scores (last 10 cycles)

\# Example read in Chair Agent:  
memory \= redis.get(f'warroom:memory:{ticker}')  
past\_decisions \= json.loads(memory) if memory else \[\]

\# Example write after Chair decision:  
history \= json.loads(redis.get(f'warroom:memory:{ticker}') or '\[\]')  
history.append(decision\_object)  
redis.set(f'warroom:memory:{ticker}', json.dumps(history\[-10:\]))  \# keep last 10

# **4\. Frontend Component Specification**

All components are React functional components using hooks. WebSocket connection is managed at the App level and passed down via context.

## **Component Tree**

App  
  WarRoomProvider  (WebSocket context, session state)  
    TopBar           (ticker input \+ start button)  
    MainGrid         (2x2 panel layout)  
      DebateStream   (top-left)  
        AgentMessage   (repeated per message)  
      ConfidencePanel (top-right)  
        ConfidenceBar  (one per agent x7)  
      AllocationBar  (bottom-left)  
      ControlPanel   (bottom-right)  
        NewsInjector   (6 event buttons)  
        DecisionCard   (verdict display)  
        BenchmarkPanel (AMD stats)  
        ReevalTimer    (countdown)

## **Component Specs**

| Component | Props / State | Behaviour & Notes |
| :---- | :---- | :---- |
| **WarRoomProvider** | session\_id, messages\[\], decision, benchmark | Holds WebSocket connection. On message: parse type field, dispatch to correct state slice. Exposes sendTicker(ticker) and injectEvent(event) helpers. |
| **TopBar** | onSubmit(ticker) | Controlled input for ticker symbol. On submit: call POST /analyze, store session\_id, open WebSocket. Shows spinner while agents are running. |
| **DebateStream** | messages: AgentMessage\[\] | Scrolling feed. Auto-scrolls to bottom on new message. Messages with flag=INTERRUPT render with red left border. flag=WEAK\_ARG renders with amber. Agent avatar \+ name shown on each message. |
| **AgentMessage** | agent, content, confidence, flag, timestamp | Single message row. Avatar is a colored circle with agent initials. Color per agent: News=blue, Quant=amber, Bull=green, Bear=red, Risk=orange, Skeptic=gray, Chair=navy. |
| **ConfidencePanel** | confidences: {agent: int}\[\] | 7 labelled progress bars. Animate smoothly with CSS transition: width 0.4s ease. Chair bar is taller/wider than others to signal dominance. |
| **AllocationBar** | verdict, allocation\_pct | Horizontal segmented bar: green (invest) / amber (hold) / red (reject). Width proportional to allocation\_pct. Animate on update with CSS transition. |
| **NewsInjector** | onInject(event: string) | 6 buttons: 'Earnings miss', 'CEO resigns', 'Market crash \-10%', 'Competitor acquired', 'Regulatory probe', 'Record earnings'. Each calls POST /inject with session\_id \+ event string. Disabled if no active session. |
| **DecisionCard** | decision: DecisionObject | Verdict badge (colored). Allocation %. Confidence bar. Risk level chip. Reasoning text. Updates animate with a brief flash transition. |
| **BenchmarkPanel** | benchmark: BenchmarkObject | 3 stat tiles: cycle latency (ms), agents parallel, tokens processed. GPU label always shows 'AMD MI300X'. Pull from benchmark WebSocket messages. |
| **ReevalTimer** | reeval\_seconds: int | Countdown from reeval\_seconds to 0\. On expiry: auto-call POST /analyze with same ticker. Display as MM:SS. Hidden when no active countdown. |

## **WebSocket Hook**

// hooks/useWarRoom.js  
import { useState, useEffect, useRef, useCallback } from 'react'

export function useWarRoom() {  
  const \[messages, setMessages\] \= useState(\[\])  
  const \[decision, setDecision\]  \= useState(null)  
  const \[benchmark, setBenchmark\] \= useState(null)  
  const \[sessionId, setSessionId\] \= useState(null)  
  const ws \= useRef(null)

  const startDebate \= useCallback(async (ticker) \=\> {  
    const res \= await fetch('/analyze', {  
      method: 'POST',  
      headers: {'Content-Type': 'application/json'},  
      body: JSON.stringify({ ticker })  
    })  
    const { session\_id } \= await res.json()  
    setSessionId(session\_id)  
    ws.current \= new WebSocket(\`ws://localhost:8000/ws/${session\_id}\`)  
    ws.current.onmessage \= (e) \=\> {  
      const msg \= JSON.parse(e.data)  
      if (msg.type \=== 'agent\_message') setMessages(m \=\> \[...m, msg.payload\])  
      if (msg.type \=== 'decision')      setDecision(msg.payload)  
      if (msg.type \=== 'benchmark')     setBenchmark(msg.payload)  
    }  
  }, \[\])

  const injectEvent \= useCallback(async (event) \=\> {  
    await fetch('/inject', {  
      method: 'POST',  
      headers: {'Content-Type': 'application/json'},  
      body: JSON.stringify({ session\_id: sessionId, event })  
    })  
  }, \[sessionId\])

  return { messages, decision, benchmark, startDebate, injectEvent }  
}

# **5\. Definition of Done — Per Ticket**

A ticket is done only when all DoD criteria are met. No exceptions. This prevents 'done' meaning different things to different people.

| Ticket | Title | Definition of Done |
| :---- | :---- | :---- |
| **D1-01** | AMD Cloud setup | vLLM endpoint returns a text response to a curl POST request. Latency documented. |
| **D1-02** | CrewAI scaffold | All 7 Agent objects instantiate without error. Crew object created. No API calls yet. |
| **D1-03** | News Agent | Agent.run('TSLA') returns valid SentimentObject JSON with all required fields. |
| **D1-04** | Quant Agent | Agent.run('TSLA') returns valid QuantObject JSON with price, rsi, volatility, momentum. |
| **D1-05** | Bull & Bear Agents | Bull output contains rebuttal field referencing Bear's claim by name (or null on first run). Bear references Bull's evidence in rebuttal field. |
| **D1-06** | Risk & Skeptic Agents | Risk Agent correctly sets interrupt: true when volatility is HIGH and simulated drawdown \> 0.15. Skeptic identifies at least one weak argument when given intentionally bad inputs. |
| **D1-07** | Chair Agent | Chair output contains all 6 required fields. Verdict changes appropriately when interrupt flag is set vs not set. |
| **D1-08** | Redis memory | After 2 debate cycles on same ticker, Chair output references past decision in reasoning field. |
| **D1-09** | FastAPI \+ WebSocket | POST /analyze returns session\_id. WebSocket connection established. At least one message received from ws:// endpoint. |
| **D1-11** | CLI smoke test | Full pipeline runs end-to-end: TSLA in, Chair DecisionObject out, all 7 agent outputs printed to console in sequence. |
| **D2-01** | War room layout | All 4 panels visible on screen simultaneously. No horizontal scroll on 1440px viewport. Layout holds on 1280px viewport. |
| **D2-02** | Debate stream | New messages appear within 200ms of WebSocket receipt. Stream auto-scrolls. INTERRUPT messages visually distinct. At least 3 agents visually distinguishable by avatar color. |
| **D2-03** | Confidence meters | All 7 bars animate smoothly. Values update on every agent\_message WebSocket event. No flicker or jump. |
| **D2-06** | News injection buttons | Clicking any button triggers a new agent\_message cycle visible in the debate stream within 5 seconds. Decision card updates. |
| **D2-10** | AMD benchmark panel | Cycle latency displays a real measured number from the backend, not a hardcoded value. Updates each cycle. |
| **D2-12** | Demo script | Full 3-minute demo runs cleanly twice in a row with no team intervention. Backup video recorded and playable. |

# **6\. Environment Variables**

All secrets must be in a .env file. Never commit to git. Create a .env.example with placeholder values.

\# .env — copy to all team members via secure channel

\# AMD Cloud  
AMD\_ENDPOINT=http://YOUR\_MI300X\_INSTANCE/v1  
AMD\_TOKEN=your\_token\_here

\# Market Data  
NEWS\_API\_KEY=your\_newsapi\_key  
\# Yahoo Finance: no key needed for basic usage

\# Redis  
REDIS\_URL=redis://localhost:6379

\# App  
SESSION\_SECRET=random\_32\_char\_string  
DRAWDOWN\_THRESHOLD=0.15  
MAX\_DEBATE\_CYCLES=3

# **7\. Blocking Dependencies**

These are the inter-person blockers. Resolve them first or teams will be waiting on each other.

| Blocker | Blocks | Depends on | Resolve by |
| :---- | :---- | :---- | :---- |
| WebSocket schema | **P4 (frontend)** | P3 (backend) | Agree schema (Section 3\) before P4 writes any WebSocket code. Do this morning of Day 1\. |
| AMD endpoint live | **P1 (agents)** | P2 (infra) | P2 sets up AMD Cloud tonight. P1 cannot write agent code without a live LLM endpoint. |
| Agent output JSON shape | **P3 (backend routing)** | P1 (agents) | P1 finalizes all output schemas (Section 3\) by end of Day 1 morning. P3 needs them to build routing logic. |
| /analyze endpoint | **P4 (frontend)** | P3 (backend) | P3 ships POST /analyze by Day 1 afternoon so P4 can test WebSocket connection before end of day. |

