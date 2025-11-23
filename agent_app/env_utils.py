from __future__ import annotations

import os
from .context_inspector import ProjectContext


def build_env_for_context(ctx: ProjectContext) -> dict[str, str]:
    """Return an environment dict that respects the project's venv."""

    env = os.environ.copy()
    if ctx.venv is not None:
        scripts = ctx.venv / "Scripts"
        env["PATH"] = f"{scripts};{env.get('PATH', '')}"
        env["VIRTUAL_ENV"] = str(ctx.venv)
    return env


def resolve_executable(executable: str, ctx: ProjectContext) -> str:
    """Resolve an executable within the project's venv if one exists."""

    if ctx.venv is not None:
        candidate = ctx.venv / "Scripts" / f"{executable}.exe"
        if candidate.exists():
            return str(candidate)
    return executable
