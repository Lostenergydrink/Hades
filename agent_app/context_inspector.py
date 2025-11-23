from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from .config import CONFIG


PROJECT_MARKERS = {"requirements.txt", "pyproject.toml", "main.py", ".git"}


@dataclass
class ProjectContext:
    root: Path
    venv: Path | None
    requirements: Path | None


def find_project_root(start: Path | None = None) -> Path | None:
    path = start or Path.cwd()
    path = path.resolve()
    for parent in (path, *path.parents):
        if any((parent / marker).exists() for marker in PROJECT_MARKERS):
            return parent
    for candidate in CONFIG.default_projects:
        if candidate.exists():
            return candidate
    return None


def guess_venv(root: Path) -> Path | None:
    candidates = [
        CONFIG.apex_root.parent / "venvs" / f"{root.name}",
        root / ".venv",
    ]
    for base in candidates:
        scripts_dir = base / "Scripts"
        if (scripts_dir / "python.exe").exists():
            return base
    return None


def load_context(start: Path | None = None) -> ProjectContext | None:
    root = find_project_root(start)
    if root is None:
        return None
    venv = guess_venv(root)
    req = root / "requirements.txt"
    return ProjectContext(root=root, venv=venv, requirements=req if req.exists() else None)
