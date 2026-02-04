# Hades Roadmap

This document defines the scope, constraints, and milestones for Hades development. It exists to **prevent scope creep** and ensure non-negotiable aspects remain intact.

---

## Guiding Principles

1. **Refusal is success.** Hades is not obligated to produce output. Detecting that something cannot be safely synthesized is a valid outcome.
2. **AST is the foundation.** Regex may serve as a prefilter, never as the source of truth.
3. **Narrow beats universal.** A tool that works perfectly for TypeScript is better than a tool that half-works for everything.
4. **Provenance is law.** Every claim must trace back to an exact source anchor.
5. **Determinism is required.** Identical inputs must produce identical graphs and claim IDs.

---

## v1.0 — Foundation (Current)

**Goal**: A working pipeline that can decompose TypeScript/JavaScript code into an assertion graph, detect contradictions, and either produce a woven artifact or refuse.

### Scope

| In Scope | Out of Scope |
|----------|--------------|
| TypeScript/JavaScript source files | Python, Rust, Go, etc. |
| AST-driven claim extraction | Regex-based extraction (except prefilter) |
| Predicate vocabulary: `defines_function`, `calls`, `returns_type` | Semantic equivalence detection |
| Hard parse failure = collapse | Tolerant/partial parsing |
| Single input bundle (one `sourceId` per deliberation) | Multi-source comparison (deferred) |
| CLI + library API (Node) | Web interface |

### Non-Negotiable Constraints

These cannot be compromised in v1:

- **Language binding**: TypeScript compiler API only. No fallback parsers.
- **Predicate vocabulary**: Start tight. Only expand when proven necessary.
- **Parse failure handling**: If it doesn't parse, it doesn't exist. Epistemic collapse.
- **Provenance anchoring**: `node.getText(sourceFile)` or equivalent. No approximate spans.
- **No "helpful" hallucination**: If Hecate can't extract, Eris sees an empty graph, Cerberus refuses.
- **Determinism**: Identical inputs must yield identical claim IDs and graph structure. Critical for Styx and future multi-source comparison.

### Milestones

- [x] Bootstrap project structure
- [x] Core types defined (`AtomicClaim`, `AssertionGraph`, `PressureReport`, etc.)
- [x] Hecate: AST-driven extraction for functions and calls
- [x] Eris: Basic contradiction detection via exclusive predicates
- [x] Moirae: Topological sort weaving
- [x] Cerberus: Gate evaluation (PASS/TRIAL/REFUSE)
- [x] Styx: Forbidden path memory
- [ ] Predicate registry with exclusivity rules
- [ ] Normalization rules for claim identity
- [ ] Deterministic claim ID strategy (hash over normalized claim + anchor)
- [ ] CLI artifact output (`graph.json`, `pressure.json`, etc.)
- [ ] Golden-file tests for graph/pressure JSON outputs
- [ ] Test coverage for core paths
- [ ] Documentation complete

---

## Contradiction Model (v1)

A **contradiction** exists when two claims collide under a predicate's exclusivity rules.

### Exclusivity Rules

| Predicate | Exclusive? | Rule |
|-----------|------------|------|
| `defines_function` | Yes | One definition per identifier per scope (overloads deferred) |
| `returns_type` | Yes | One return type per function signature in a given source |
| `calls` | No | Functions can call multiple things; no contradiction from volume |

- Exclusivity is declared per predicate in a **registry** (single source of truth).
- Only exclusive predicates can produce contradictions in v1.
- Non-exclusive predicates may contribute to pressure via dependency structure (optional, not v1 core).

---

## Normalization Rules (v1)

AST provides structure, but canonicalization prevents false disagreements.

| Element | Normalization Strategy |
|---------|------------------------|
| Function identity | `name` (or `ClassName.methodName` for methods) |
| Callee identity | Identifier only in v1 (`foo`); property access (`obj.foo`) tracked separately |
| Return type | `node.type.getText(sourceFile)` — raw string, no interpretation |
| Scope path | File-relative; class/function nesting tracked via `findParentScope()` |

These rules must be **stable**. Changing normalization breaks Styx signatures and claim ID determinism.

---

## Threat Model

What Hades defends against:

- **Malicious or invalid input**: Inputs may be syntactically broken or adversarially crafted.
- **Invented claims**: Output must never contain claims not derivable from anchors.
- **Approximate provenance**: Graph must be reconstructible from exact source spans only.
- **Convenience creep**: System must refuse rather than approximate. "Styx forbids theater."

This model protects against well-meaning contributors who want to make Hades "more helpful" at the cost of honesty.

---

