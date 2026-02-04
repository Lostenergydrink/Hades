# Hades Roadmap

This document defines the scope, constraints, and milestones for Hades development. It exists to **prevent scope creep** and ensure non-negotiable aspects remain intact.

---

## Guiding Principles

1. **Refusal is success.** Hades is not obligated to produce output. Detecting that something cannot be safely synthesized is a valid outcome.
2. **AST is the foundation.** Regex may serve as a prefilter, never as the source of truth.
3. **Narrow beats universal.** A tool that works perfectly for TypeScript is better than a tool that half-works for everything.
4. **Provenance is law.** Every claim must trace back to an exact source anchor.

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
| Single-source deliberation | Multi-source comparison (deferred) |
| CLI and programmatic API | Web interface |

### Non-Negotiable Constraints

These cannot be compromised in v1:

- **Language binding**: TypeScript compiler API only. No fallback parsers.
- **Predicate vocabulary**: Start tight. Only expand when proven necessary.
- **Parse failure handling**: If it doesn't parse, it doesn't exist. Epistemic collapse.
- **Provenance anchoring**: `node.getText(sourceFile)` or equivalent. No approximate spans.
- **No "helpful" hallucination**: If Hecate can't extract, Eris sees an empty graph, Cerberus refuses.

### Milestones

- [x] Bootstrap project structure
- [x] Core types defined (`AtomicClaim`, `AssertionGraph`, `PressureReport`, etc.)
- [x] Hecate: AST-driven extraction for functions and calls
- [x] Eris: Basic contradiction detection via exclusive predicates
- [x] Moirae: Topological sort weaving
- [x] Cerberus: Gate evaluation (PASS/TRIAL/REFUSE)
- [x] Styx: Forbidden path memory
- [ ] CLI artifact output (`graph.json`, `pressure.json`, etc.)
- [ ] Test coverage for core paths
- [ ] Documentation complete

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
