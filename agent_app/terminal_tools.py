from __future__ import annotations

import os
import re
import shlex
import subprocess
import time
from dataclasses import dataclass
from typing import Sequence

from .context_inspector import ProjectContext
from .env_utils import build_env_for_context


@dataclass(slots=True)
class CommandAssessment:
    status: str  # "allow", "confirm", "block"
    reason: str | None = None


@dataclass(slots=True)
class CommandRunResult:
    command: Sequence[str]
    returncode: int
    stdout: str
    stderr: str
    duration: float


_IS_WINDOWS = os.name == "nt"


class CommandSafetyChecker:
    """Lightweight heuristic guardrail for terminal commands."""

    _BLOCKED = {
        "format",
        "mkfs",
        "diskpart",
        "shutdown",
        "reboot",
    }
    _CONFIRM_COMMANDS = {
        "rm",
        "del",
        "erase",
        "mv",
        "move",
        "chmod",
        "chown",
        "attrib",
        "pip",
        "npm",
        "conda",
    }

    def assess(self, argv: Sequence[str]) -> CommandAssessment:
        if not argv:
            return CommandAssessment(status="block", reason="No command provided")
        cmd = argv[0].lower().strip()
        if cmd in self._BLOCKED:
            return CommandAssessment(status="block", reason=f"'{cmd}' is blocked")
        if cmd in self._CONFIRM_COMMANDS:
            return CommandAssessment(
                status="confirm", reason=f"'{cmd}' is destructive or modifies environment"
            )
        return CommandAssessment(status="allow")


_CONFIRMATION_PATTERN = re.compile(
    r"confirm(?:ed)?[:\s]+(yes|ok|true|1)\b", re.IGNORECASE
)


def strip_confirmation(text: str) -> tuple[str, bool]:
    """Remove confirmation keywords and return (cleaned_text, was_confirmed)."""
    if not text:
        return text, False
    match = _CONFIRMATION_PATTERN.search(text)
    if not match:
        return text, False
    cleaned = text[: match.start()] + text[match.end() :]
    return cleaned.strip(), True


def parse_command_text(text: str) -> list[str]:
    """Return argv parsed from the provided command text."""
    argv = shlex.split(text, posix=not _IS_WINDOWS)
    if not argv:
        raise ValueError("No executable provided")
    return argv


def run_shell_command(argv: Sequence[str], ctx: ProjectContext) -> CommandRunResult:
    start = time.perf_counter()
    try:
        completed = subprocess.run(  # nosec - command vetted by guardrails
            list(argv),
            cwd=ctx.root,
            env=build_env_for_context(ctx),
            capture_output=True,
            text=True,
            encoding="utf-8",
            shell=False,
        )
    except FileNotFoundError as exc:  # pragma: no cover - surfaced to caller
        raise RuntimeError(f"Executable not found: {argv[0]}") from exc
    duration = time.perf_counter() - start
    return CommandRunResult(
        command=list(argv),
        returncode=completed.returncode,
        stdout=completed.stdout,
        stderr=completed.stderr,
        duration=duration,
    )
