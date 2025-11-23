from __future__ import annotations

import ast
import importlib.util
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, Sequence

from .context_inspector import ProjectContext
from .env_utils import build_env_for_context, resolve_executable


@dataclass
class Issue:
    path: Path
    line: int
    column: int
    message: str
    kind: str = "error"


@dataclass
class ImportStatus:
    module: str
    present: bool
    resolved_path: Path | None


@dataclass
class ImportReport:
    target: Path
    statuses: Sequence[ImportStatus]

    @property
    def missing(self) -> list[ImportStatus]:
        return [status for status in self.statuses if not status.present]


def check_syntax(path: Path) -> Sequence[Issue]:
    text = path.read_text(encoding="utf-8")
    try:
        ast.parse(text, filename=str(path))
        return []
    except SyntaxError as e:  # pragma: no cover - simple mapping
        return [
            Issue(
                path=path,
                line=e.lineno or 0,
                column=e.offset or 0,
                message=e.msg,
                kind="syntax",
            )
        ]


def _run_in_venv(cmd: list[str], ctx: ProjectContext) -> subprocess.CompletedProcess:
    return subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        encoding="utf-8",
        env=build_env_for_context(ctx),
        cwd=ctx.root,
    )


def run_ruff(path: Path, ctx: ProjectContext) -> str:
    cmd = [resolve_executable("ruff", ctx), "check", str(path)]
    result = _run_in_venv(cmd, ctx)
    return (result.stdout or "") + (result.stderr or "")


def lint_with_ruff(ctx: ProjectContext, targets: Iterable[Path] | None = None, fix: bool = False) -> str:
    target_args = [str(path) for path in (targets or [ctx.root])]
    cmd = [resolve_executable("ruff", ctx), "check", *target_args]
    if fix:
        cmd.append("--fix")
    result = _run_in_venv(cmd, ctx)
    combined = (result.stdout or "") + (result.stderr or "")
    if result.returncode == 0 and not combined.strip():
        return "Ruff check passed with no findings."
    return combined


def _resolve_local_module(module: str, ctx: ProjectContext) -> Path | None:
    dotted = module.replace(".", "/")
    file_candidate = ctx.root / f"{dotted}.py"
    if file_candidate.exists():
        return file_candidate
    package_candidate = ctx.root / dotted
    init_file = package_candidate / "__init__.py"
    if init_file.exists():
        return init_file
    return None


def analyze_imports(path: Path, ctx: ProjectContext) -> ImportReport:
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    modules: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                modules.add(alias.name.split(".")[0])
        elif isinstance(node, ast.ImportFrom):
            if node.level == 0 and node.module:
                modules.add(node.module.split(".")[0])

    statuses = []
    for module in sorted(modules):
        resolved = _resolve_local_module(module, ctx)
        present = resolved is not None or importlib.util.find_spec(module) is not None
        statuses.append(ImportStatus(module=module, present=present, resolved_path=resolved))
    return ImportReport(target=path, statuses=statuses)


def format_import_report(report: ImportReport) -> str:
    lines = [f"Import analysis for {report.target}:"]
    for status in report.statuses:
        if status.present:
            if status.resolved_path is not None:
                lines.append(f"  ✓ {status.module} -> {status.resolved_path}")
            else:
                lines.append(f"  ✓ {status.module} (available in interpreter)")
        else:
            lines.append(f"  ✗ {status.module} (not found in project; install or add path)")
    missing = report.missing
    if missing:
        lines.append("")
        lines.append("Missing modules detected. Consider pip installing or verifying local packages:")
        for status in missing:
            lines.append(f"  - {status.module}")
    return "\n".join(lines)
