# Thanatos (Terminal/Ops) Agent Notes

## Scope
- Execute guarded shell commands, enforce HITL approvals, surface CommandReports.

## Current Status
- Guardrail heuristics exist, but orchestrator lacks confirmation callback wiring.

## Upcoming
- Implement approval channel (CLI prompt or UI hook).
- Log every guarded command to persistent audit trail.

## Metrics to Capture
- `guarded_commands_exercised`
- `approvals_recorded`
- Average command duration (s)
