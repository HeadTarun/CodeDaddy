"""
functions/run_python_file.py — Execute a Python file inside the sandbox.

Security:
- Path traversal prevention via centralised _pathguard
- Extension whitelist (.py only)
- Sanitised subprocess environment (no inherited API keys)
- Configurable timeout
- Output size cap
"""

from __future__ import annotations
import os
import subprocess
import sys
from agent.config import (
    ALLOWED_EXEC_EXTENSIONS,
    SUBPROCESS_TIMEOUT_SECS,
    MAX_TOOL_OUTPUT_CHARS,
)
from functions._pathguard import resolve_safe_path, PathEscapeError, sandbox_root

_MAX_HALF = MAX_TOOL_OUTPUT_CHARS // 2  # budget split between stdout and stderr


def run_python_file(
    working_directory: str,
    file_path: str,
    args: list[str] | None = None,
) -> str:
    """
    Execute `file_path` (relative to sandbox root) with the current Python interpreter.

    Supports nested paths: "pkg/main.py", "src/tests/test_calc.py", etc.
    The subprocess's cwd is set to the sandbox root so relative imports work.
    """
    try:
        target_path = resolve_safe_path(working_directory, file_path)
    except PathEscapeError as e:
        return f"Error: {e}"
    except Exception as e:
        return f"Error resolving path: {e}"

    if not os.path.exists(target_path):
        return (
            f'Error: File not found: "{file_path}". '
            f'Use get_files_info(".") to list available files.'
        )

    if not os.path.isfile(target_path):
        return f'Error: "{file_path}" is not a regular file.'

    ext = os.path.splitext(target_path)[1].lower()
    if ext not in ALLOWED_EXEC_EXTENSIONS:
        return (
            f'Error: Cannot execute "{file_path}" — only '
            f'{sorted(ALLOWED_EXEC_EXTENSIONS)} files are allowed.'
        )

    # Validate args
    safe_args: list[str] = []
    for a in (args or []):
        if not isinstance(a, str):
            return f"Error: all args must be strings, got {type(a).__name__!r}."
        safe_args.append(a)

    command = [sys.executable, target_path] + safe_args

    # Sanitised env — never leak GROQ_API_KEY or other secrets
    clean_env: dict[str, str] = {k: v for k, v in {
        "PATH": os.environ.get("PATH", ""),
        "HOME": os.environ.get("HOME", ""),
        "PYTHONPATH": os.environ.get("PYTHONPATH", ""),
        "PYTHONDONTWRITEBYTECODE": "1",
        "PYTHONUTF8": "1",
    }.items() if v}

    # cwd = sandbox root so scripts can do relative imports correctly
    cwd = sandbox_root(working_directory)

    try:
        result = subprocess.run(
            command,
            cwd=cwd,
            capture_output=True,
            text=True,
            timeout=SUBPROCESS_TIMEOUT_SECS,
            env=clean_env,
        )
    except subprocess.TimeoutExpired:
        return (
            f'Error: "{file_path}" was killed after {SUBPROCESS_TIMEOUT_SECS}s '
            f"(execution time limit exceeded)."
        )
    except Exception as e:
        return f'Error launching "{file_path}": {e}'

    parts: list[str] = []

    if result.returncode != 0:
        parts.append(f"Exit code: {result.returncode}")

    stdout = result.stdout.strip()
    stderr = result.stderr.strip()

    if stdout:
        if len(stdout) > _MAX_HALF:
            stdout = stdout[:_MAX_HALF] + "\n[...stdout truncated]"
        parts.append(f"STDOUT:\n{stdout}")

    if stderr:
        if len(stderr) > _MAX_HALF:
            stderr = stderr[:_MAX_HALF] + "\n[...stderr truncated]"
        parts.append(f"STDERR:\n{stderr}")

    if not stdout and not stderr:
        parts.append("Script completed with no output.")

    return "\n".join(parts)
