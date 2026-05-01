# Copilot Instructions for this Repository

## Build, test, and lint commands

This project is a Python package with no separate build pipeline.

```bash
# Install deps (includes dev tools from uv.lock / pyproject.toml)
uv sync --dev

# Run lint
uv run ruff check .

# Run the agent CLI
uv run python main.py "Read workspace/main.py and explain it"
```

Tests in this repo are script-style harnesses (not a unified pytest suite):

```bash
# Run all current test scripts
uv run python test_get_files_info.py && uv run python test_get_file_content.py && uv run python test_write.py && uv run python test_run_python_file.py

# Run a single test script
uv run python test_get_file_content.py
```

## High-level architecture

Request lifecycle across modules:

1. `main.py` loads persisted chat history, ensures the system prompt exists, appends the new user task, and starts the iterative tool-use loop (`MAX_ITERATIONS`).
2. In each loop turn, `main.py` sends `history + TOOLS` to Groq, receives either text or tool calls, and persists assistant turns in a Groq-compatible JSON format (including serialized `tool_calls` when present).
3. Tool calls are handed to `agent/call_function.py`, which validates the function name, parses JSON args, force-injects `WORKING_DIRECTORY`, executes the mapped function, and truncates oversized outputs.
4. `functions/*` performs the actual filesystem/script operations, each with its own path-boundary checks and operation-specific guards.
5. Tool results are appended back into history as `role=tool` messages, then fed into the next model turn until a final assistant text response is emitted and history is written to `chat_history.json`.

Configuration for all of the above (model, limits, sandbox path, prompt, timeout) is centralized in `agent/config.py`.

`workspace/` is the default sandbox root that tools operate against. `code-agent-refactored/` is a parallel refactor snapshot; the active runtime path in this repository starts at the top-level `main.py`.

## Key conventions

- Tool implementations return human-readable strings for both success and errors; they do not propagate exceptions to the model loop.
- Sandbox safety is enforced in two layers:
  - Dispatcher-level forced `working_directory` injection in `agent/call_function.py`.
  - Per-tool path checks (`os.path.commonpath`) in each file under `functions/`.
- All operational limits are config-driven via `agent/config.py` environment overrides (`MAX_*`, timeout, allowed executable extensions, working dir).
- Assistant/tool chat history is persisted to `chat_history.json`; assistant `tool_calls` are serialized to plain dicts, and `tool_calls` is omitted entirely when empty.
- When adding a new tool, update both:
  - `agent/tools.py` (schema exposed to the model)
  - `agent/call_function.py` `FUNCTION_MAP` (runtime dispatch)
