from __future__ import annotations

from pathlib import Path

from .context_inspector import ProjectContext
from .registry import ProjectRegistry


def _entry_point(ctx: ProjectContext) -> Path:
    registry = ProjectRegistry(ctx)
    return registry.default_entrypoint()


def generate_project_launcher_ps1(ctx: ProjectContext) -> str:
    venv_path = ctx.venv or (ctx.root / ".venv")
    python_path = venv_path / "Scripts" / "python.exe"
    entry_point = _entry_point(ctx)
    lines = [
        "$ErrorActionPreference = 'Stop'",
        f"$projectRoot = '{ctx.root.as_posix()}'",
        f"$venvPath = '{venv_path.as_posix()}'",
        "if (-not (Test-Path \"$venvPath/Scripts/python.exe\")) {",
        "    python -m venv $venvPath",
        "}",
        "& \"$venvPath/Scripts/Activate.ps1\"",
        f"& \"{python_path.as_posix()}\" \"{entry_point.as_posix()}\"",
        "pause",
        "",
    ]
    return "`n".join(lines)


def _as_windows_path(path: Path) -> str:
    return str(path).replace("/", "\\")


def generate_project_launcher_bat(ctx: ProjectContext) -> str:
    venv_path = ctx.venv or (ctx.root / ".venv")
    entry_point = _entry_point(ctx)
    lines = [
        "@echo off",
        "setlocal enableextensions",
        f"set \"PROJECT_ROOT={_as_windows_path(ctx.root)}\"",
        f"set \"VENV_PATH={_as_windows_path(venv_path)}\"",
        "if not exist \"%VENV_PATH%\\Scripts\\python.exe\" (",
        "    python -m venv \"%VENV_PATH%\"",
        ")",
        "call \"%VENV_PATH%\\Scripts\\activate.bat\"",
        f"python \"{_as_windows_path(entry_point)}\"",
        "pause",
        "",
    ]
    return "\r\n".join(lines)


def write_launcher(ctx: ProjectContext, output: Path) -> None:
    output.write_text(generate_project_launcher_ps1(ctx), encoding="utf-8")
    bat_path = output.with_suffix(".bat")
    bat_path.write_text(generate_project_launcher_bat(ctx), encoding="utf-8")
