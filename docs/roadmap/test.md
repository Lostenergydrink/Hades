# Test Runner Agent Notes

## Scope
- Discover/execute pytest suites, parse results, emit structured TestReports.

## Current Status
- Agent stub returns pending; smoke scenario defined in `tests/eval/smoke_manifest.json`.

## Upcoming
- Add venv-aware execution helpers and failure parsing.
- Wire context passing (changed files) from Styx outputs.

## Metrics to Capture
- `tests_run`
- `failures_detected`
- `smoke_duration_s`
