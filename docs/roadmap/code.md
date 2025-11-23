# Styx (Code/Refactor) Agent Notes

## Scope
- Deterministic edits via `apply_patch`, ChangeManifest emission, checkpoint management.

## Current Status
- MVP limited to syntax/import checks; rollback snapshots pending.
- Phase dependencies: requires Phase 1 schemas/checkpoints before Phase 2 work.

## Upcoming
- Implement transactional checkpoints under `.apex/checkpoints/`.
- Enforce scoped edits using registry metadata and AgentRequest context.

## Metrics to Capture
- `manifests_emitted`
- `rollback_available`
- Average time to apply ChangeManifest (s)
