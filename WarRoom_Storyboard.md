**War Room**

Team Storyboard — Per-Person Tickets

Track 1: AI Agents & Agentic Workflows  |  AMD Developer Cloud  |  2 Days

| P1 — Agent Engineer | P2 — Data & Infra | P3 — Backend | P4 — Frontend |
| :---- | :---- | :---- | :---- |

| P0 \= Critical — must ship | P1 \= Important | P2 \= Nice to have | Tonight \= Do before Day 1 |
| :---- | :---- | :---- | :---- |

| Person 1 — Agent Engineer CrewAI · All 7 agents · Debate quality · Prompt tuning *You own everything the agents say. If the debate is boring, that's on you.* |
| :---- |

Your most important task is P1-04 (Bull & Bear agents). If they don't reference each other, the debate looks fake and you lose. Spend at least 2 hours on prompt tuning.

| ID | Ticket | What to build | Done when… | Pri | When |
| :---- | :---- | :---- | :---- | ----- | ----- |
| P1-00 | **AMD endpoint smoke test** | Confirm the vLLM endpoint from P2 is live. Send a curl POST and verify a text response returns. Record the latency number. | curl returns a text response in under 5s Latency documented in shared notes | **P0** | **Tonight** |
| P1-01 | **CrewAI project scaffold** | Install CrewAI. Init project structure. Define all 7 Agent objects with role, goal, backstory from Tech Spec §2. Create Crew object with sequential process. | All 7 agents instantiate without error crew.kickoff() runs (even if output is garbage) | **P0** | **Day 1 AM** |
| P1-02 | **News Agent \+ task** | Implement News Agent using goal/backstory from Tech Spec §2. Wire task: input ticker, call fetcher.get\_news(), return SentimentObject JSON. Validate JSON shape: headline, source, sentiment, score, reasoning. | agent.run('TSLA') returns valid SentimentObject All 5 fields present and correct types | **P0** | **Day 1 AM** |
| P1-03 | **Quant Agent \+ task** | Implement Quant Agent using Tech Spec §2 prompt. Task: input ticker, call fetcher.get\_quant(), return QuantObject. Validate: price, change\_pct, rsi, volatility, momentum, key\_signal. | agent.run('TSLA') returns valid QuantObject RSI is a float, volatility is LOW/MEDIUM/HIGH | **P0** | **Day 1 AM** |
| P1-04 | **Bull & Bear Agents \+ tasks** | Implement Bull and Bear agents from Tech Spec §2. Bull receives: SentimentObject \+ QuantObject \+ bear\_output (null on first run). Bear receives: all above \+ bull\_output. Both must reference each other by name in rebuttal field. | Bull rebuttal references Bear's claim by name when Bear runs first Bear rebuttal names a specific Bull evidence point Both output valid ArgumentObject JSON | **P0** | **Day 1 AM** |
| P1-05 | **Risk Agent \+ interrupt logic** | Implement Risk Agent. Input: QuantObject \+ both arguments. Set interrupt: true when volatility is HIGH AND drawdown\_risk \> DRAWDOWN\_THRESHOLD (0.15). Return RiskObject: drawdown\_risk, interrupt, threshold\_breached, risk\_note. | interrupt: true fires correctly on simulated HIGH volatility \+ high drawdown interrupt: false when volatility is LOW | **P0** | **Day 1 PM** |
| P1-06 | **Skeptic Agent \+ re-eval logic** | Implement Skeptic Agent. Input: all prior outputs. Must identify at least one weak argument when given intentionally bad inputs. If force\_reeval: true, debate loop restarts from Bull/Bear with a REEVAL flag. | Skeptic correctly flags a deliberately weak argument in testing force\_reeval: true triggers a second Bull/Bear cycle | **P1** | **Day 1 PM** |
| P1-07 | **Chair Agent \+ final decision output** | Implement Chair Agent. Input: all prior outputs \+ Redis memory. Output DecisionObject: verdict, allocation\_pct, confidence, risk\_level, reasoning, reeval\_seconds. Chair must cite specific agent arguments in reasoning field. When interrupt flag is set, Chair issues conservative HOLD or REJECT only. | DecisionObject contains all 6 required fields Verdict changes appropriately with vs without interrupt flag reasoning field references at least one specific agent by name | **P0** | **Day 1 PM** |
| P1-08 | **Full debate loop — end-to-end test** | Wire all 7 agents into a single crew.kickoff() call. Test with TSLA, NVDA, AAPL. Verify output quality: no repetitive arguments, agents reference each other, Chair produces a reasoned verdict. | Full pipeline runs for 3 tickers without error Bull and Bear arguments are distinct and reference each other Chair verdict is coherent and cites agent output | **P0** | **Day 1 PM** |
| P1-09 | **Prompt tuning — debate quality pass** | Run 5 debate cycles. Identify repetitive or weak outputs. Tighten agent backstories and task descriptions to force conflict. Ensure Bull and Bear disagree on at least 2 points per cycle. | Two back-to-back TSLA debates produce meaningfully different arguments No agent repeats the same sentence twice in one cycle | **P1** | **Day 2 AM** |
| P1-10 | **Breaking news injection handling** | When /inject fires, re-run News Agent with injected event string as headline. Restart debate from Bull/Bear with injected context. Chair must update verdict — verify it actually changes. | 'CEO Resigns' injection visibly changes Bear confidence and Chair verdict Injected event appears in debate stream within 5s | **P1** | **Day 2 AM** |
| P1-11 | **Demo dry run \+ agent QA** | Run the full demo script twice end-to-end with P4. Fix any agent outputs that would confuse a non-technical judge. Ensure the INTERRUPT moment is dramatic and visible. | Demo runs cleanly twice with no prompting from team Risk Agent interrupt is clearly visible in the debate stream | **P0** | **Day 2 PM** |

