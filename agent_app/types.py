"""
Core type definitions for Hades's structured agent communication.

This module defines schemas that standardize how agents report results,
track file changes, assess risk, and communicate diagnostic information.
These types replace the ad-hoc metadata dict usage and enable reliable
multi-agent workflows with proper context passing and rollback support.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any, Literal


# ============================================================================
# Risk Assessment
# ============================================================================


class RiskLevel(str, Enum):
    """Classification of operation risk for HITL confirmation decisions."""

    SAFE = "safe"  # Read-only or trivial changes (formatting, comments)
    LOW = "low"  # Isolated changes with easy rollback (single file edits)
    MEDIUM = "medium"  # Multi-file changes or test modifications
    HIGH = "high"  # Dependency changes, config updates, or destructive ops
    CRITICAL = "critical"  # System-level commands, deletions, or git operations


# ============================================================================
# File Change Tracking
# ============================================================================


@dataclass(slots=True, frozen=True)
class FileChange:
    """Individual file modification within a ChangeManifest."""

    path: Path
    operation: Literal["create", "modify", "delete", "rename"]
    lines_added: int = 0
    lines_removed: int = 0
    old_path: Path | None = None  # For rename operations
    backup_path: Path | None = None  # Checkpoint location if snapshotted

    @property
    def is_destructive(self) -> bool:
        """Whether this change cannot be easily undone."""
        return self.operation in ("delete", "rename")


@dataclass(slots=True)
class ChangeManifest:
    """
    Structured record of file modifications produced by write-capable agents.

    All agents that modify files (Code, Lint, Terminal) must return a
    ChangeManifest in their AgentResult.changes field. This enables:
    - Automatic rollback via checkpoint restoration
    - Router summaries that track which files were touched
    - HITL approval flows for high-risk batches
    - Evaluation harness validation of expected vs actual changes
    """

    files: list[FileChange] = field(default_factory=list)
    summary: str = ""
    risk: RiskLevel = RiskLevel.SAFE
    scope_paths: list[Path] = field(default_factory=list)  # Allowed modification paths
    checkpoint_id: str | None = None  # Links to .apex/checkpoints/<id>/

    def __post_init__(self) -> None:
        # Auto-compute risk if not explicitly set
        if self.risk == RiskLevel.SAFE and self.files:
            if any(f.is_destructive for f in self.files):
                object.__setattr__(self, "risk", RiskLevel.HIGH)
            elif len(self.files) > 3:
                object.__setattr__(self, "risk", RiskLevel.MEDIUM)
            elif len(self.files) > 0:
                object.__setattr__(self, "risk", RiskLevel.LOW)

    @property
    def total_lines_changed(self) -> int:
        """Total line delta across all file changes."""
        return sum(f.lines_added + f.lines_removed for f in self.files)

    @property
    def modified_paths(self) -> list[Path]:
        """All file paths touched by this manifest."""
        return [f.path for f in self.files]

    def is_within_scope(self, path: Path) -> bool:
        """Check if a path is allowed by scope_paths constraints."""
        if not self.scope_paths:
            return True  # No scope restriction
        path_resolved = path.resolve()
        return any(
            path_resolved == scope.resolve() or path_resolved.is_relative_to(scope.resolve())
            for scope in self.scope_paths
        )


# ============================================================================
# Diagnostic Information
# ============================================================================


@dataclass(slots=True, frozen=True)
class Diagnostic:
    """
    Structured diagnostic message (error, warning, or info) from agent operations.

    Replaces ad-hoc string formatting in agent outputs. Used for:
    - Syntax errors, lint warnings, import resolution failures
    - Test failures with file/line locations
    - Command execution errors with context
    """

    severity: Literal["error", "warning", "info"]
    message: str
    file: Path | None = None
    line: int | None = None
    column: int | None = None
    code: str | None = None  # Error code like "E501" or "import-error"
    source: str | None = None  # Tool that generated it (ruff, pytest, ast)

    def __str__(self) -> str:
        """Format as VSCode-compatible diagnostic string."""
        location = ""
        if self.file:
            location = str(self.file)
            if self.line is not None:
                location += f":{self.line}"
                if self.column is not None:
                    location += f":{self.column}"
            location += " "

        code_suffix = f" [{self.code}]" if self.code else ""
        severity_prefix = self.severity.upper()

        return f"{location}{severity_prefix}: {self.message}{code_suffix}"


# ============================================================================
# Enhanced Agent Result
# ============================================================================


@dataclass(slots=True)
class AgentResult:
    """
    Standardized output envelope for all agents.

    Replaces the minimal AgentResult from base.py with structured fields
    that enable reliable context passing, rollback, and evaluation.
    """

    output: str
    success: bool = True

    # Structured data replacing ad-hoc metadata dict
    changes: ChangeManifest | None = None
    diagnostics: list[Diagnostic] = field(default_factory=list)
    artifacts: list[Path] = field(default_factory=list)  # Generated files (launchers, reports, screenshots)

    # Confirmation and safety
    confirmation_required: bool = False
    confirmation_reason: str | None = None
    blocked: bool = False  # Operation rejected by safety checks

    # Context for downstream agents
    context_data: dict[str, Any] = field(default_factory=dict)  # Agent-specific outputs for next hop

    # Legacy metadata for backward compatibility (will be phased out)
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        """Ensure mutable fields are initialized."""
        if self.diagnostics is None:
            object.__setattr__(self, "diagnostics", [])
        if self.artifacts is None:
            object.__setattr__(self, "artifacts", [])
        if self.context_data is None:
            object.__setattr__(self, "context_data", {})
        if self.metadata is None:
            object.__setattr__(self, "metadata", {})

    @property
    def error_count(self) -> int:
        """Number of error-level diagnostics."""
        return sum(1 for d in self.diagnostics if d.severity == "error")

    @property
    def warning_count(self) -> int:
        """Number of warning-level diagnostics."""
        return sum(1 for d in self.diagnostics if d.severity == "warning")

    @property
    def modified_files(self) -> list[Path]:
        """Convenience accessor for changed file paths."""
        return self.changes.modified_paths if self.changes else []

    def format_diagnostics(self, max_lines: int = 20) -> str:
        """Render diagnostics as multi-line string, limited to max_lines."""
        if not self.diagnostics:
            return "(No diagnostics)"
        lines = [str(d) for d in self.diagnostics[:max_lines]]
        if len(self.diagnostics) > max_lines:
            remaining = len(self.diagnostics) - max_lines
            lines.append(f"... and {remaining} more diagnostic(s)")
        return "\n".join(lines)


# ============================================================================
# Backward Compatibility Helpers
# ============================================================================


def migrate_legacy_metadata(result: AgentResult) -> None:
    """
    Helper to populate structured fields from legacy metadata dict usage.

    Call this in agent code during migration to convert old-style
    metadata={'issues': 5, 'launcher': '/path'} into proper diagnostics
    and artifacts fields.
    """
    meta = result.metadata

    # Code agent: issues → diagnostics count
    if "issues" in meta and result.error_count == 0:
        # Create placeholder diagnostics if count doesn't match
        for _ in range(meta["issues"] - len(result.diagnostics)):
            result.diagnostics.append(
                Diagnostic(severity="error", message="Syntax error (legacy metadata)")
            )

    # Code agent: launcher → artifacts
    if "launcher" in meta and meta["launcher"]:
        launcher_path = Path(meta["launcher"])
        if launcher_path not in result.artifacts:
            result.artifacts.append(launcher_path)

    # Terminal agent: confirmation_required
    if meta.get("confirmation_required"):
        result.confirmation_required = True
        result.confirmation_reason = meta.get("reason", "Command requires approval")

    # Terminal agent: blocked
    if meta.get("blocked"):
        result.blocked = True
        result.success = False


# ============================================================================
# Factory Functions
# ============================================================================


def create_error_result(message: str, file: Path | None = None, line: int | None = None) -> AgentResult:
    """Convenience factory for error-only results."""
    diagnostic = Diagnostic(severity="error", message=message, file=file, line=line)
    return AgentResult(output=message, success=False, diagnostics=[diagnostic])


def create_success_result(message: str, changes: ChangeManifest | None = None) -> AgentResult:
    """Convenience factory for successful operation results."""
    return AgentResult(output=message, success=True, changes=changes)
