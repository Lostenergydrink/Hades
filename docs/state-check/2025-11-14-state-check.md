# State Check (Integrated)

> Roadmap cross-reference: Inline tags such as `[P1-S1]` map to the matching section in `Hades/ROADMAP.md` (e.g., `[P1-S1](Hades/ROADMAP.md#phase-1-foundational-restructuring--core-safety)` is Phase 1, Step 1).

## Metrics Snapshot

| Metric | Latest Value | Source | Notes |
| --- | --- | --- | --- |
| `registry_scan_ms` | 720 ms | tests/eval/smoke_manifest.json | Phase 1 target < 750 ms; update after each registry optimization |
| `guarded_commands_exercised` | 0 (pending) | Terminal audit log | Populate once HITL wiring completes |
| `smoke_duration_s` | 65 s | tests/eval/smoke_manifest.json | Derived from baseline smoke scenario |

## Snapshot: Where Things Stand
- Router/orchestrator plumbing, context discovery, and registry caching already form a coherent skeleton (agent_app/orchestrator.py (line 22), agent_app/context_inspector.py (line 19), agent_app/registry.py (line 30)), so the folder aligns with the multi-agent plan described in AGENT_SYSTEM_DESIGN.md.
- Terminal operations feel production-ready: command parsing, confirmation keywords, and guard-rail heuristics are clearly implemented (agent_app/agents/thanatos_agent.py (line 15), agent_app/terminal_tools.py (line 33)), so controlled shell tasks are safe to run today. `[P3-Terminal](Hades/ROADMAP.md#phase-3-expanding-the-toolkit-terminal--web)`
- The Styx is still limited to syntax/import checks and launcher generation (agent_app/agents/styx_agent.py (line 20)), so "real" refactors or apply_patch-style edits aren't implemented yet and everything else falls back to an error. `[P2-CodeRefactor](Hades/ROADMAP.md#phase-2-core-agent-implementation-code--test)`
- Routing relies on a literal keyword matrix and doesn't yet look at registry metadata or past outcomes, so ambiguous tasks fall through to the Styx (agent_app/agents/hades_agent.py (line 18)). `[P4-RouterIQ](Hades/ROADMAP.md#phase-4-intelligence-and-evaluation)`
- Test Runner and Hermes (Hermes (Web Automation))s immediately return "pending" (agent_app/agents/persephone_agent.py (line 16), agent_app/agents/hermes_agent.py (line 16)), so multi-hop plans can't succeed beyond the first hop. `[P2-TestRunner](Hades/ROADMAP.md#phase-2-core-agent-implementation-code--test)` / `[P3-Web](Hades/ROADMAP.md#phase-3-expanding-the-toolkit-terminal--web)`
- Registry discovery currently walks every *.py with Path.rglob and no ignore list (agent_app/registry.py (line 65)), so large repos with venvs or artifacts make context loading slow (recent_python_files can take 5+ seconds on large directory trees). `[P1-Schemas](Hades/ROADMAP.md#phase-1-foundational-restructuring--core-safety)`
- No model invocations are wired yet; router decisions are pure keyword matching and no agent calls LLM APIs. GitHub token scopes or Azure AI Foundry endpoints still need validation via a test agent_framework.agents.Agent. `[P1-Safety](Hades/ROADMAP.md#phase-1-foundational-restructuring--core-safety)`
- StyxAgent applies changes but doesn't snapshot original content or track undo manifests (agent_app/agents/styx_agent.py (line 20)), leaving partial modifications with no rollback when hops fail. `[P1-Checkpoints](Hades/ROADMAP.md#phase-1-foundational-restructuring--core-safety)`
- Smoke tests exist (tests_smoke.py (line 18)) but lack assertions or golden outputs, so regressions can't be detected automatically; there is no evaluation harness. `[P4-Eval](Hades/ROADMAP.md#phase-4-intelligence-and-evaluation)`
- Agent result metadata is a free-form dict (issues, missing, launcher, plan, etc.), so Router summaries are fragile and can't reliably extract file changes, risk levels, or follow-up actions. `[P1-Schemas](Hades/ROADMAP.md#phase-1-foundational-restructuring--core-safety)`
- Tracing is enabled via ensure_tracing() (agent_app/observability.py (line 5)) but not validated—no spans captured, no console exporter/OTLP endpoint configured. `[P1-Safety](Hades/ROADMAP.md#phase-1-foundational-restructuring--core-safety)`
- The Microsoft Agent Framework dependency is pinned to >=0.1.0.dev0 (requirements.txt (line 1)), which is an unstable pre-release. `[Foundation-Step1](Hades/ROADMAP.md#foundation-steps-0-4)`
- Multi-hop plans run sequentially (agent_app/orchestrator.py (line 63)) but each agent re-gets the same AgentRequest, so later hops can't consume outputs from earlier ones. `[Core-Steps5-10](Hades/ROADMAP.md#core-specialists--safety-steps-5-10)`
- Thanatos emits confirmation_request for risky commands (agent_app/agents/thanatos_agent.py (line 29)), but the orchestrator never wires a user-input callback or policy checker; approvals can't be gathered. `[Core-Steps5-10](Hades/ROADMAP.md#core-specialists--safety-steps-5-10)`
- The Styx promises to "limit edits to requested scope" but lacks runtime enforcement to prevent apply_patch from touching arbitrary files outside the declared scope. `[P2-CodeRefactor](Hades/ROADMAP.md#phase-2-core-agent-implementation-code--test)`