## **Your Sync Schedule**

| Sync point | What to communicate |
| :---- | :---- |
| **Tonight (before sleep)** | Confirm P2 AMD endpoint is live. Get the URL. Set it in your local .env. Do not start Day 1 without this. |
| **Day 1 AM — 9:00** | Quick standup: confirm P2 fetcher module works, P3 /analyze is up. Unblock each other before heads-down coding. |
| **Day 1 PM — 15:00** | Share full debate loop output with team. P3 needs final JSON schemas to wire WebSocket messages. Do not delay this. |
| **Day 2 AM — 9:00** | Team standup. Review Day 1 CLI output quality. Identify top 2 prompt issues to fix today. |
| **Day 2 AM — 11:00** | Sit with P4 for demo dry run. Watch the UI while the debate runs. Flag anything confusing to a judge. |
| **Day 2 PM — 16:00** | Final full demo run. Fix only critical bugs. Freeze code. |

| Person 2 — Data & Infrastructure AMD Cloud · Market data APIs · Redis · Environment *You are the foundation everyone else builds on. If your infra is late, everyone is blocked.* |
| :---- |

Your most important task is P2-00 — done TONIGHT. The entire team is blocked on Day 1 morning if the AMD endpoint is not live. This is the single most critical task in the project.

| ID | Ticket | What to build | Done when… | Pri | When |
| :---- | :---- | :---- | :---- | ----- | ----- |
| P2-00 | **Provision AMD MI300X instance** | Log into AMD Developer Cloud tonight. Provision an MI300X instance. Deploy Llama 3.1 70B (or DeepSeek-V3) via vLLM. Confirm inference endpoint returns a response via curl. | Endpoint URL documented and shared with P1 before Day 1 starts curl POST returns text response | **P0** | **Tonight** |
| P2-01 | **Get API keys \+ test calls** | Sign up for NewsAPI (newsapi.org — free tier works). Test Yahoo Finance via yfinance Python package (no key needed). Run a test fetch for TSLA: confirm headline and price data return. | NewsAPI returns ≥3 headlines for TSLA yfinance returns price, rsi, volume for TSLA | **P0** | **Tonight** |
| P2-02 | **Data fetcher module** | Build data/fetcher.py with get\_news(ticker) and get\_quant(ticker). Use Tech Spec §3 code as the base — copy and adapt. get\_quant() must compute RSI manually from price history. Return standardised JSON objects consumed by agents. | fetcher.get\_news('TSLA') returns list of dicts with headline \+ source fetcher.get\_quant('TSLA') returns dict with price, change\_pct, rsi, volatility, momentum, key\_signal | **P0** | **Day 1 AM** |
| P2-03 | **Redis setup \+ memory helpers** | Spin up Redis locally (Docker: docker run \-d \-p 6379:6379 redis). Write memory.py with read\_memory(ticker) and write\_memory(ticker, decision). Key pattern: warroom:memory:{ticker} — store last 10 DecisionObjects. Write confidence tracking: warroom:confidence:{ticker}:{agent}. | After 2 debate cycles, read\_memory('TSLA') returns 2 past decisions Chair receives memory context and references it in reasoning | **P1** | **Day 1 AM** |
| P2-04 | **News headline cache (fallback)** | Pre-fetch and save headlines for TSLA, NVDA, AAPL to JSON files. If NewsAPI fails or rate-limits during demo, load from cache instead. Cache format: {ticker: \[{headline, source, sentiment\_guess}\]}. | Cache files exist for all 3 demo tickers Fetcher falls back to cache when API returns error or empty | **P1** | **Day 1 PM** |
| P2-05 | **AMD benchmark timing** | Wrap the crew.kickoff() call with time.perf\_counter() to measure cycle latency. Record: total debate duration (ms), per-agent latency, parallel token throughput. Expose these as a /benchmark GET endpoint for the frontend panel. | Benchmark endpoint returns real latency numbers (not hardcoded) Numbers update every debate cycle | **P1** | **Day 1 PM** |
| P2-06 | **Environment \+ secrets setup** | Create .env file with all required keys (see Tech Spec §6). Create .env.example with placeholder values. Add .env to .gitignore. Share actual .env with team via secure channel (not Slack/email plaintext). | .env.example committed to repo .env never appears in git log All team members confirm their local .env works | **P0** | **Day 1 AM** |
| P2-07 | **API reliability hardening** | Add retry logic (3 attempts, 1s backoff) to NewsAPI calls. Add timeout=5s to all external HTTP calls. If both NewsAPI and cache fail, return a default neutral SentimentObject so debate can still run. | Simulated NewsAPI failure falls back to cache gracefully No unhandled exception when external API is down | **P1** | **Day 2 AM** |
| P2-08 | **Pre-demo infrastructure check** | Day 2 PM: verify AMD Cloud instance is running and responsive. Confirm Redis is running and memory is clean. Do a full cold-start test: restart everything, run TSLA debate, verify no errors. | Cold start completes without error in under 2 minutes AMD endpoint latency is under 3s per agent | **P0** | **Day 2 PM** |

