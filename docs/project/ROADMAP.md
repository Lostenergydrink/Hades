# Hades Development Roadmap

This document outlines a phased development plan for Hades, addressing its scale by breaking down the implementation into manageable stages. The core strategy is to structure each agent as a self-contained package within the main application, allowing for focused development and clear separation of concerns.

## Phase Overview & Ownership

| Phase | Focus | Owner | Target Window | Integration Milestone |
| --- | --- | --- | --- | --- |
| Phase 1 | Foundational restructuring, schemas, safety | Alex Kim (Foundations) | 03–21 Nov 2025 | Config + safety scaffolding in place for downstream agents |
| Phase 2 | Code/Test core loop | Priya Shah (Code/Test) | 24 Nov – 19 Dec 2025 | Code → Test smoke test produces green manifest |
| Phase 3 | Terminal + Web toolkit expansion | Luis Ortega (Ops & Automation) | 05–30 Jan 2026 | Multi-hop "code → terminal → test" workflow succeeds with artifacts |
| Phase 4 | Intelligence, evaluation, observability | Samira Chen (Intelligence) | 02–27 Feb 2026 | Evaluation harness + tracing dashboards cover ≥20 tasks |

## Phase 1: Foundational Restructuring & Core Safety

This phase focuses on creating a robust and scalable project structure and implementing critical safety features before building out individual agent capabilities.

> Dependencies: Bootstraps configuration and safety infrastructure for every subsequent phase. Blocks Phase 2 until schema + checkpoint work is merged.

**1. Restructure into Agent Packages:**
   - Refactor the existing `agent_app/agents` directory.
   - Each agent (`Router`, `Code`, `Terminal`, `TestRunner`, `WebAutomation`) will be moved into its own subdirectory (package).
   - The new structure will look like this:
     ```
     agent_app/
     ├── agents/
     │   ├── __init__.py
     │   ├── code/
     │   │   ├── __init__.py
     │   │   ├── styx_agent.py
     │   │   └── helpers.py  # Example helper
     │   ├── terminal/
     │   │   ├── __init__.py
     │   │   └── thanatos_agent.py
     │   └── ... (etc. for other agents)
     ├── __init__.py
     └── orchestrator.py
     ```

**2. Implement Core Schemas & Configuration:**
   - **Define `AgentResult` and `ChangeManifest`:** Create standardized data structures in `agent_app/types.py` for inter-agent communication and structured output.
   - **Create `hades_config.toml`:** Establish a centralized configuration file for project paths, ignore patterns, and tool settings to reduce hardcoded values and auto-detection fragility.

**3. Build Safety & Validation Mechanisms:**
   - **Pre-flight Validator:** Implement a `check-env` task to verify that essential tools (`git`, `ruff`, etc.) and services are available.
   - **Human-in-the-Loop (HITL) Confirmation:** Implement a user approval step in the orchestrator for all generated plans and high-risk operations.
   - **Transactional Checkpoints:** The `StyxAgent` will save the state of files to a `.apex/checkpoints/` directory before modification, enabling a simple rollback mechanism.

**Phase 1 Exit Criteria:**
- ✅ All agents successfully moved to package structure with imports working
- ✅ `check-env` command returns green on your development machine
- ✅ HITL confirmation successfully blocks a high-risk terminal command
- ✅ A code change can be rolled back from checkpoint (manual test)
- ✅ `hades_config.toml` is read and respected by registry/orchestrator

**Integration Checkpoint:** Outputs from Phase 1 (schemas, config, checkpoints) are required inputs for the Phase 2 Code/Test loop, so accept no Phase 2 work until these artifacts are versioned and documented.

## Phase 2: Core Agent Implementation (Code & Test)

With a solid foundation, this phase focuses on delivering the primary "code-and-test" loop.

> Dependencies: Requires Phase 1 schema + checkpoint features. Unlocks Phase 3 once the Code → Test smoke path is reliable.

**1. `StyxAgent` (Initial Implementation):**
   - Implement file-patching capabilities based on `ChangeManifest`.
   - Enforce file scope to prevent unintended edits.
   - Develop initial refactoring commands (e.g., "apply patch," "remove unused imports").

**2. `TestRunnerAgent` (Initial Implementation):**
   - Implement logic to discover and run `pytest` in the target project's virtual environment.
   - Parse test output to create a structured `AgentResult` (pass/fail counts, errors).
   - Wire it into the orchestrator so it can run after a `StyxAgent` operation.

**3. `HadesAgent` (Keyword-Based):**
   - Enhance the existing keyword-based routing matrix to support the new agent packages and the "code-then-test" plan.

**4. End-to-End Scenario:**
   - Build and validate a complete "fix a bug and run tests" smoke test to ensure context passes correctly between agents and that rollback works on failure.

