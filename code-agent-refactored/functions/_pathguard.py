"""
functions/_pathguard.py — Centralised, tested path resolution for the sandbox.

ALL filesystem functions must call resolve_safe_path() instead of doing their
own os.path.join / abspath / commonpath logic.  Having one place makes it easy
to audit and impossible to diverge between functions.
"""

from __future__ import annotations
import os


class PathEscapeError(ValueError):
    """Raised when a requested path would escape the sandbox."""


def resolve_safe_path(working_directory: str, user_path: str) -> str:
    """
    Resolve `user_path` relative to `working_directory` and verify it stays
    inside the sandbox.

    Rules
    -----
    - working_directory is converted to an absolute path anchored to the
      *script's* directory (via AGENT_ROOT), NOT the shell's CWD.  This means
      the sandbox is stable regardless of where the user runs `python main.py`.
    - user_path may be:
        - a flat name:          "file.py"
        - a nested relative:    "pkg/calculator.py"
        - a dot-prefixed:       "./src/utils/helper.py"
        - deeply nested:        "a/b/c/d/e/file.py"
    - Anything that resolves outside the sandbox raises PathEscapeError.
    - Absolute paths supplied by the LLM (e.g. "/etc/passwd") are REJECTED.

    Returns
    -------
    str — the fully-resolved absolute path, guaranteed to be inside the sandbox.

    Raises
    ------
    PathEscapeError — if the path escapes the sandbox.
    ValueError      — if working_directory itself cannot be resolved.
    """
    # ── 1. Resolve sandbox root, anchored to AGENT_ROOT env var or script dir ─
    agent_root = os.environ.get("AGENT_ROOT", "")
    if not agent_root:
        # Fallback: directory of this file → project root → workspace
        agent_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    # working_directory may be absolute OR relative-to-agent-root
    if os.path.isabs(working_directory):
        sandbox = os.path.normpath(working_directory)
    else:
        sandbox = os.path.normpath(os.path.join(agent_root, working_directory))

    # ── 2. Reject absolute user paths immediately ──────────────────────────────
    # The LLM should never supply "/etc/passwd" — catch it before join() makes
    # it look like a valid nested path.
    if os.path.isabs(user_path):
        raise PathEscapeError(
            f"Absolute paths are not allowed: {user_path!r}. "
            f"Use a relative path like 'pkg/file.py'."
        )

    # ── 3. Resolve target path ────────────────────────────────────────────────
    target = os.path.normpath(os.path.join(sandbox, user_path))

    # ── 4. Sandbox boundary check ─────────────────────────────────────────────
    # Add os.sep to sandbox so that /workspace doesn't match /workspace-evil
    sandbox_with_sep = sandbox if sandbox.endswith(os.sep) else sandbox + os.sep
    if not (target == sandbox or target.startswith(sandbox_with_sep)):
        raise PathEscapeError(
            f"Path {user_path!r} resolves outside the permitted working "
            f"directory. Only paths inside the sandbox are allowed."
        )

    return target


def sandbox_root(working_directory: str) -> str:
    """Return the absolute sandbox root (convenience wrapper)."""
    return resolve_safe_path(working_directory, ".")
