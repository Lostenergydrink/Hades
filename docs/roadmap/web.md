# Hermes (Web Automation) Agent Notes

## Scope
- Playwright/Puppeteer-driven UI automation, artifact capture under `tests/e2e/.artifacts/`.

## Current Status
- Stub agent returns pending; dependencies not yet isolated from Python core.

## Upcoming
- Scaffold Playwright dependency management (possibly Node-based subpackage).
- Implement screenshot + artifact upload path referenced by Phase 3 exit criteria.

## Metrics to Capture
- `artifacts_produced`
- `e2e_runs`
- Failure rate (%)
