"""
functions/get_files_info.py — List sandbox directory contents with optional recursion.

The LLM needs to see nested structure in ONE call so it can form correct paths
like "pkg/calculator.py" without guessing.  depth=2 (default) exposes two
levels of nesting; increase to 3 for deeper projects.
"""

from __future__ import annotations
import os
from functions._pathguard import resolve_safe_path, PathEscapeError, sandbox_root


def get_files_info(
    working_directory: str,
    directory: str = ".",
    depth: int = 2,
) -> str:
    """
    List the contents of `directory` (relative to sandbox root).

    Parameters
    ----------
    working_directory : str
        Sandbox root — injected by the dispatcher, never from the LLM.
    directory : str
        Relative path to the directory to list.  Defaults to "." (sandbox root).
    depth : int
        How many levels deep to recurse.  1 = flat, 2 = one sub-level, etc.
        Capped at 5 to prevent enormous outputs.

    Returns a tree-style listing the LLM can use to construct correct file paths.

    Example output
    --------------
    workspace/
    ├── pkg/
    │   ├── calculator.py  [342 B]  → "pkg/calculator.py"
    │   └── render.py      [128 B]  → "pkg/render.py"
    ├── main.py            [768 B]  → "main.py"
    └── tests.py          [1401 B]  → "tests.py"
    """
    depth = max(1, min(depth, 5))  # clamp 1–5

    try:
        target_dir = resolve_safe_path(working_directory, directory)
    except PathEscapeError as e:
        return f"Error: {e}"
    except Exception as e:
        return f"Error resolving path: {e}"

    if not os.path.isdir(target_dir):
        return (
            f'Error: "{directory}" is not a directory. '
            f'Use get_files_info(".") to list the workspace root.'
        )

    root_abs = sandbox_root(working_directory)

    lines: list[str] = []
    rel_label = os.path.relpath(target_dir, root_abs)
    header = "workspace/" if rel_label == "." else f"workspace/{rel_label}/"
    lines.append(header)

    _walk_tree(target_dir, root_abs, lines, current_depth=1, max_depth=depth, prefix="")

    if len(lines) == 1:
        lines.append("  (empty directory)")

    return "\n".join(lines)


def _walk_tree(
    dir_path: str,
    root_abs: str,
    lines: list[str],
    current_depth: int,
    max_depth: int,
    prefix: str,
) -> None:
    """Recursively build a tree listing into `lines`."""
    try:
        entries = sorted(os.listdir(dir_path))
    except PermissionError:
        lines.append(f"{prefix}  [permission denied]")
        return

    for i, entry in enumerate(entries):
        entry_path = os.path.join(dir_path, entry)
        is_last = i == len(entries) - 1
        connector = "└── " if is_last else "├── "
        child_prefix = prefix + ("    " if is_last else "│   ")

        if os.path.isdir(entry_path):
            lines.append(f"{prefix}{connector}{entry}/")
            if current_depth < max_depth:
                _walk_tree(
                    entry_path, root_abs, lines,
                    current_depth + 1, max_depth, child_prefix,
                )
            else:
                try:
                    n = len(os.listdir(entry_path))
                    if n:
                        lines.append(
                            f"{child_prefix}... ({n} items — "
                            f'call get_files_info("{os.path.relpath(entry_path, root_abs)}")'
                            f" to expand)"
                        )
                except OSError:
                    pass
        else:
            try:
                size = _human_size(os.path.getsize(entry_path))
            except OSError:
                size = "?"
            rel_path = os.path.relpath(entry_path, root_abs)
            lines.append(f'{prefix}{connector}{entry}  [{size}]  → "{rel_path}"')


def _human_size(n: int) -> str:
    for unit in ("B", "KB", "MB"):
        if n < 1024:
            return f"{n} {unit}"
        n //= 1024
    return f"{n} GB"
