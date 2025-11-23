# Roadmap Notes

This folder captures per-agent implementation notes, decision logs, and open questions that would otherwise clutter `ROADMAP.md`.

## Suggested Structure

```
roadmap/
├── code.md          # Code/Refactor agent decisions and TODOs
├── test.md          # Test Runner plans, fixtures, and smoke metrics
├── terminal.md      # Terminal/Ops guardrails exercised and approvals logged
├── web.md           # Web automation dependencies, artifacts, and selectors
└── router.md        # Routing heuristics, model prompts, and evaluation data
```

## Usage Guidelines

- Update the relevant agent file whenever a milestone completes or a blocker emerges.
- Record lightweight metrics (registry scan time, guarded command count, smoke duration) after each iteration so the State Check document can reference concrete deltas.
- Reference the `phase:<n>` issue labels used in GitHub/ADO so stakeholders can trace plan items back to execution artifacts.
