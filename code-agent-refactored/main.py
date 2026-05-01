"""
Code Agent — Groq-powered local AI coding agent.
Entry point: python main.py "your task here"
"""

import os
import sys
import json
import logging
from dotenv import load_dotenv
from groq import Groq

from agent.call_function import call_function
from agent.tools import TOOLS
from agent.config import (
    HISTORY_FILE, MAX_MESSAGES, MAX_ITERATIONS, MODEL, SYSTEM_PROMPT
)

# ──────────────────────────────────────────────
# Logging
# ──────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger(__name__)


# ──────────────────────────────────────────────
# History helpers
# ──────────────────────────────────────────────
def load_history() -> list[dict]:
    if not os.path.exists(HISTORY_FILE):
        return []
    try:
        with open(HISTORY_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
        if not isinstance(data, list):
            logger.warning("Corrupt history file — resetting.")
            return []
        return data
    except (json.JSONDecodeError, OSError) as e:
        logger.warning("Could not load history (%s) — starting fresh.", e)
        return []


def save_history(history: list[dict]) -> None:
    try:
        with open(HISTORY_FILE, "w", encoding="utf-8") as f:
            json.dump(history, f, indent=2, ensure_ascii=False)
    except OSError as e:
        logger.error("Could not save history: %s", e)


def trim_history(history: list[dict]) -> list[dict]:
    """Keep system message + last MAX_MESSAGES turns."""
    system_msgs = [m for m in history if m.get("role") == "system"]
    non_system = [m for m in history if m.get("role") != "system"]
    trimmed = non_system[-MAX_MESSAGES:]
    return system_msgs + trimmed


# ──────────────────────────────────────────────
# Serialise assistant message safely
# ──────────────────────────────────────────────
def serialise_tool_calls(tool_calls) -> list[dict] | None:
    """Convert Groq ToolCall objects to plain dicts for JSON persistence."""
    if not tool_calls:
        return None
    result = []
    for tc in tool_calls:
        result.append({
            "id": tc.id,
            "type": "function",
            "function": {
                "name": tc.function.name,
                "arguments": tc.function.arguments,
            },
        })
    return result


# ──────────────────────────────────────────────
# Agent loop
# ──────────────────────────────────────────────
def run_agent(client: Groq, user_input: str) -> None:
    history = load_history()

    # Inject system prompt exactly once
    if not any(m.get("role") == "system" for m in history):
        history.insert(0, {"role": "system", "content": SYSTEM_PROMPT})

    history.append({"role": "user", "content": user_input})
    history = trim_history(history)

    for iteration in range(1, MAX_ITERATIONS + 1):
        logger.info("── Iteration %d/%d ──────────────────", iteration, MAX_ITERATIONS)

        try:
            response = client.chat.completions.create(
                model=MODEL,
                messages=history,
                tools=TOOLS,
                tool_choice="auto",
                temperature=0,
            )
        except Exception as e:
            logger.error("Groq API error: %s", e)
            print(f"\n[ERROR] API call failed: {e}")
            sys.exit(1)

        message = response.choices[0].message

        # Persist assistant turn.
        # IMPORTANT: Groq rejects {"tool_calls": null} — only include the key
        # when there are actual tool calls.
        assistant_msg: dict = {
            "role": "assistant",
            "content": message.content or "",
        }
        serialised = serialise_tool_calls(message.tool_calls)
        if serialised:
            assistant_msg["tool_calls"] = serialised
        history.append(assistant_msg)

        # ── Tool calls ───────────────────────────────
        if message.tool_calls:
            for tool_call in message.tool_calls:
                result = call_function(tool_call)
                logger.info("  ↳ result preview: %s", str(result)[:120])

                history.append({
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "content": str(result),
                })
            continue  # let the model react to tool results

        # ── Final text response ──────────────────────
        if message.content:
            print("\n" + "─" * 60)
            print(message.content)
            print("─" * 60)
            save_history(history)
            return

        # Model returned neither tools nor text — treat as done
        logger.warning("Model returned empty response on iteration %d.", iteration)
        break

    print("\n[WARN] Max iterations reached. Agent may not have completed the task.")
    save_history(history)
    sys.exit(1)


# ──────────────────────────────────────────────
# CLI entry point
# ──────────────────────────────────────────────
def main() -> None:
    load_dotenv()
    api_key = os.getenv("GROQ_API_KEY")

    if not api_key:
        print("Error: GROQ_API_KEY not found in environment or .env file.")
        sys.exit(1)

    if len(sys.argv) < 2:
        print("Usage: python main.py \"<task description>\"")
        sys.exit(1)

    user_input = " ".join(sys.argv[1:])  # allow multi-word args without quotes

    client = Groq(api_key=api_key)
    run_agent(client, user_input)


if __name__ == "__main__":
    main()
