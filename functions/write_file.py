"""
functions/write_file.py — Write a file inside the sandbox.
"""

import os
from agent.config import MAX_FILE_WRITE_BYTES


def write_file(working_directory: str, file_path: str, content: str) -> str:
    """
    Write `content` to `file_path` (relative to `working_directory`).

    Safety:
    - Path traversal prevention (commonpath check)
    - Refuses to write to directories
    - Enforces a maximum content size (MAX_FILE_WRITE_BYTES)
    - Creates parent directories as needed
    """
    try:
        working_dir_abs = os.path.abspath(working_directory)
        target_path = os.path.normpath(os.path.join(working_dir_abs, file_path))

        # ── Path traversal guard ──────────────────────────────────────────────
        if not _is_safe_path(working_dir_abs, target_path):
            return (
                f'Error: Cannot write to "{file_path}" — path is outside the '
                f"permitted working directory."
            )

        # ── Refuse to overwrite a directory ───────────────────────────────────
        if os.path.isdir(target_path):
            return f'Error: "{file_path}" is a directory, not a file.'

        # ── Content size guard ────────────────────────────────────────────────
        encoded = content.encode("utf-8")
        if len(encoded) > MAX_FILE_WRITE_BYTES:
            return (
                f"Error: Content too large ({len(encoded)} bytes). "
                f"Maximum allowed: {MAX_FILE_WRITE_BYTES} bytes."
            )

        # ── Create parent directories ─────────────────────────────────────────
        parent = os.path.dirname(target_path)
        if parent:
            os.makedirs(parent, exist_ok=True)

        # ── Write ─────────────────────────────────────────────────────────────
        with open(target_path, "w", encoding="utf-8") as f:
            f.write(content)

        return (
            f'Successfully wrote to "{file_path}" '
            f"({len(encoded)} bytes, {len(content)} chars)."
        )

    except OSError as e:
        return f"Error writing file: {e}"
    except Exception as e:
        return f"Error: {e}"


def _is_safe_path(base: str, target: str) -> bool:
    try:
        return os.path.commonpath([base, target]) == base
    except ValueError:
        return False
