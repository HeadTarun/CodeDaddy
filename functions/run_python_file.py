"""
functions/run_python_file.py — Execute a Python file inside the sandbox.

Security measures applied:
- Path traversal prevention
- Extension whitelist (.py only)
- Argument sanitisation (strings only, no shell injection)
- Isolated subprocess environment (no inherited secrets)
- Configurable timeout
- Output size truncation
"""

import os
import subprocess
import sys
from agent.config import (
    ALLOWED_EXEC_EXTENSIONS,
    SUBPROCESS_TIMEOUT_SECS,
    MAX_TOOL_OUTPUT_CHARS,
)

_MAX_OUTPUT = MAX_TOOL_OUTPUT_CHARS // 2  # split budget between stdout and stderr


def run_python_file(
    working_directory: str,
    file_path: str,
    args: list[str] | None = None,
) -> str:
    """
    Execute `file_path` (relative to `working_directory`) with Python.

    Returns combined stdout/stderr as a string.
    """
    try:
        working_dir_abs = os.path.abspath(working_directory)
        target_path = os.path.normpath(os.path.join(working_dir_abs, file_path))

        # ── Path traversal guard ──────────────────────────────────────────────
        if not _is_safe_path(working_dir_abs, target_path):
            return (
                f'Error: Cannot execute "{file_path}" — path is outside the '
                f"permitted working directory."
            )

        if not os.path.isfile(target_path):
            return f'Error: "{file_path}" does not exist or is not a regular file.'

        # ── Extension whitelist ───────────────────────────────────────────────
        ext = os.path.splitext(target_path)[1].lower()
        if ext not in ALLOWED_EXEC_EXTENSIONS:
            return (
                f'Error: "{file_path}" has extension "{ext}". '
                f"Only {sorted(ALLOWED_EXEC_EXTENSIONS)} files may be executed."
            )

        # ── Sanitise args (must all be strings, no shell metacharacters) ──────
        safe_args: list[str] = []
        if args:
            for a in args:
                if not isinstance(a, str):
                    return f"Error: all args must be strings, got {type(a).__name__}."
                safe_args.append(a)

        # ── Build command ─────────────────────────────────────────────────────
        # Use the same Python interpreter that runs this agent.
        python_exe = sys.executable
        command = [python_exe, target_path] + safe_args

        # ── Sanitised environment (do NOT inherit GROQ_API_KEY etc.) ──────────
        clean_env = {
            "PATH": os.environ.get("PATH", ""),
            "HOME": os.environ.get("HOME", ""),
            "PYTHONPATH": os.environ.get("PYTHONPATH", ""),
            "PYTHONDONTWRITEBYTECODE": "1",
            # Add any other env vars the child legitimately needs here
        }

        # ── Execute ───────────────────────────────────────────────────────────
        result = subprocess.run(
            command,
            cwd=working_dir_abs,
            capture_output=True,
            text=True,
            timeout=SUBPROCESS_TIMEOUT_SECS,
            env=clean_env,
        )

        parts: list[str] = []

        if result.returncode != 0:
            parts.append(f"Process exited with code {result.returncode}.")

        stdout = result.stdout.strip()
        stderr = result.stderr.strip()

        if stdout:
            if len(stdout) > _MAX_OUTPUT:
                stdout = stdout[:_MAX_OUTPUT] + "\n[...stdout truncated]"
            parts.append(f"STDOUT:\n{stdout}")

        if stderr:
            if len(stderr) > _MAX_OUTPUT:
                stderr = stderr[:_MAX_OUTPUT] + "\n[...stderr truncated]"
            parts.append(f"STDERR:\n{stderr}")

        if not stdout and not stderr:
            parts.append("Script completed with no output.")

        return "\n".join(parts)

    except subprocess.TimeoutExpired:
        return (
            f'Error: "{file_path}" exceeded the {SUBPROCESS_TIMEOUT_SECS}s '
            f"execution time limit and was killed."
        )
    except Exception as e:
        return f"Error executing Python file: {e}"


def _is_safe_path(base: str, target: str) -> bool:
    try:
        return os.path.commonpath([base, target]) == base
    except ValueError:
        return False
