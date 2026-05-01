"""
functions/get_files_info.py — List files in a sandboxed directory.
"""

import os


def get_files_info(working_directory: str, directory: str = ".") -> str:
    """
    List entries in `directory`, which must be inside `working_directory`.

    Returns a human-readable string. Never raises — errors are returned as
    error strings so the agent can read and act on them.
    """
    try:
        working_dir_abs = os.path.abspath(working_directory)
        target_dir = os.path.normpath(os.path.join(working_dir_abs, directory))

        # ── Path traversal guard ──────────────────────────────────────────────
        if not _is_safe_path(working_dir_abs, target_dir):
            return (
                f'Error: Cannot list "{directory}" — path is outside the '
                f"permitted working directory."
            )

        if not os.path.isdir(target_dir):
            return f'Error: "{directory}" is not a directory.'

        items = os.listdir(target_dir)
        if not items:
            return f'Directory "{directory}" is empty.'

        lines: list[str] = []
        for item in sorted(items):
            item_path = os.path.join(target_dir, item)
            try:
                size = os.path.getsize(item_path)
                suffix = "/" if os.path.isdir(item_path) else ""
                lines.append(f"  {item}{suffix}  ({size} bytes)")
            except OSError as e:
                lines.append(f"  {item}  [error: {e}]")

        return f"Contents of '{directory}':\n" + "\n".join(lines)

    except Exception as e:
        return f"Error listing directory: {e}"


def _is_safe_path(base: str, target: str) -> bool:
    """Return True only if target is inside (or equal to) base."""
    try:
        return os.path.commonpath([base, target]) == base
    except ValueError:
        # Different drives on Windows
        return False