## **Your Sync Schedule**

| Sync point | What to communicate |
| :---- | :---- |
| **Tonight — before midnight** | AMD endpoint must be live. Share URL with P1 and P3 immediately. If it takes longer, message the team. |
| **Day 1 AM — 9:00** | Confirm fetcher module is working. P1 needs fetcher.get\_news() and fetcher.get\_quant() before they can test agents. |
| **Day 1 PM — 14:00** | Confirm Redis is running and P1 can read/write memory. Test with a dummy decision object. |
| **Day 2 AM — 9:00** | Share benchmark latency numbers with team. P4 needs real numbers for the AMD panel. |
| **Day 2 PM — 14:00** | Full infrastructure check: AMD Cloud up, Redis clean, fetcher live. Be the one who knows everything is healthy. |

| Person 3 — Backend Engineer FastAPI · WebSockets · /analyze · /inject · Re-eval timer *You are the bridge between agents and the UI. If your WebSocket is slow or broken, the demo dies.* |
| :---- |

Your most important task is P3-00 — the schema agreement with P4. Do this in the first 30 minutes of Day 1\. If you and P4 build to different schemas, Day 2 AM becomes a debugging session instead of integration.

| ID | Ticket | What to build | Done when… | Pri | When |
| :---- | :---- | :---- | :---- | ----- | ----- |
| P3-00 | **Agree WebSocket schema with P4** | Read Tech Spec §3 WebSocket Message Schema. Meet with P4 for 15 minutes this morning. Agree on exact JSON shape for agent\_message, decision, benchmark, error types. Do not write any WebSocket code until this is agreed. | Both P3 and P4 have signed off on the schema in writing (Slack/notes) Schema matches Tech Spec §3 exactly or deviations are documented | **P0** | **Day 1 AM** |
| P3-01 | **FastAPI app scaffold** | Init FastAPI app with uvicorn. Add CORS middleware (allow all origins for hackathon). Add /health GET endpoint that returns {status: 'ok'}. Confirm P4 can hit /health from the frontend dev server. | curl localhost:8000/health returns {"status": "ok"} P4 confirms frontend can reach the endpoint | **P0** | **Day 1 AM** |
| P3-02 | **POST /analyze endpoint** | Accept {ticker: str} in request body. Generate a unique session\_id (uuid4). Start the CrewAI debate in a background task (FastAPI BackgroundTasks). Return {session\_id, status: 'started'} immediately — do not block. | POST /analyze returns session\_id in under 200ms Debate runs in background — server stays responsive | **P0** | **Day 1 AM** |
| P3-03 | **WebSocket /ws/{session\_id} endpoint** | Accept WebSocket connections at /ws/{session\_id}. As each agent completes, serialize its output to the agreed schema and send. Keep connection open until Chair delivers final decision. Send a status message when debate starts and ends. | P4 connects to ws:// and receives all 7 agent messages in order Connection closes cleanly after Chair message No dropped messages in 5 test runs | **P0** | **Day 1 PM** |
| P3-04 | **POST /inject endpoint** | Accept {session\_id, event: str}. Inject event string into the active debate context for the given session. Trigger News Agent re-run with injected event as the headline. Stream new messages over existing WebSocket connection. | Injecting 'CEO Resigns' triggers new agent messages on the WebSocket within 5s Existing WebSocket connection does not drop on inject | **P1** | **Day 1 PM** |
| P3-05 | **GET /memory/{ticker} endpoint** | Read past decisions from Redis using memory.read\_memory(ticker). Return {ticker, decisions: \[\], confidence\_history: \[\]}. Return empty arrays (not 404\) if no history exists. | Returns valid JSON for a ticker with history Returns {decisions: \[\], confidence\_history: \[\]} for unknown ticker | **P2** | **Day 1 PM** |
| P3-06 | **Benchmark timing endpoint** | Track cycle start/end time per session\_id. After Chair fires, send a benchmark WebSocket message with: cycle\_latency\_ms, agents\_parallel (always 7), tokens\_processed (estimate from output lengths), gpu: 'AMD MI300X'. Also expose GET /benchmark/{session\_id} for polling fallback. | Frontend receives benchmark message after every Chair decision cycle\_latency\_ms is a real measured number | **P1** | **Day 2 AM** |
| P3-07 | **Re-evaluation timer backend** | After Chair fires with reeval\_seconds \> 0, schedule a background task to re-run the debate after that delay. Re-run uses same ticker and session\_id. Streams new agent messages over same WebSocket. | After Chair sets reeval\_seconds: 30, a new debate cycle starts automatically 30s later WebSocket receives new messages from the re-evaluation cycle | **P1** | **Day 2 AM** |
| P3-08 | **Error handling \+ edge cases** | Return 400 for invalid ticker (empty string, numeric only). If AMD endpoint is unreachable: send error WebSocket message, do not crash. If WebSocket client disconnects mid-debate: cancel background task cleanly. Add request logging so errors are easy to trace during demo. | Invalid ticker returns 400 with clear message AMD endpoint failure sends error WS message without crashing server Server stays up after 10 rapid POST /analyze calls | **P1** | **Day 2 AM** |
| P3-09 | **Frontend integration test with P4** | Sit with P4 for 30 minutes. Run full flow: P4 types TSLA → WS messages appear in UI → inject event → new messages appear. Fix any schema mismatches or timing issues found. | All 7 agent messages appear in P4's debate stream Decision card updates from WS message Inject button triggers visible new messages | **P0** | **Day 2 AM** |
| P3-10 | **Pre-demo backend stability run** | Run 10 consecutive debate cycles without restarting the server. Verify no memory leaks or accumulating errors. Confirm WebSocket reconnects cleanly if client refreshes. Document the start commands for the demo machine. | 10 cycles complete without server restart Start commands written in README.md | **P0** | **Day 2 PM** |

