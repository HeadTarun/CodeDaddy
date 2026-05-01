"""
functions/get_file_content.py — Read a file inside the sandbox.
"""

from __future__ import annotations
import os
from agent.config import MAX_FILE_READ_CHARS
from functions._pathguard import resolve_safe_path, PathEscapeError


def get_file_content(working_directory: str, file_path: str) -> str:
    """
    Read `file_path` (relative to sandbox root) and return its text content.

    Supports nested paths: "pkg/calculator.py", "src/utils/helper.py", etc.
    Files larger than MAX_FILE_READ_CHARS are truncated with a clear notice.
    """
    try:
        target_path = resolve_safe_path(working_directory, file_path)
    except PathEscapeError as e:
        return f"Error: {e}"
    except Exception as e:
        return f"Error resolving path: {e}"

    if not os.path.exists(target_path):
        # Give the LLM a helpful hint so it can correct its path
        return (
            f'Error: File not found: "{file_path}". '
            f'Tip: Use get_files_info(".") to list available files and their exact paths.'
        )

    if not os.path.isfile(target_path):
        return (
            f'Error: "{file_path}" is a directory, not a file. '
            f'Use get_files_info("{file_path}") to list its contents.'
        )

    file_size = os.path.getsize(target_path)
    if file_size == 0:
        return f'File "{file_path}" exists but is empty.'

    try:
        with open(target_path, "r", encoding="utf-8", errors="replace") as f:
            content = f.read(MAX_FILE_READ_CHARS)
            truncated = bool(f.read(1))
    except OSError as e:
        return f'Error reading "{file_path}": {e}'

    if truncated:
        content += (
            f'\n\n[File truncated at {MAX_FILE_READ_CHARS} chars. '
            f'Total size: {file_size} bytes]'
        )

    return content
