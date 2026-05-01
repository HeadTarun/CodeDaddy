"""
agent/config.py — Single source of truth for all agent configuration.

Override any value via environment variable (e.g. GROQ_MODEL, MAX_ITERATIONS).
"""

import os
import pathlib

# ── Anchor the sandbox to the project directory ──────────────────────────────
# Set AGENT_ROOT to the directory that contains main.py.
# This MUST happen before any functions/_pathguard.py call so the sandbox
# root is stable regardless of which directory the user runs `python main.py` from.
_PROJECT_ROOT = str(pathlib.Path(__file__).parent.parent.resolve())
os.environ.setdefault("AGENT_ROOT", _PROJECT_ROOT)

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

## Your sandbox
All files live inside a workspace directory. You can read, write, and execute
files anywhere inside it, including nested subdirectories.

## Tools
- get_files_info(directory=".", depth=2)  — tree listing of the workspace
- get_file_content(file_path)             — read any file
- write_file(file_path, content)          — create or overwrite any file
- run_python_file(file_path, args=[])     — execute a .py file

## Path rules — READ THIS CAREFULLY
1. Always use RELATIVE paths from the workspace root. Examples:
     CORRECT: "pkg/calculator.py"
     CORRECT: "src/utils/helper.py"
     CORRECT: "main.py"
     WRONG:   "/workspace/pkg/calculator.py"   ← never use absolute paths
     WRONG:   "./pkg/calculator.py"            ← omit the leading ./

2. Nested directories are fully supported. You can:
     - read  "a/b/c/file.py"
     - write "new_pkg/module.py"  (directories are created automatically)
     - run   "tests/test_calc.py"

3. Before accessing a file you haven't seen yet, ALWAYS call get_files_info
   first so you know the exact relative path. Never guess file locations.

4. If you see a directory listed (e.g. "pkg/"), call get_files_info("pkg")
   to see what's inside before trying to read files from it.

## Workflow
1. Call get_files_info(".") to understand the workspace structure.
2. Use the exact paths shown in the → "path" column of the listing.
3. Read files before modifying them.
4. After writing, confirm by reading back or running the file.
5. When done, summarise exactly what you changed.

## Error recovery
- "File not found" → call get_files_info to find the correct path.
- Tool errors → read the error message; it contains corrective hints.
- Never give up after one failure; investigate and retry.
"""
