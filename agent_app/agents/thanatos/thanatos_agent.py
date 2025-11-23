from __future__ import annotations

from typing import Sequence

from agent_app.output_sanitizer import OutputSanitizer, should_reject_output, wrap_terminal_output
from agent_app.terminal_tools import (
    CommandRunResult,
    CommandSafetyChecker,
    parse_command_text,
    run_shell_command,
    strip_confirmation,
)
from agent_app.types import RiskLevel

from ..base import AgentRequest, AgentResult, ToolLimitedAgent


class ThanatosAgent(ToolLimitedAgent):
    name = "terminal_ops"
    description = "Runs safe terminal commands, env checks, and package installs with confirmation."
    allowed_tools = ("shell_exec", "process_inspector")
    guardrails = (
        "Requires confirmation for destructive commands (rm/mv/chmod/chown).",
        "Requires confirmation for package installs.",
        "Defaults to dry-run when supported.",
    )

    def __init__(self) -> None:
        super().__init__()
        self._safety = CommandSafetyChecker()
        self._sanitizer = OutputSanitizer()

    def handle(self, request: AgentRequest) -> AgentResult:
        argv, confirmed, error = self._extract_command(request.task)
        if argv is None:
            return AgentResult(output=error or "No command provided.", success=False)

        assessment = self._safety.assess(argv)
        if assessment.status == "block":
            return AgentResult(
                output=f"Command blocked: {assessment.reason}",
                success=False,
                blocked=True,
                metadata={"command": argv},
            )
        if assessment.status == "confirm" and not confirmed:
            return AgentResult(
                output=(
                    f"Command '{argv[0]}' requires confirmation ({assessment.reason}). "
                    "Re-run the request with 'confirm: yes' appended to proceed."
                ),
                success=False,
                confirmation_required=True,
                confirmation_reason=assessment.reason,
                metadata={"command": argv},
            )

        try:
            run_result = run_shell_command(argv, request.context)
        except RuntimeError as exc:
            return AgentResult(
                output=str(exc),
                success=False,
                metadata={"command": argv},
            )

        # Safety net: Check if output should be rejected
        combined_output = run_result.stdout + run_result.stderr
        should_reject, reject_reason = should_reject_output(combined_output)
        if should_reject:
            return AgentResult(
                output=f"OUTPUT REJECTED: {reject_reason}\n\nDo you want a digest instead?",
                success=False,
                blocked=True,
                metadata={"command": argv, "rejection_reason": reject_reason},
            )

        metadata = {
            "command": run_result.command,
            "returncode": run_result.returncode,
            "duration_seconds": run_result.duration,
        }
        if assessment.reason:
            metadata["safety_reason"] = assessment.reason
        return AgentResult(
            output=self._format_run_output(run_result),
            success=run_result.returncode == 0,
            metadata=metadata,
        )

    def _extract_command(self, task: str) -> tuple[Sequence[str] | None, bool, str | None]:
        cleaned, confirmed = strip_confirmation(task)
        raw = self._find_command_text(cleaned)
        if raw is None:
            raw = cleaned.strip()
        if not raw:
            return None, confirmed, (
                "Specify a command using 'run <cmd>' or 'command: <cmd>'."
            )
        try:
            argv = parse_command_text(raw)
        except ValueError as exc:
            return None, confirmed, f"Unable to parse command: {exc}"
        return argv, confirmed, None

    def _find_command_text(self, task: str) -> str | None:
        lines = [line.strip() for line in task.strip().splitlines() if line.strip()]
        if not lines:
            return None
        for idx, line in enumerate(lines):
            lowered = line.lower()
            for keyword in ("run", "execute"):
                prefix = f"{keyword} "
                if lowered.startswith(prefix):
                    return line[len(prefix) :].strip("` ")
            for keyword in ("command", "cmd"):
                for separator in (":", "="):
                    marker = f"{keyword}{separator}"
                    if lowered.startswith(marker):
                        payload = line[len(marker) :].strip()
                        if payload:
                            return payload.strip("` ")
                        return self._next_nonempty_line(lines, idx + 1)
        return None

    def _next_nonempty_line(self, lines: Sequence[str], start: int) -> str | None:
        for line in lines[start:]:
            lowered = line.lower()
            if lowered.startswith("confirm"):
                continue
            candidate = line.strip("` ")
            if candidate:
                return candidate
        return None

    def _format_run_output(self, result: CommandRunResult) -> str:
        cmd_display = " ".join(result.command)
        header = f"Command: {cmd_display}\nReturn code: {result.returncode} in {result.duration:.2f}s"
        
        # Safety net: Sanitize and wrap outputs
        stdout = self._sanitizer.sanitize_terminal_output(result.stdout.strip())
        stderr = self._sanitizer.sanitize_terminal_output(result.stderr.strip())
        
        if stdout and stderr:
            body = f"<terminal_output begin>\nSTDOUT:\n{stdout}\n\nSTDERR:\n{stderr}\n<terminal_output end>"
        elif stdout:
            body = f"<terminal_output begin>\nSTDOUT:\n{stdout}\n<terminal_output end>"
        elif stderr:
            body = f"<terminal_output begin>\nSTDERR:\n{stderr}\n<terminal_output end>"
        else:
            body = "(No output)"
        return f"{header}\n{body}"