**Phase 2 Exit Criteria:**
- ✅ "Fix bug → run tests" smoke test passes end-to-end
- ✅ Test failures correctly propagate to Router summary with structured output
- ✅ Context passing validated (TestRunner sees StyxAgent's file list)
- ✅ Rollback triggers automatically when test phase fails
- ✅ Router can successfully route at least 5 different task types to correct agents

**Integration Checkpoint:** Publish the smoke test results and ChangeManifest samples to `tests/eval/` so Phase 3 and 4 teams can reuse them as fixtures.

## Phase 3: Expanding the Toolkit (Terminal & Web)

This phase expands the agent's capabilities beyond code and tests into operational and E2E tasks.

> Dependencies: Needs Phase 2's stable multi-hop execution to host Terminal/Web hooks; produces artifacts consumed by Phase 4 evaluation runs.

**1. `ThanatosAgent` (Full Implementation):**
   - Wire the HITL confirmation flow for destructive commands (`pip install`, `git clean`).
   - Improve command parsing and guardrails against dangerous operations.
   - Ensure output is streamed back effectively as part of the `AgentResult`.

**2. `HermesAgent` (Scaffolding):**
   - Set up the agent package with Playwright/Puppeteer dependencies.
   - Implement a basic "launch and take screenshot" task.
   - Define artifact storage strategy under `tests/e2e/.artifacts/`.

**Phase 3 Exit Criteria:**
- ✅ ThanatosAgent successfully blocks and requests approval for 3 destructive command types
- ✅ ThanatosAgent can execute safe commands with output captured in `AgentResult`
- ✅ HermesAgent can launch a local server and capture a screenshot
- ✅ Artifacts are correctly stored and referenced in the `AgentResult`
- ✅ Multi-hop plan "code → terminal → test" completes successfully

**Integration Checkpoint:** Archive terminal transcripts and web artifacts under `tests/e2e/.artifacts/` with metadata so the evaluation harness (Phase 4) can replay them.

## Phase 4: Intelligence and Evaluation

This phase focuses on making the agent smarter and measuring its performance.

> Dependencies: Builds on artifacts, manifests, and smoke tests from Phases 2 & 3. Provides telemetry back to earlier phases when regressions appear.

**1. Evaluation Harness:**
   - Convert the smoke tests into a formal evaluation harness under `tests/eval/`.
   - Create a dataset of tasks mapped to expected outcomes (`ChangeManifests` or `AgentResults`).
   - Automate the running of evaluations to catch regressions.

**2. `HadesAgent` (Enhanced Intelligence):**
   - Begin incorporating context from the `ProjectRegistry` and results from previous agent runs into routing decisions.
   - Lay the groundwork for integrating an LLM for true natural language understanding, moving beyond simple keyword matching.

**3. Observability:**
   - Validate that tracing is correctly configured and that spans for multi-agent plans are being exported and visualized correctly.

**Phase 4 Exit Criteria:**
- ✅ Evaluation harness runs automatically in CI with at least 20 test scenarios
- ✅ Router uses registry metadata (file counts, recent changes) in routing decisions
- ✅ Tracing spans are visible in AI Toolkit for multi-hop plans
- ✅ Regression detection catches at least one intentionally introduced bug
- ✅ LLM-based router prototype handles 3 ambiguous queries correctly

**Integration Checkpoint:** Feed evaluation summaries and tracing dashboards back into the State Check document so future roadmap revisions have measurable deltas.

---

## When to Consider Separate Projects

The monorepo approach (with package-based agent organization) should serve you well through all four phases. However, you should consider splitting agents into separate projects if:

- **Different Runtime Requirements:** An agent fundamentally needs a different language or runtime (e.g., a Node.js-based HermesAgent vs. the Python core).
- **Independent Deployment Needs:** You want to version and deploy agents separately (e.g., ThanatosAgent as a standalone CLI tool, or HermesAgent as a containerized service).
- **Team Scaling:** You have 5+ developers working on different agents simultaneously, and repository boundaries would reduce coordination overhead.
- **External Consumption:** An agent needs to be consumed by projects outside the Hades ecosystem, requiring its own release cycle and public API contract.

**None of these conditions apply at the current scale.** The package-based structure proposed in Phase 1 provides the modularity benefits without the operational complexity of managing multiple repositories.

If you eventually outgrow the monorepo, pilot the split by extracting agents with unique runtime stacks (likely `HermesAgent` if Playwright/Node-specific) into optional subpackages or git submodules. This lets you validate independent release cycles without disrupting the shared registry/orchestrator code paths.

## Risk Register & Metrics Dashboard

| Risk | Impact | Owner | Mitigation | Status Metric |
| --- | --- | --- | --- | --- |
| Registry scans remain slow even after ignore list | Blocks Router latency targets | Foundations Lead | Profile `ProjectRegistry` weekly; cache counts to disk | `registry_scan_ms` average (target < 750ms) |
| ChangeManifest/checkpoints skipped in rush fixes | Dirty repo, rollback impossible | Code/Test Lead | CI gate requiring manifest artifact | `% runs with manifest attached` |
| HITL confirmations bypassed for Terminal | Risky commands slip through | Ops Lead | Enforce policy in orchestrator; add audit log | `guarded_commands_logged` per week |
| Smoke tests rot as scope expands | False confidence, regressions | Intelligence Lead | Convert smoke to pytest + fixtures (`tests/eval/`) | `smoke_duration_s`, `scenarios_green` |

Minimum metrics to capture at the end of each phase (record in `State Check - Updated.md`):
- `registry_scan_ms`
- `guarded_commands_exercised`
- `smoke_duration_s`
- Count of evaluation scenarios run in CI

## Status Tracking & Documentation

- Create per-agent implementation notes under `docs/roadmap/<agent>.md` (see folder stub) to capture decisions, blockers, and open questions without bloating this roadmap.
- Tag issues/PRs with `phase:<n>` labels so progress reports can filter by roadmap slice.
- Append metric deltas to the State Check document after each milestone so the roadmap doubles as a status dashboard.

By following this phased roadmap, we can manage the project's complexity while ensuring that each step builds on a stable, well-structured, and safe foundation.
