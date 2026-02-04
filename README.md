# Hades

**A zero-trust epistemic judge for AI code evaluation.**

Hades is not a "truth engine." It is a **refusal engine** that detects structural disagreement and provenance gaps in code artifacts. Built on AST-driven decomposition, it extracts atomic claims from source code and measures the friction between competing interpretations.

> *"Structure over vibes."*

---

## Status

**Work in Progress** — v1 scope is deliberately narrow. See [ROADMAP.md](./ROADMAP.md) for constraints and milestones.

---

## Core Philosophy

1. **Zero Trust**: Every claim must be anchored to provenance. Theater is refused.
2. **AST Over Regex**: Structural truth via compiler APIs, not pattern matching.
3. **Refusal > Hallucination**: "No output" is a valid success state.
4. **Narrow Scope**: v1 targets TypeScript/JavaScript only. Other languages are explicitly out of scope.

---

## Architecture

Hades operates through mythologically-themed modules called **Pillars**:

| Pillar | Role |
|--------|------|
| **Hecate** | Assertion extraction via TypeScript AST. Decomposes code into atomic claims (subject-predicate-object triples). |
| **Eris** | Pressure calculation. Detects ontological contradictions between claims. |
| **Moirae** | Weaving. Synthesizes surviving claims into coherent output via topological sort. |
| **Cerberus** | Gatekeeper. Evaluates pressure reports and decides: PASS, TRIAL, or REFUSE. |
| **Persephone** | Trial administration. Executes ordeals for contested claims. |
| **Styx** | Negative constraint memory. Records forbidden paths that must never be retried. |
| **Lethe** | Failure archive. Tracks friction patterns for future reference. |

---

## Installation

```bash
npm install
npm run build
```

## Usage

### Programmatic

```typescript
import { HadesOrchestrator } from './dist/index.js';

const hades = new HadesOrchestrator();
const result = await hades.deliberate('source-id', sourceCode);
```

### CLI

```bash
npx hades <file.ts>
```

Outputs to `./artifacts/`:
- `graph.json` — Assertion graph
- `pressure.json` — Pressure report  
- `verdict.json` — Gate/trial verdicts
- `artifact.txt` — Woven output (if successful)

---

## Development

```bash
npm run dev      # Run with tsx (hot reload)
npm run build    # Build with tsup
npm test         # Run vitest
npm run lint     # ESLint
npm run format   # Prettier
```

---

## Project Structure

```
src/
├── core/
│   └── types.ts        # Stone invariants (readonly interfaces)
├── pillars/
│   ├── Hecate.ts       # AST decomposition
│   ├── Eris.ts         # Pressure calculation
│   ├── Moirae.ts       # Claim weaving
│   ├── Cerberus.ts     # Gate evaluation
│   ├── Persephone.ts   # Trial execution
│   ├── Styx.ts         # Forbidden path memory
│   └── Lethe.ts        # Failure archive
├── index.ts            # Orchestrator
└── cli.ts              # CLI entry point
docs/
└── gemini-2.0-context.md  # Architectural vision document
```

---

## v1 Constraints

These are **non-negotiable** for the initial release:

- **Language**: TypeScript/JavaScript only (via `typescript` compiler API)
- **Predicate vocabulary**: `defines_function`, `calls`, `returns_type` (extensible later)
- **Parse failures**: Treated as epistemic collapse (empty graph, refused)
- **No multi-language**: Python, Rust, etc. are explicitly deferred to v2+

See [ROADMAP.md](./ROADMAP.md) for the full constraint matrix.

---

## License

[MIT](./LICENSE)

---

## Contributing

See [CONTRIBUTING.md](./CONTRIBUTING.md) for guidelines.
