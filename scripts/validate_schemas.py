"""
Validation script for Phase 1 schema definitions.

Demonstrates that all types work correctly and can be used together.
Run this after installing dependencies to verify the schema implementation.
"""

import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Import all new types
from agent_app.types import (
    AgentResult,
    ChangeManifest,
    Diagnostic,
    FileChange,
    RiskLevel,
    create_error_result,
    create_success_result,
    migrate_legacy_metadata,
)


def test_basic_types():
    """Verify basic type instantiation."""
    print("✓ Testing basic type instantiation...")

    # FileChange
    change = FileChange(
        path=Path("app.py"),
        operation="modify",
        lines_added=10,
        lines_removed=5,
    )
    assert change.path == Path("app.py")
    assert not change.is_destructive

    # Diagnostic
    diag = Diagnostic(
        severity="error",
        message="Test error",
        file=Path("test.py"),
        line=42,
    )
    assert "test.py:42" in str(diag)

    # RiskLevel
    assert RiskLevel.SAFE.value == "safe"
    assert RiskLevel.CRITICAL.value == "critical"

    print("  ✓ FileChange, Diagnostic, RiskLevel work correctly")


def test_change_manifest():
    """Verify ChangeManifest logic."""
    print("✓ Testing ChangeManifest...")

    # Auto-compute risk
    manifest = ChangeManifest(
        files=[
            FileChange(path=Path("a.py"), operation="modify", lines_added=5),
            FileChange(path=Path("b.py"), operation="modify", lines_added=3),
        ],
        summary="Test changes",
    )
    assert manifest.risk == RiskLevel.LOW
    assert manifest.total_lines_changed == 8
    assert len(manifest.modified_paths) == 2

    # Destructive changes → HIGH risk
    manifest2 = ChangeManifest(
        files=[FileChange(path=Path("old.py"), operation="delete")],
        summary="Delete file",
    )
    assert manifest2.risk == RiskLevel.HIGH
    assert manifest2.files[0].is_destructive

    # Scope validation
    manifest3 = ChangeManifest(
        files=[],
        scope_paths=[Path("agent_app/agents/")],
    )
    assert manifest3.is_within_scope(Path("agent_app/agents/styx/styx_agent.py"))
    assert not manifest3.is_within_scope(Path("scripts/clean.ps1"))

    print("  ✓ ChangeManifest logic (risk, scope, properties) works correctly")


def persephone_agent_result():
    """Verify enhanced AgentResult."""
    print("✓ Testing AgentResult...")

    # Basic success
    result = AgentResult(output="Success", success=True)
    assert result.success
    assert result.error_count == 0

    # With diagnostics
    result2 = AgentResult(
        output="Found errors",
        success=False,
        diagnostics=[
            Diagnostic(severity="error", message="Error 1"),
            Diagnostic(severity="warning", message="Warning 1"),
            Diagnostic(severity="error", message="Error 2"),
        ],
    )
    assert result2.error_count == 2
    assert result2.warning_count == 1

    # With changes
    manifest = ChangeManifest(
        files=[FileChange(path=Path("app.py"), operation="modify", lines_added=10)]
    )
    result3 = AgentResult(output="Modified files", changes=manifest)
    assert len(result3.modified_files) == 1
    assert result3.modified_files[0] == Path("app.py")

    # Confirmation required
    result4 = AgentResult(
        output="Needs approval",
        success=False,
        confirmation_required=True,
        confirmation_reason="High-risk operation",
    )
    assert result4.confirmation_required
    assert result4.confirmation_reason

    print("  ✓ AgentResult (diagnostics, changes, confirmation) works correctly")


def test_factory_functions():
    """Verify convenience factories."""
    print("✓ Testing factory functions...")

    # create_error_result
    error = create_error_result("Test error", file=Path("test.py"), line=10)
    assert not error.success
    assert len(error.diagnostics) == 1
    assert error.diagnostics[0].severity == "error"

    # create_success_result
    manifest = ChangeManifest(files=[])
    success = create_success_result("All done", changes=manifest)
    assert success.success
    assert success.changes == manifest

    print("  ✓ Factory functions work correctly")


def test_legacy_migration():
    """Verify backward compatibility helper."""
    print("✓ Testing legacy metadata migration...")

    # Old-style result with metadata
    old_result = AgentResult(
        output="Legacy result",
        success=False,
        metadata={
            "issues": 3,
            "launcher": "launch.ps1",
            "confirmation_required": True,
            "reason": "Needs approval",
            "blocked": True,
        },
    )

    # Migrate to structured fields
    migrate_legacy_metadata(old_result)

    assert len(old_result.diagnostics) == 3
    assert Path("launch.ps1") in old_result.artifacts
    assert old_result.confirmation_required
    assert old_result.confirmation_reason == "Needs approval"
    assert old_result.blocked

    print("  ✓ Legacy metadata migration works correctly")


def main():
    """Run all validation tests."""
    print("\n" + "=" * 60)
    print("Hades Phase 1 Schema Validation")
    print("=" * 60 + "\n")

    try:
        test_basic_types()
        test_change_manifest()
        persephone_agent_result()
        test_factory_functions()
        test_legacy_migration()

        print("\n" + "=" * 60)
        print("✅ All schema validation tests passed!")
        print("=" * 60 + "\n")
        print("Phase 1 schema definitions are complete and working correctly.")
        print("\nNext steps:")
        print("  1. Registry optimization (IGNORE_DIRS)")
        print("  2. HITL confirmation flow")
        print("  3. Checkpoint/rollback system")
        print("  4. Agent migration to use structured types")

    except AssertionError as e:
        print(f"\n❌ Validation failed: {e}")
        raise


if __name__ == "__main__":
    main()
