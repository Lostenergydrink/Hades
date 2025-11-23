from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, Sequence

from .context_inspector import ProjectContext


# Directories to ignore during recursive file discovery
IGNORE_DIRS = frozenset(
    (
        ".venv",
        "venv",
        "env",
        ".env",
        "node_modules",
        "__pycache__",
        ".git",
        ".pytest_cache",
        ".mypy_cache",
        ".ruff_cache",
        ".tox",
        "dist",
        "build",
        ".eggs",
        "*.egg-info",
        ".apex",  # Our own checkpoint/state directory
    )
)


@dataclass(slots=True)
class RegistrySummary:
    root: Path
    venv: Path | None
    requirements: Path | None
    recent_python: Sequence[Path]

    def to_lines(self) -> list[str]:
        lines = [f"root: {self.root}"]
        if self.venv:
            lines.append(f"venv: {self.venv}")
        if self.requirements:
            lines.append(f"requirements: {self.requirements}")
        if self.recent_python:
            lines.append("recent python files:")
            for path in self.recent_python:
                lines.append(f"  - {path}")
        return lines


class ProjectRegistry:
    """Cache of cheap project metadata shared across agents."""

    def __init__(self, context: ProjectContext) -> None:
        self._context = context
        self._python_cache: list[Path] | None = None

    @property
    def context(self) -> ProjectContext:
        return self._context

    @property
    def root(self) -> Path:
        return self._context.root

    def default_entrypoint(self) -> Path:
        """Returns the canonical python entry point for the project."""

        preferred_names = (
            "main.py",
            "app.py",
            "webui.py",
            f"{self.root.name}.py",
            "launch.py",
            "run.py",
        )
        for name in preferred_names:
            candidate = self.root / name
            if candidate.exists():
                return candidate
        python_files = self.recent_python_files(limit=1)
        if python_files:
            return python_files[0]
        raise FileNotFoundError("Unable to determine entry point; no python files discovered.")

    def recent_python_files(self, limit: int = 10) -> list[Path]:
        if self._python_cache is None:
            files = []
            for path in self.root.rglob("*.py"):
                # Skip files in ignored directories
                if any(part in IGNORE_DIRS for part in path.parts):
                    continue
                files.append(path)
            files.sort(key=lambda path: path.stat().st_mtime, reverse=True)
            self._python_cache = files
        return self._python_cache[:limit]

    def summary(self, limit: int = 5) -> RegistrySummary:
        return RegistrySummary(
            root=self.root,
            venv=self._context.venv,
            requirements=self._context.requirements,
            recent_python=self.recent_python_files(limit=limit),
        )

    def as_relative(self, path: Path) -> str:
        try:
            return str(path.relative_to(self.root))
        except ValueError:
            return str(path)
