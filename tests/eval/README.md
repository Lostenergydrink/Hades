# Evaluation Harness

This folder contains structured tasks and expected outputs referenced by the roadmap checkpoints. Each entry links a natural-language request to the ChangeManifest/TestReport artifacts that downstream phases consume.

## Current Fixtures

| File | Purpose |
| --- | --- |
| `smoke_manifest.json` | Baseline "fix bug → run tests" scenario used in Phase 2 exit criteria. |

## Usage

1. Load the JSON manifest in your evaluation harness (pytest or custom runner).
2. Replay the `request` against the orchestrator using the provided `context` snippet.
3. Compare resulting `ChangeManifest`/`TestReport` payloads to `expected` for regression detection.
4. Record runtime metrics (see roadmap) and append deltas to `State Check - Updated.md` after each run.