## Pain Points & Missing Guardrails
1. **Context discovery drag** – ProjectRegistry walks `.venv`, `node_modules`, cache folders, and anything under the repo, slowing every request. `[P1-Schemas](Hades/ROADMAP.md#phase-1-foundational-restructuring--core-safety)`
2. **Unvalidated foundation** – Model credentials and tracing aren't verified, so any real execution could fail silently. `[P1-Safety](Hades/ROADMAP.md#phase-1-foundational-restructuring--core-safety)`
3. **Unstructured change data** – No ChangeManifest type, ad-hoc metadata, and no rollback snapshotting leave the repo dirty when a plan fails. `[P1-Schemas](Hades/ROADMAP.md#phase-1-foundational-restructuring--core-safety)`
4. **Specialists are stubs** – Code, Test, and Hermes (Hermes (Web Automation))s can't perform the work Router promises, collapsing multi-hop flow. `[P2-Core](Hades/ROADMAP.md#phase-2-core-agent-implementation-code--test)` / `[P3-Web](Hades/ROADMAP.md#phase-3-expanding-the-toolkit-terminal--web)`
5. **Plan outputs can't flow** – AgentRequest lacks upstream context, so downstream agents operate blind. `[Core-Steps5-10](Hades/ROADMAP.md#core-specialists--safety-steps-5-10)`
6. **Safety loop incomplete** – Terminal confirmation workflow is missing; scope enforcement is aspirational. `[Core-Steps5-10](Hades/ROADMAP.md#core-specialists--safety-steps-5-10)`
7. **Testing gap** – Smoke script lacks assertions, so regressions slip through; no evaluation harness or coverage for guardrails/routing. `[P4-Eval](Hades/ROADMAP.md#phase-4-intelligence-and-evaluation)`

## Integrated Plan & Order of Operations

### Foundation (Steps 0‑4) `[Phase 1](Hades/ROADMAP.md#phase-1-foundational-restructuring--core-safety)`
0.  **Define `ChangeManifest` and `AgentResult` schemas** (agent_app/types.py) so every agent produces structured output. `ChangeManifest` should cover `{files, summary, risk}` for writes, and `AgentResult` should standardize how findings, errors, and diagnostics are reported. `[P1-Schemas](Hades/ROADMAP.md#phase-1-foundational-restructuring--core-safety)`
1.  **Pin `agent-framework-azure-ai`** to a known dev build (e.g., `==0.1.0.dev20250114`) or vendor it (requirements.txt) to avoid surprise API breaks mid-implementation. `[P1-Safety](Hades/ROADMAP.md#phase-1-foundational-restructuring--core-safety)`
2.  **Optimize registry performance** by skipping `IGNORE_DIRS = {".venv", "venv", "node_modules", ".git", "__pycache__"}` (agent_app/registry.py (line 65)) and caching per-run stats. Without this, every agent call incurs a multi-second delay. `[P1-Structure](Hades/ROADMAP.md#phase-1-foundational-restructuring--core-safety)`
3.  **Validate model integration & tracing** – run a minimal `agent_framework.agents.Agent` against models.inference.ai.azure.com with `OTEL_EXPORTER_OTLP_ENDPOINT=http://localhost:4318` to confirm spans emit before leaning on observability. `[P1-Safety](Hades/ROADMAP.md#phase-1-foundational-restructuring--core-safety)`
4.  **Refine router keywords** – expand the literal matrix with real task samples and tie-breakers (agent_app/agents/hades_agent.py (line 18)) so requests route beyond the Styx even before ML routing arrives. `[P4-RouterIQ](Hades/ROADMAP.md#phase-4-intelligence-and-evaluation)`