## Data Contracts (v1 CLI Output)

CLI artifacts are **versioned contracts**, not random JSON.

### `graph.json`

```json
{
  "version": "1.0",
  "sourceId": "string",
  "nodes": [
    {
      "id": "sha256-hash",
      "sourceId": "string",
      "subject": "string",
      "predicate": "string",
      "object": "string",
      "dependencies": ["id", ...],
      "payload": {
        "anchor": "exact source text",
        "fragment": "clean artifact"
      },
      "score": 0
    }
  ],
  "edges": [
    { "from": "id", "to": "id", "type": "SUPPORTS|CONTRADICTS|REFINES" }
  ]
}
```

### `pressure.json`

```json
{
  "version": "1.0",
  "totalPressure": 0.0,
  "conflictMap": { "claimId": ["conflictingClaimId", ...] },
  "isTerminal": false,
  "reasonCodes": ["ONTOLOGICAL_FRICTION", ...]
}
```

### `verdict.json`

```json
{
  "version": "1.0",
  "gate": { "action": "PASS|TRIAL|REFUSE", "reason": "string", "isFinal": true },
  "trial": { "outcome": "string", "success": true } | null
}
```

### `artifact.txt`

Plain text. Woven output if successful, empty or absent if refused.

---

## Test Strategy

Tests must be **meaningful**, not performative.

### Required Categories

| Category | What it validates |
|----------|-------------------|
| **Parsing tests** | Valid TS patterns: class methods, arrow functions, generics, decorators |
| **Provenance tests** | Anchors match exact source spans; no drift |
| **Contradiction tests** | Exclusive predicate collisions detected correctly |
| **Refusal tests** | Broken syntax triggers epistemic collapse |
| **Determinism tests** | Same input → same claim IDs and graph structure |
| **Golden-file tests** | CLI output matches expected JSON schemas |

Tests that assert `true === true` will be rejected.

---

## v1.1 — Hardening

**Goal**: Production-ready stability. Edge cases handled. Test coverage meaningful.

### Planned Work

- Hecate: Handle edge cases (decorators, generics, arrow functions, class methods)
- Hecate: Add `imports`, `exports` predicates
- Eris: Refine conflict strength calculation
- Persephone: Implement basic trial logic (re-derivation check)
- Comprehensive test suite (unit + integration)
- Error handling audit

### Constraints Carried Forward

All v1.0 constraints remain in effect.

---

## v2.0 — Multi-Source Deliberation

**Goal**: Compare multiple code sources (e.g., competing LLM outputs) and surface disagreements.

### Planned Work

- Hecate: Accept multiple `{ sourceId, content }` inputs
- Eris: Cross-source conflict detection
- Hermes: Provenance transport layer (tracking claim origins across sources)
- Consider: Tolerant parsing mode (salvage with low-confidence markers)

### Potential Scope Expansion

- Python support (via separate parser module, not regex)
- Additional predicates based on v1 learnings

---

## v3.0+ — Future Considerations

These are **not commitments**, just acknowledged possibilities:

- Language-agnostic decomposer interface
- Semantic equivalence detection (likely requires external tooling)
- Web-based visualization of assertion graphs
- Integration with CI/CD pipelines
- Plugin architecture for custom predicates

---

## Decision Log

Documenting key architectural decisions for future reference.

| Date | Decision | Rationale |
|------|----------|-----------|
| 2026-02-03 | AST over Regex | Regex produces confident garbage. AST provides structural truth. User's explicit choice based on project philosophy. |
| 2026-02-03 | TS/JS only for v1 | Narrow scope prevents abandoned-project syndrome. Multi-language is a v2+ concern. |
| 2026-02-03 | Hard parse failure | Aligns with "Styx forbids theater" worldview. Tolerant parsing deferred to v2 consideration. |
| 2026-02-03 | Tight predicate vocabulary | Prevents Eris pressure from becoming noise. Start small, prove pipeline, then expand. |

---

## Anti-Goals

Things Hades will **never** attempt:

- **Replace human judgment**: Hades surfaces friction; humans decide what to do about it.
- **Guarantee correctness**: Hades detects structural disagreement, not semantic truth.
- **Be "helpful" at the cost of honesty**: Producing plausible garbage is worse than refusing.
- **Support every language**: Better to do one thing well than many things poorly.

---

## Contributing to the Roadmap

Scope changes require explicit justification against the guiding principles. If a proposed feature conflicts with a non-negotiable constraint, it must either:

1. Wait for the appropriate version milestone, or
2. Be rejected outright

See [CONTRIBUTING.md](./CONTRIBUTING.md) for the process.
