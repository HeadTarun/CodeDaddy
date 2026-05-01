"""
functions/get_file_content.py — Read a file inside the sandbox.
"""

import os
from agent.config import MAX_FILE_READ_CHARS


def get_file_content(working_directory: str, file_path: str) -> str:
    """
    Read `file_path` (relative to `working_directory`) and return its text content.

    Files larger than MAX_FILE_READ_CHARS are truncated with a notice.
    Binary files that cannot be decoded as UTF-8 are read with replacement chars.
    """
    try:
        working_dir_abs = os.path.abspath(working_directory)
        target_path = os.path.normpath(os.path.join(working_dir_abs, file_path))

        # ── Path traversal guard ──────────────────────────────────────────────
        if not _is_safe_path(working_dir_abs, target_path):
            return (
                f'Error: Cannot read "{file_path}" — path is outside the '
                f"permitted working directory."
            )

        if not os.path.isfile(target_path):
            return f'Error: File not found or is not a regular file: "{file_path}"'

        # ── Size sanity check (avoid reading huge binaries) ───────────────────
        file_size = os.path.getsize(target_path)
        if file_size == 0:
            return f'File "{file_path}" is empty.'

        with open(target_path, "r", encoding="utf-8", errors="replace") as f:
            content = f.read(MAX_FILE_READ_CHARS)
            truncated = bool(f.read(1))  # peek to see if there's more

        if truncated:
            content += (
                f'\n[...File "{file_path}" truncated at {MAX_FILE_READ_CHARS} chars. '
                f"Total size: {file_size} bytes]"
            )

        return content

    except Exception as e:
        return f"Error reading file: {e}"


def _is_safe_path(base: str, target: str) -> bool:
    try:
        return os.path.commonpath([base, target]) == base
    except ValueError:
        return False
