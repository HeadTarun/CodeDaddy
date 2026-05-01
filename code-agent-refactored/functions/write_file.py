"""
functions/write_file.py — Write a file inside the sandbox.

Supports deeply nested paths; parent directories are created automatically.
"""

from __future__ import annotations
import os
from agent.config import MAX_FILE_WRITE_BYTES
from functions._pathguard import resolve_safe_path, PathEscapeError


def write_file(working_directory: str, file_path: str, content: str) -> str:
    """
    Write `content` to `file_path` (relative to sandbox root).

    - Nested paths like "pkg/new_module.py" or "src/a/b/c/file.py" are supported.
    - Parent directories are created automatically.
    - Refuses to overwrite directories.
    - Enforces MAX_FILE_WRITE_BYTES limit.
    """
    try:
        target_path = resolve_safe_path(working_directory, file_path)
    except PathEscapeError as e:
        return f"Error: {e}"
    except Exception as e:
        return f"Error resolving path: {e}"

    if os.path.isdir(target_path):
        return f'Error: "{file_path}" is a directory. Provide a file path, not a directory.'

    encoded = content.encode("utf-8")
    if len(encoded) > MAX_FILE_WRITE_BYTES:
        return (
            f"Error: Content is {len(encoded):,} bytes which exceeds the "
            f"{MAX_FILE_WRITE_BYTES:,} byte limit."
        )

    # Auto-create all intermediate directories (e.g. pkg/, src/utils/)
    parent = os.path.dirname(target_path)
    try:
        os.makedirs(parent, exist_ok=True)
    except OSError as e:
        return f'Error creating directories for "{file_path}": {e}'

    try:
        with open(target_path, "w", encoding="utf-8") as f:
            f.write(content)
    except OSError as e:
        return f'Error writing "{file_path}": {e}'

    return (
        f'Successfully wrote "{file_path}" '
        f"({len(encoded):,} bytes, {content.count(chr(10))+1} lines)."
    )
