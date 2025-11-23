# Hades Types Quick Reference

## Import
```python
from agent_app.types import (
    AgentResult, ChangeManifest, FileChange, Diagnostic, RiskLevel,
    create_success_result, create_error_result, migrate_legacy_metadata
)
```

## Creating Results

### Success with Changes
```python
result = create_success_result(
    "Refactored 3 files",
    changes=ChangeManifest(
        files=[FileChange(path=Path("app.py"), operation="modify", lines_added=10, lines_removed=5)],
        summary="Fixed imports",
        risk=RiskLevel.LOW
    )
)
```

### Error with Diagnostics
```python
result = create_error_result(
    "Syntax error in app.py",
    file=Path("app.py"),
    line=42
)
# Or build manually:
result = AgentResult(
    output="Failed",
    success=False,
    diagnostics=[
        Diagnostic(severity="error", message="Invalid syntax", file=Path("app.py"), line=42)
    ]
)
```

### Confirmation Required
```python
result = AgentResult(
    output="Command needs approval",
    success=False,
    confirmation_required=True,
    confirmation_reason="Destructive operation: rm -rf",
    context_data={"command": ["rm", "-rf", "temp/"]}
)
```

## ChangeManifest Patterns

### Single File Edit
```python
manifest = ChangeManifest(
    files=[FileChange(path=Path("app.py"), operation="modify", lines_added=5, lines_removed=2)],
    summary="Fixed typo"
)
# Auto-computes: risk=RiskLevel.LOW
```

### Multiple Files with Scope
```python
manifest = ChangeManifest(
    files=[...],
    summary="Refactored agent package",
    scope_paths=[Path("agent_app/agents/")],
    checkpoint_id="run_20251120_143022"
)
# Validate: manifest.is_within_scope(target_file)
```

### Destructive Operation
```python
manifest = ChangeManifest(
    files=[
        FileChange(path=Path("old.py"), operation="delete"),
        FileChange(path=Path("new.py"), operation="create", lines_added=100)
    ],
    summary="Replaced module",
    risk=RiskLevel.HIGH
)
```

## Diagnostic Patterns

### Syntax Error
```python
Diagnostic(severity="error", message="Invalid syntax", file=Path("app.py"), line=42, source="ast")
```

### Lint Warning
```python
Diagnostic(severity="warning", message="Line too long", file=Path("app.py"), line=55, code="E501", source="ruff")
```

### Test Failure
```python
Diagnostic(severity="error", message="AssertionError", file=Path("tests/test_app.py"), line=18, source="pytest")
```

## RiskLevel Decision Tree

```
Is it destructive (delete/rename)?     → CRITICAL/HIGH
Is it a system/git command?            → CRITICAL
Is it a dependency/config change?      → HIGH
Does it modify >3 files?               → MEDIUM
Does it modify 1-3 files?              → LOW
Is it read-only or formatting?         → SAFE
```

## Context Passing

### Sending Data Forward
```python
# First agent (Code):
return AgentResult(
    output="Fixed imports",
    success=True,
    changes=manifest,
    context_data={"modified_modules": ["app", "utils"]}
)
```

### Receiving Data
```python
# Second agent (Test):
def handle(self, request: AgentRequest) -> AgentResult:
    if request.upstream_results:
        prev = request.upstream_results[0]
        files = prev.modified_files
        modules = prev.context_data.get("modified_modules", [])
        # Run targeted tests
```

## Result Properties

```python
result.error_count          # Number of errors
result.warning_count        # Number of warnings
result.modified_files       # List[Path] from changes
result.format_diagnostics() # Pretty-printed diagnostic list
```

## Manifest Properties

```python
manifest.total_lines_changed    # Sum of adds + removes
manifest.modified_paths         # List[Path] of all files
manifest.is_within_scope(path)  # Validate against scope_paths
```

## Migration Helper

```python
# Convert legacy metadata to structured fields:
old_result = AgentResult(output="...", metadata={"issues": 5, "launcher": "/path"})
migrate_legacy_metadata(old_result)
# Now: old_result.diagnostics has 5 items, old_result.artifacts has launcher
```