## **Your Sync Schedule**

| Sync point | What to communicate |
| :---- | :---- |
| **Day 1 AM — first 30 mins** | Schema agreement meeting with P4. Agree WebSocket JSON shapes. Both sign off. Start coding after. |
| **Day 1 AM — 11:00** | P4 must be able to hit /health from frontend. Share server URL and port immediately. |
| **Day 1 PM — 15:00** | POST /analyze and WebSocket must be live. P4 cannot build DebateStream without receiving real messages. |
| **Day 2 AM — 10:00** | 30-minute integration session with P4. Full flow: ticker in → WS messages → inject → new messages. Fix together. |
| **Day 2 PM — 15:00** | 10-cycle stability run. Start commands documented. Be ready to restart the server in under 30 seconds during demo. |

| Person 4 — Frontend Engineer React · Tailwind · War room UI · Demo script · Backup video *You own what the judges see. The UI is the demo. If it looks bad, the project looks bad.* |
| :---- |

Your most important task is P4-13 — the backup demo video. Record it no matter what. Hardware fails on stage. Network drops. A clean pre-recorded video has saved more hackathon demos than any other single action.

| ID | Ticket | What to build | Done when… | Pri | When |
| :---- | :---- | :---- | :---- | ----- | ----- |
| P4-00 | **Agree WebSocket schema with P3** | Read Tech Spec §3 WebSocket Message Schema. Meet with P3 for 15 minutes this morning. Agree on exact JSON shape before writing any frontend code. Sketch the 4-panel layout on paper or Figma (10 mins) so the team can see it. | Schema agreed and noted Layout sketch shared with team | **P0** | **Day 1 AM** |
| P4-01 | **React app scaffold \+ 4-panel layout** | Create React app (Vite or CRA). Install Tailwind CSS. Build the 4-panel grid: 2 columns × 2 rows, full viewport height. Add placeholder content in each panel so layout is visible immediately. Dark background: bg-gray-950 or equivalent. | 4 panels visible on 1440px viewport with no horizontal scroll Layout holds on 1280px viewport Dark theme applied globally | **P0** | **Day 1 AM** |
| P4-02 | **useWarRoom hook \+ WebSocket connection** | Implement useWarRoom hook from Tech Spec §4 exactly. On startDebate(ticker): POST /analyze → get session\_id → open WebSocket. On WS message: parse type field, dispatch to messages / decision / benchmark state. Expose injectEvent(event) helper that calls POST /inject. | Hook connects to WS and populates messages\[\] state decision state updates when Chair WS message arrives No console errors on connect/disconnect | **P0** | **Day 1 AM** |
| P4-03 | **TopBar — ticker input \+ start button** | Controlled text input for ticker (uppercase forced). Submit button: calls startDebate(ticker), shows spinner while debate runs. Disable input while debate is active. Show session status: Idle / Running / Complete. | Typing 'tsla' auto-uppercases to 'TSLA' Button disables after click until Chair message arrives Spinner visible during debate | **P0** | **Day 1 AM** |
| P4-04 | **DebateStream panel — live message feed** | Render messages\[\] from useWarRoom hook. Each AgentMessage shows: coloured avatar circle (initials), agent name, timestamp, content. Agent colours: News=blue, Quant=amber, Bull=green, Bear=red, Risk=orange, Skeptic=gray, Chair=navy. flag=INTERRUPT: red left border. flag=WEAK\_ARG: amber left border. Auto-scroll to bottom on new message. | New messages appear within 200ms of WS receipt All 7 agents are visually distinct by colour Panel auto-scrolls without user input INTERRUPT messages have red border | **P0** | **Day 1 PM** |
| P4-05 | **ConfidencePanel — 7 animated bars** | One labelled progress bar per agent. Bar width driven by agent.confidence from WS messages. Animate with CSS transition: width 0.4s ease. Chair bar is visually larger/bolder than others. Show numeric value next to each bar. | All 7 bars animate smoothly — no flicker or jump Bars update in real time as WS messages arrive Chair bar is visually dominant | **P0** | **Day 1 PM** |
| P4-06 | **DecisionCard — Chair verdict display** | Always-visible card in control panel. Verdict badge: INVEST (green) / HOLD (amber) / REJECT (red). Show: allocation\_pct, confidence score, risk\_level chip, reasoning text. Animate a brief flash (outline pulse) when decision updates. | Card updates immediately when decision WS message arrives Verdict badge colour matches verdict correctly Reasoning text is fully readable (no truncation) | **P0** | **Day 1 PM** |
| P4-07 | **AllocationBar — portfolio allocation** | Horizontal segmented bar: green (invest) / amber (hold) / red (reject). Width proportional to allocation\_pct from Chair decision. Animate width change with CSS transition on update. Show percentage labels inside each segment. | Bar animates smoothly on each Chair decision Segment widths are proportional to allocation\_pct Labels are readable at all allocation values | **P1** | **Day 2 AM** |
| P4-08 | **NewsInjector — 6 event buttons** | 6 buttons in control panel: 'Earnings miss', 'CEO resigns', 'Market crash \-10%', 'Competitor acquired', 'Regulatory probe', 'Record earnings'. Each calls injectEvent(event) from useWarRoom hook. Buttons disabled when no active session. Show a brief 'Injecting…' state while POST /inject is in flight. | Clicking any button triggers new agent messages in DebateStream within 5s Buttons are disabled when no session is active 'Injecting…' state visible on click | **P0** | **Day 2 AM** |
| P4-09 | **BenchmarkPanel — AMD stats** | 3 stat tiles: Cycle Latency (ms), Agents Parallel, Tokens Processed. Fixed label: 'AMD MI300X' with AMD red accent. Pull values from benchmark WS messages. Update after every Chair decision. | All 3 stats display real numbers from backend Panel updates after every debate cycle AMD MI300X label is prominent and styled | **P1** | **Day 2 AM** |
| P4-10 | **ReevalTimer — countdown display** | Show MM:SS countdown when Chair sets reeval\_seconds \> 0\. On expiry: auto-call startDebate() with same ticker. Hide timer when no countdown is active. Subtle pulsing animation in final 10 seconds. | Timer counts down accurately from reeval\_seconds to 0 New debate triggers automatically at 0 Timer is hidden when no reeval is pending | **P1** | **Day 2 AM** |
| P4-11 | **Full integration test with P3** | Sit with P3 for 30 minutes on Day 2 AM. Run: TSLA → all WS messages → inject CEO Resigns → new messages → Chair update. Fix any rendering bugs found during live test. Verify auto-scroll, confidence bars, and decision card all update correctly. | All 7 agent messages render in DebateStream Decision card updates from Chair WS message Inject triggers visible new messages Confidence bars animate during debate | **P0** | **Day 2 AM** |
| P4-12 | **UI polish pass** | Apply consistent dark terminal aesthetic across all panels. Add panel labels / headers (e.g. 'LIVE DEBATE', 'CONFIDENCE', 'ALLOCATION', 'CONTROLS'). Ensure font sizes are readable from 3 metres away (demo distance). Remove any console errors or warnings. | No console errors All text readable at arm's length Consistent colour palette across all panels | **P1** | **Day 2 PM** |
| P4-13 | **Demo script rehearsal \+ backup video** | Run the 3-minute demo script from Project Plan §6 twice with the full team. Record a clean screen capture of the second run as backup. Note any timing issues or moments where the UI looked confusing. Fix the top 2 issues found. | Demo runs clean twice end-to-end Backup video file saved and playable Top 2 issues fixed | **P0** | **Day 2 PM** |