### Core Specialists & Safety (Steps 5‑10) `[Phase 2 & Phase 3](Hades/ROADMAP.md#phase-2-core-agent-implementation-code--test)`
5.  **Introduce Pre-flight Validation Command** – Add a `validate-tools` or `check-env` task that verifies required executables (`git`, `ruff`), model endpoints, and tracing collectors are available and configured correctly.
6.  **Implement User Confirmation for Plans & Ops** – Before executing a multi-step plan from the Router or a high-risk command from the Thanatos, require user approval. Decide on synchronous (`input()`) vs. asynchronous (e.g., web UI) confirmation flow.
7.  **Extend StyxAgent** – add TransactionContext checkpointing under `.hades/checkpoints/<run_id>/`, enforce scope against `AgentRequest.context`, wrap `apply_patch` helpers, honor registry paths, and add diagnostics tests.
8.  **Build Persephone** – add venv-aware command helpers (reusing `python_tools` style), parse stdout/stderr into structured suites, and attach `ChangeManifest` references for Router summaries; include failure-hand-off metadata.
9.  **Wire multi-hop context passing** – extend `AgentRequest` to carry `upstream_results: list[AgentResult]` so the Test Runner knows which files changed and the Hermes (Hermes (Web Automation)) can see prior artifacts.
10. **End-to-end smoke test** – run a real "fix bug → run tests" scenario to validate rollback, confirmations, and context passing before investing in Router intelligence.

### Validation, Intelligence, and Coverage (Steps 11‑14) `[Phase 4](Hades/ROADMAP.md#phase-4-intelligence-and-evaluation)`
11. **Build evaluation harness** – turn `tests_smoke.py` into pytest cases under `tests/eval/` with JSON fixtures (task → expected `ChangeManifest`) and CI gating.
12. **Enhance Router decisioning** – once upstream data flows, teach the router to read registry stats, recent manifests, and clarifying questions instead of pure keywords; consider Microsoft Agent Framework router when models are ready.
13. **Add unit/integration coverage** – pytest suites for `CommandSafetyChecker`, registry discovery, routing, `ChangeManifest` parsing, and rollback scenarios.
14. **Introduce Centralized Configuration** – Create a `hades_config.toml` to allow explicit overrides for project roots, venv paths, and ignore patterns, reducing reliance on auto-detection.

### Deferred but Planned (Steps 15‑16)
15. **Implement Hermes (Hermes (Web Automation))** – layer Playwright runners, artifact storage under `tests/e2e/.artifacts/<timestamp>`, and selector diff summaries once Code/Test loop is reliable.
16. **Lint & terminal resilience** – add targeted globbing, better error surfacing, and regression tests for `lint_with_ruff` plus Terminal safeguards.

## Why This Order Works
- **Foundation first** – Schemas, registry speedups, and dependency pinning unblock every agent call, while validation ensures later telemetry is trustworthy.
- **Safety before execution** – User confirmation (HITL), TransactionContext, and pre-flight checks guarantee edits/tests can be approved and rolled back before automation touches the repo.
- **Tight loop focus** – Building Code → Terminal → Test with context passing yields the first useful autonomous flow; everything else (router intelligence, web automation) builds on that success.
- **Measurement baked in** – Evaluation harness and unit tests only land once the core loop exists, turning the smoke script into a guardrail instead of a checkbox.

## Structure & Environment Notes
- Keep agents under `agent_app/agents/`, but graduate heavy ones (styx_agent/, persephone_agent/, hermes_agent/) into packages so helpers and tests sit beside their agent code.
- A single shared venv is enough; each project already maintains its runtime, and `env_utils.build_env_for_context` (agent_app/env_utils.py (line 4)) activates it as needed.
- Cross-platform support maintained; containers are optional unless Linux-only tooling becomes necessary.
- Follow the guardrail ethos from `AGENT_SYSTEM_DESIGN.md`: each agent should import only the tools it needs and expose a minimal surface for auditing.

With this integrated plan, the narrative clarity from the original State Check (what works vs. what is blocked) stays intact, while the updated prioritization gives you an actionable, dependency-aware backlog.
