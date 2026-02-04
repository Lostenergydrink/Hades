# hades-playground

Unmoored epistemic deliberation utility.

## Setup
1. `npm install`
2. `npm run build`
3. `npm start` (Runs the demo)

## CLI Usage
```bash
npx hades <file.ts>
```

This will analyze the file and write artifacts to `./artifacts/`:
- `graph.json` - Assertion graph
- `pressure.json` - Pressure report
- `verdict.json` - Gate/trial verdicts
- `artifact.txt` - Woven output

## Structure
- `src/pillars/`: The core logic modules (Hecate, Eris, etc.)
- `src/core/`: Type definitions and stone invariants.
