"""
agent/call_function.py — Dispatches tool calls from Groq to the correct handler.
"""

import json
import logging

from functions.get_files_info import get_files_info
from functions.get_file_content import get_file_content
from functions.write_file import write_file
from functions.run_python_file import run_python_file
from agent.config import WORKING_DIRECTORY, MAX_TOOL_OUTPUT_CHARS

logger = logging.getLogger(__name__)

# ── Central tool registry ─────────────────────────────────────────────────────
# Add new tools here: name → callable
FUNCTION_MAP = {
    "get_files_info": get_files_info,
    "get_file_content": get_file_content,
    "write_file": write_file,
    "run_python_file": run_python_file,
}


def call_function(tool_call) -> str:
    """
    Execute a Groq tool call safely.

    Args:
        tool_call: A Groq ChatCompletionMessageToolCall object.

    Returns:
        String result (always a str — never raises to the caller).
    """
    function_name: str = getattr(tool_call.function, "name", "") or ""

    # ── Parse arguments ───────────────────────────────────────────────────────
    try:
        raw_args = getattr(tool_call.function, "arguments", "{}") or "{}"
        args: dict = json.loads(raw_args)
        if not isinstance(args, dict):
            args = {}
    except (json.JSONDecodeError, TypeError):
        logger.warning("Could not parse arguments for %s — using empty dict.", function_name)
        args = {}

    logger.info("[TOOL] %s | args=%s", function_name, args)

    # ── Validate function name ────────────────────────────────────────────────
    if function_name not in FUNCTION_MAP:
        return f"Error: Unknown function '{function_name}'. Available: {list(FUNCTION_MAP)}"

    # ── Inject sandbox directory (callers must not override this) ─────────────
    # This is the key security boundary: the working_directory is ALWAYS set
    # by the server, never by the model/user.
    args.pop("working_directory", None)  # remove if model tried to supply one
    args["working_directory"] = WORKING_DIRECTORY

    # ── Execute ───────────────────────────────────────────────────────────────
    try:
        result = FUNCTION_MAP[function_name](**args)
    except TypeError as e:
        # Mismatched arguments (missing required param, etc.)
        logger.error("Argument error calling %s: %s", function_name, e)
        return f"Error: bad arguments for '{function_name}': {e}"
    except Exception as e:
        logger.error("Unexpected error in %s: %s", function_name, e)
        return f"Error executing '{function_name}': {e}"

    # ── Truncate large output to protect context window ───────────────────────
    result_str = str(result)
    if len(result_str) > MAX_TOOL_OUTPUT_CHARS:
        result_str = (
            result_str[:MAX_TOOL_OUTPUT_CHARS]
            + f"\n[...output truncated at {MAX_TOOL_OUTPUT_CHARS} chars]"
        )

    return result_str
