# Hades Types Usage Guide

This guide explains how to use the structured types introduced in Phase 1 for standardized agent communication.

## Overview

The `agent_app/types.py` module provides structured schemas that replace ad-hoc metadata dictionaries:

- **`AgentResult`**: Enhanced result envelope with structured fields
- **`ChangeManifest`**: Tracks file modifications for rollback and approval
- **`Diagnostic`**: Standardized error/warning/info messages
- **`FileChange`**: Individual file modification record
- **`RiskLevel`**: Classification for HITL confirmation decisions

## Core Types

### AgentResult

The enhanced `AgentResult` replaces the minimal version from `base.py` with structured fields:

```python
from agent_app.types import AgentResult, ChangeManifest, Diagnostic, create_success_result

# Before (legacy metadata dict):
result = AgentResult(
    output="Fixed 3 files",
    success=True,
    metadata={"files_changed": 3, "issues": 2}
)

# After (structured fields):
result = AgentResult(
    output="Fixed 3 files",
    success=True,
    changes=ChangeManifest(
        files=[...],
        summary="Fixed import errors",
        risk=RiskLevel.LOW
    ),
    diagnostics=[
        Diagnostic(severity="error", message="Import not found", file=Path("app.py"), line=10)
    ]
)

# Or use convenience factory:
result = create_success_result("Operation complete", changes=manifest)
```

### ChangeManifest

All write-capable agents (Code, Lint, Terminal) must return a `ChangeManifest`:

```python
from pathlib import Path
from agent_app.types import ChangeManifest, FileChange, RiskLevel

manifest = ChangeManifest(
    files=[
        FileChange(
            path=Path("agent_app/agents/styx/styx_agent.py"),
            operation="modify",
            lines_added=15,
            lines_removed=8,
            backup_path=Path(".apex/checkpoints/run123/styx_agent.py.bak")
        ),
        FileChange(
            path=Path("tests/test_styx.py"),
            operation="create",
            lines_added=42
        )
    ],
    summary="Refactored StyxAgent to use structured types",
    risk=RiskLevel.MEDIUM,  # Auto-computed if not set
    scope_paths=[Path("agent_app/agents/")],
    checkpoint_id="run123"
)

# Access computed properties:
print(manifest.total_lines_changed)  # 65
print(manifest.modified_paths)  # [Path("agent_app/agents/styx/styx_agent.py"), Path("tests/test_styx.py")]
print(manifest.is_within_scope(Path("agent_app/agents/styx/styx_agent.py")))  # True
```

### Diagnostic

Replace string formatting with structured diagnostics:

```python
from agent_app.types import Diagnostic

# Syntax error
diag = Diagnostic(
    severity="error",
    message="invalid syntax",
    file=Path("app.py"),
    line=42,
    column=15,
    code="E999",
    source="ast"
)

# Test failure
diag = Diagnostic(
    severity="error",
    message="AssertionError: Expected 5, got 3",
    file=Path("tests/test_math.py"),
    line=18,
    source="pytest"
)

# Lint warning
diag = Diagnostic(
    severity="warning",
    message="Line too long (120 > 88 characters)",
    file=Path("agent.py"),
    line=55,
    code="E501",
    source="ruff"
)

# Format as VSCode-compatible string:
print(str(diag))  # "app.py:42:15 ERROR: invalid syntax [E999]"
```

### RiskLevel

Classify operations for HITL approval:

```python
from agent_app.types import RiskLevel

# Auto-computed by ChangeManifest based on operations:
# - SAFE: No files changed or formatting only
# - LOW: Single file modification
# - MEDIUM: Multiple file changes (>3)
# - HIGH: Destructive operations (delete, rename) or dependency changes
# - CRITICAL: System commands, git operations

if manifest.risk in (RiskLevel.HIGH, RiskLevel.CRITICAL):
    # Request user confirmation
    print(f"⚠️  High-risk operation: {manifest.summary}")
```

## Migration from Legacy Metadata

Use `migrate_legacy_metadata()` to convert existing code during the transition:

```python
from agent_app.types import AgentResult, migrate_legacy_metadata

# Old agent code returning legacy metadata:
result = AgentResult(
    output="Found 5 issues",
    success=False,
    metadata={"issues": 5, "launcher": "/path/to/launcher.ps1"}
)

# Convert to structured fields:
migrate_legacy_metadata(result)

# Now result.diagnostics has 5 placeholder entries
# and result.artifacts contains the launcher path
```

