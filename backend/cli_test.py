"""
P1-08 / P1-11 CLI smoke test.

Usage:
    python cli_test.py [TICKER] [--inject "event string"]

Examples:
    python cli_test.py TSLA
    python cli_test.py NVDA --inject "CEO resigns effective immediately"
"""
from __future__ import annotations

import asyncio
import sys

from dotenv import load_dotenv

load_dotenv()

from debate_runner import DebateRunner  # noqa: E402 — must load .env first

_AGENT_COLORS = {
    "news": "\033[94m",     # blue
    "quant": "\033[93m",    # amber/yellow
    "bull": "\033[92m",     # green
    "bear": "\033[91m",     # red
    "risk": "\033[33m",     # orange
    "skeptic": "\033[90m",  # gray
    "chair": "\033[34m",    # navy/blue
}
_RESET = "\033[0m"
_BOLD = "\033[1m"


async def main(ticker: str, injected_event: str | None) -> None:
    runner = DebateRunner()

    print(f"\n{_BOLD}{'=' * 64}{_RESET}")
    print(f"{_BOLD}  QUORUM WAR ROOM — CLI SMOKE TEST{_RESET}")
    print(f"  Ticker: {_BOLD}{ticker}{_RESET}")
    if injected_event:
        print(f"  Injected event: {injected_event}")
    print(f"{_BOLD}{'=' * 64}{_RESET}\n")

    async for msg in await runner.run(ticker, injected_event=injected_event):
        if msg.type == "status":
            print(f"  [{msg.payload['status'].upper()}]\n")

        elif msg.type == "agent_message":
            p = msg.payload
            color = _AGENT_COLORS.get(p["agent"], "")
            agent_label = f"{color}{_BOLD}{p['agent'].upper():<8}{_RESET}"
            flag_label = f" \033[1m[{p['flag']}]\033[0m" if p["flag"] else ""
            conf_label = f" (confidence: {p['confidence']}/100)" if p["confidence"] is not None else ""
            print(f"{agent_label}{flag_label}{conf_label}")
            print(f"  {p['content']}\n")

        elif msg.type == "decision":
            p = msg.payload
            verdict_color = {"INVEST": "\033[92m", "HOLD": "\033[93m", "REJECT": "\033[91m"}.get(p["verdict"], "")
            print(f"\n{_BOLD}{'─' * 64}{_RESET}")
            print(f"  VERDICT: {verdict_color}{_BOLD}{p['verdict']}{_RESET}")
            print(f"  Allocation:  {p['allocation_pct']}%")
            print(f"  Confidence:  {p['confidence']}/100")
            print(f"  Risk level:  {p['risk_level']}")
            print(f"  Reasoning:   {p['reasoning']}")
            print(f"  Re-eval in:  {p['reeval_seconds']}s")
            print(f"{_BOLD}{'─' * 64}{_RESET}\n")

        elif msg.type == "benchmark":
            p = msg.payload
            print(f"  Benchmark: {p['cycle_latency_ms']}ms total | {p['gpu']}\n")


if __name__ == "__main__":
    args = sys.argv[1:]
    ticker = "TSLA"
    inject = None

    for i, arg in enumerate(args):
        if arg == "--inject" and i + 1 < len(args):
            inject = args[i + 1]
        elif not arg.startswith("--"):
            ticker = arg.upper()

    asyncio.run(main(ticker, inject))