## **Your Sync Schedule**

| Sync point | What to communicate |
| :---- | :---- |
| **Day 1 AM — first 30 mins** | Schema agreement meeting with P3. Agree WebSocket JSON shapes. Both sign off. Start coding after. |
| **Day 1 AM — 11:00** | Confirm you can reach P3's /health endpoint. Unblock P3-01 immediately if not. |
| **Day 1 PM — 15:00** | You should be receiving real WS messages by now. If not — stop UI work and resolve the WS connection with P3. |
| **Day 2 AM — 10:00** | 30-minute integration session with P3. Full flow. Fix schema mismatches or timing bugs together. |
| **Day 2 PM — 14:00** | UI polish freeze. Only fix critical visual bugs after this point. Start demo rehearsal. |
| **Day 2 PM — 16:30** | Record backup demo video. This is non-negotiable. If the live demo breaks on stage, this saves you. |

# **Master Timeline — All 4 People**

| When | P1 — Agents | P2 — Infra | P3 — Backend | P4 — Frontend |
| :---- | :---- | :---- | :---- | :---- |
| **Tonight** | AMD endpoint smoke test | **AMD Cloud \+ APIs live ⚡** | Read Tech Spec schemas P3 | Read Tech Spec schemas P4 |
| **Day 1 AM** | CrewAI scaffold → News → Quant → Bull → Bear agents | Fetcher module \+ Redis \+ .env setup | Schema agreement with P4 → FastAPI scaffold → /analyze | Schema agreement with P3 → React scaffold → useWarRoom hook → TopBar |
| **Day 1 PM** | Risk \+ Skeptic \+ Chair agents → full loop CLI test | News cache fallback \+ benchmark timing | WebSocket /ws endpoint → /inject endpoint | DebateStream → ConfidencePanel → DecisionCard |
| **Day 2 AM** | Prompt tuning → injection handling → debate quality pass | API hardening \+ infra check \+ latency numbers | Benchmark WS \+ re-eval timer → integration test with P4 | AllocationBar → NewsInjector → BenchmarkPanel → ReevalTimer → Integration test with P3 |
| **Day 2 PM** | Demo dry run x2 → fix top agent issues → code freeze | Cold-start stability run → confirm AMD Cloud healthy | 10-cycle stability run → start commands → code freeze | UI polish → demo rehearsal x2 → record backup video |

## **The Rule**

Engine before UI. A working agent debate with a basic frontend beats a beautiful UI with broken agents. If Day 1 PM arrives and the CLI smoke test is not passing — P4 stops UI work and helps debug.