## Agent Implementation Examples

### Styx (Write Operations)

```python
from pathlib import Path
from agent_app.types import (
    AgentResult, ChangeManifest, FileChange, RiskLevel,
    Diagnostic, create_success_result
)

def handle_refactor(request: AgentRequest) -> AgentResult:
    # Perform changes...
    files_modified = [Path("app.py"), Path("utils.py")]
    
    manifest = ChangeManifest(
        files=[
            FileChange(
                path=f,
                operation="modify",
                lines_added=10,
                lines_removed=5,
                backup_path=checkpoint_dir / f.name
            ) for f in files_modified
        ],
        summary="Refactored utility functions",
        risk=RiskLevel.MEDIUM,
        checkpoint_id=run_id
    )
    
    return create_success_result(
        f"Refactored {len(files_modified)} files",
        changes=manifest
    )
```

### Furies (Diagnostics)

```python
from agent_app.types import AgentResult, Diagnostic

def handle_lint(request: AgentRequest) -> AgentResult:
    # Run ruff...
    diagnostics = [
        Diagnostic(
            severity="warning",
            message="Unused import 'sys'",
            file=Path("app.py"),
            line=5,
            code="F401",
            source="ruff"
        )
    ]
    
    return AgentResult(
        output=result.format_diagnostics(),
        success=result.error_count == 0,
        diagnostics=diagnostics
    )
```

### Thanatos (Confirmation Required)

```python
from agent_app.types import AgentResult

def handle_command(request: AgentRequest) -> AgentResult:
    if assessment.status == "confirm" and not confirmed:
        return AgentResult(
            output=f"Command requires approval: {assessment.reason}",
            success=False,
            confirmation_required=True,
            confirmation_reason=assessment.reason,
            context_data={"command": argv}  # Pass to next attempt
        )
    
    # Execute command...
```

## Context Passing Between Agents

The `AgentRequest.upstream_results` field enables multi-hop workflows:

```python
# Router executes: Styx → Persephone

# Styx returns:
code_result = AgentResult(
    output="Fixed imports",
    changes=ChangeManifest(files=[...]),
    context_data={"modified_modules": ["app", "utils"]}
)

# Persephone receives:
def handle(self, request: AgentRequest) -> AgentResult:
    if request.upstream_results:
        code_result = request.upstream_results[0]
        modified_files = code_result.modified_files
        # Run tests only for affected modules
```

## Validation and Properties

### AgentResult Helpers

```python
result = AgentResult(...)

# Diagnostic counts:
print(result.error_count)    # Number of errors
print(result.warning_count)  # Number of warnings

# File access:
print(result.modified_files)  # List of changed paths

# Formatted output:
print(result.format_diagnostics(max_lines=10))
```

### ChangeManifest Validation

```python
manifest = ChangeManifest(...)

# Check scope enforcement:
if not manifest.is_within_scope(target_file):
    raise ValueError(f"{target_file} outside allowed scope")

# Risk assessment:
if any(f.is_destructive for f in manifest.files):
    manifest.risk = RiskLevel.HIGH
```

## Backward Compatibility

The new types maintain backward compatibility:

- `AgentResult` is imported from `agent_app.types` but re-exported via `agents.base` 
- Existing `metadata` dict still works (will be phased out in Phase 2)
- All agents continue to work with legacy return style during migration

```python
# Both import paths work:
from agent_app.agents import AgentResult  # Re-exported
from agent_app.types import AgentResult   # Direct

# Legacy style still valid:
result = AgentResult(output="...", metadata={"key": "value"})
```

## Phase 1 Checklist

When migrating an agent to use structured types:

- [ ] Replace `metadata={"issues": N}` with `diagnostics=[...]`
- [ ] Add `ChangeManifest` for all write operations
- [ ] Use `RiskLevel` for HITL decisions
- [ ] Pass data via `context_data` instead of metadata
- [ ] Add `upstream_results` handling for multi-hop support
- [ ] Update tests to validate structured fields
- [ ] Remove legacy metadata dict usage

## Next Steps

Phase 2 will:
- Wire HITL confirmation flow using `confirmation_required` flag
- Implement checkpoint/rollback using `ChangeManifest.checkpoint_id`
- Extend Router to use `context_data` for multi-hop planning
- Add evaluation harness validating expected vs actual manifests
