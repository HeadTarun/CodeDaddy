"""
agent/config.py — Single source of truth for all agent configuration.

Override any value via environment variable (e.g. GROQ_MODEL, MAX_ITERATIONS).
"""

import os

# ── Model ────────────────────────────────────────────────────────────────────
# llama-3.3-70b-versatile is Groq's best tool-use model as of 2026.
# Switch to llama3-groq-70b-8192-tool-use-preview for lower latency.
MODEL: str = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")

# ── Agent loop ────────────────────────────────────────────────────────────────
MAX_ITERATIONS: int = int(os.getenv("MAX_ITERATIONS", "10"))
MAX_MESSAGES: int = int(os.getenv("MAX_MESSAGES", "40"))

# ── Filesystem ────────────────────────────────────────────────────────────────
# The sandbox directory the agent is allowed to read/write/execute in.
WORKING_DIRECTORY: str = os.getenv("AGENT_WORKING_DIR", "workspace")
HISTORY_FILE: str = os.getenv("HISTORY_FILE", "chat_history.json")

# ── Output limits ─────────────────────────────────────────────────────────────
MAX_FILE_READ_CHARS: int = int(os.getenv("MAX_FILE_READ_CHARS", "10000"))
MAX_TOOL_OUTPUT_CHARS: int = int(os.getenv("MAX_TOOL_OUTPUT_CHARS", "5000"))
MAX_FILE_WRITE_BYTES: int = int(os.getenv("MAX_FILE_WRITE_BYTES", str(1 * 1024 * 1024)))  # 1 MB

# ── Subprocess ────────────────────────────────────────────────────────────────
SUBPROCESS_TIMEOUT_SECS: int = int(os.getenv("SUBPROCESS_TIMEOUT", "30"))

# ── Allowed extensions for execution ─────────────────────────────────────────
ALLOWED_EXEC_EXTENSIONS: frozenset[str] = frozenset({".py"})

# ── System prompt ─────────────────────────────────────────────────────────────
SYSTEM_PROMPT: str = """You are a local AI coding agent with filesystem and execution tools.

Capabilities:
- List files and directories (within your sandbox)
- Read file contents
- Write or create files
- Execute Python files and capture output

Rules:
- Always reason step-by-step before acting.
- Use tools when action is required; reply with text when the task is complete.
- Use relative paths only — never absolute paths.
- Do NOT attempt to access files outside the working directory.
- If a tool returns an error, investigate and try to recover.
- When you have finished a task, summarise what you did clearly.
"""
