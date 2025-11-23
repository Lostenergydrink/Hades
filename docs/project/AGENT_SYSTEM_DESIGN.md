# Hades Multi-Agent System Design

This document outlines how Hades evolves from a single helper script into a routed constellation of task-specific agents. The focus is on strict tool boundaries, predictable hand-offs, and guardrails that keep each capability isolated.

## Platform + Model Strategy

- **Agent framework**: Microsoft Agent Framework (Python flavor). Install with `pip install agent-framework-azure-ai --pre`. It natively supports sequential orchestration, guarded tool calls, MCP bridges, and Azure AI / GitHub models.
- **Model mix**
  - Router / Conductor: `openai/gpt-5` (GitHub endpoint) for deep request parsing and policy reasoning.
  - Styx (Code/Refactor): `openai/gpt-5-codex` for deterministic edits and symbol-aware reasoning.
  - Furies (Lint/Format) + Test Runner: `openai/gpt-5-mini` to balance cost with deterministic instructions.
  - Thanatos (Terminal/Ops) & Hermes (Web Automation): `openai/gpt-5-chat` running in tool-only mode; pairs well with command schemas and Playwright traces.
- **Tracing**: enable Agent Framework's built-in OpenTelemetry hooks from day-one so each agent execution emits spans (`agent_framework.instrumentation.enable_tracing()`), providing guardrail auditing.

## High-Level Flow

1. **Router** receives the natural-language request plus lightweight repo metadata (project tree, recent file changes, active venv info).
2. Router selects a target agent (single hop) or composes a short plan (multi-hop) using the sequential workflow primitive.
3. Selected specialist performs work inside its sandboxed toolkit. If it cannot finish (e.g., tests fail), it annotates its reasoning and hands off back to Router for escalation.
4. Router summarizes the overall result for the end user.

All agents share a read-only project registry service for context (file listing, git summary) to avoid re-implementing discovery logic.

## Dependency Graph

The following text diagram captures run-time dependencies and the artifacts that flow between agents. Solid arrows show mandatory sequencing, while dashed arrows represent optional enrichment steps.

```
Project Registry → Router ── plan ──▶ Specialist queue
                        │                     │
                        │                     ├─▶ Styx (Code/Refactor) ──▶ ChangeManifest
                        │                     │                         │
                        │                     │                         └─▶ Test Runner ──▶ TestReport
                        │                     │                                        │
                        │                     │                                        └─▶ Router summary
                        │                     ├─▶ Thanatos (Terminal/Ops) ──▶ CommandReport ──┘
                        │                     └─▶ Hermes (Web Automation) ──▶ Artifacts ──┘
                        │
                        └─(HITL approvals)──────▶ Orchestrator guardrails
```

Key implications:
- Router cannot emit a multi-hop plan until the registry cache is warm and guardrails confirm HITL availability, so Phase 1 deliverables are hard prerequisites for every downstream agent.
- Styx (Code/Refactor) produces the ChangeManifest that gates Test Runner execution; Test Runner in turn emits structured TestReports that the Router must ingest before moving to Terminal or Web hops.
- Terminal and Hermess may run in parallel after Code/Test if the plan requires operational context or UI validation, but both must funnel artifacts back through the Router before a final summary ships.

## Agent Catalog

| Agent | Purpose | Allowed Tools | Guardrails | Typical Outputs |
| --- | --- | --- | --- | --- |
| Router / Conductor | Classify intent, draft work plan, assign agents, collect summaries. | Tool registry, lightweight code search, project metadata, conversation memory. | Cannot edit files, run commands, or mutate repo state. Must emit structured plans before delegation. | `route_decision`, `handoff_plan`, `final_summary`. |
| Styx (Code/Refactor) | Implement or modify code. | `apply_patch`, file read/write API, LSP symbols/references, static analyzers (read-only). | No git, no shell, no dependency installs, no test execution. Must confine edits to requested scope. | File diffs, rationale, follow-up todos. |
| Furies (Lint/Format) | Enforce style and quick autofixes. | `ruff`, `black`, `prettier`, config file edits. | Cannot change business logic; only style/config. Must report command invocations + results. | Lint report, optional patch snippet. |
| Thanatos (Terminal/Ops) | Execute shell commands safely. | `pwsh`/`bash` command runner, file listing, process info. | Requires confirmation for `rm`, `mv`, `chmod`, `chown`, package installs. Must default to dry-run flags when available. | Command stdout/stderr summaries, environment snapshots. |
| Persephone (Test Runner) | Owns automated tests and coverage. | `pytest`, `npm test`, Playwright CLI (test mode), coverage reporters. | Adds/updates tests via Styx, not directly. Must parse failures and suggest next steps. | Pass/fail report, parsed errors, coverage deltas. |
| Hermes (Web Automation) | Builds and maintains browser automation suites. | Playwright/Puppeteer CLIs, trace viewers, selector helpers. | No general shell access; only commands tied to automation scripts. Stores artifacts under `tests/e2e/artifacts`. | Updated scripts, trace bundles, selector diffs. |

## Router Decision Matrix

```
if request mentions "test", "coverage", "run e2e": Test Runner
elif request mentions "playwright", "browser", selector terms: Hermes (Web Automation)
elif request mentions "lint", "format", "ruff", style config: Furies (Lint/Format)
elif request mentions commands, packages, env info, "run", "start server": Thanatos (Terminal/Ops)
elif request references file edits/refactors/feature work: Styx (Code/Refactor)
else: fallback to Router summary or clarification prompt
```

Router responses must include:
- `target_agent`: string ID.
- `confidence`: 0-1 float.
- `reasoning`: short justification.
- Optional `plan`: ordered list when multiple agents need to run.

## Toolkit Details

### Shared Registry Service

- Provides cheap operations: `list_recent_files`, `get_repo_status`, `read_docs(path)`, `locate_tests(file)`.
- Backed by cached FS metadata to keep each agent fast.
- Router consumes registry results before routing; specialists can only read from it.

### Styx (Code/Refactor) Agent

- Uses `apply_patch` for deterministic edits; wraps multi-file changes in transactional batches.
- LSP assists with `find_symbol`, `references`, `rename_preview` (read-only) to plan changes.
- Maintains a change manifest for Router (`file`, `summary`, `risk_level`).

### Furies (Lint/Format) Agent

- Runs commands exactly as-logged:
  - `ruff check <paths> [--fix]`
  - `black <paths>`
  - `prettier --write <glob>`
- When touching config files (`pyproject.toml`, `.prettierrc`), changes must be accompanied by rationale.
- Fails fast if lint errors imply logic impact; escalates to Styx.

### Thanatos (Terminal/Ops) Agent

- Allowed commands: `ls`, `cat`, `git status`, `git diff`, `npm run <script>`, `pytest`, `playwright test`, env inspection.
- Confirmation workflow
  1. Detect risky command (e.g., `pip install foo`).
  2. Emit `confirmation_request` containing command, purpose, and dry-run alternative.
  3. Wait for explicit approval token from human or Router policy.
- Maintains history log for audit.
- Implementation status: `agent_app/agents/thanatos_agent.py` now wires the flow end-to-end using `terminal_tools.CommandSafetyChecker` plus the shared venv-aware env helpers in `env_utils.py`.
- Execution reports include captured stdout/stderr, duration, exit code, and are formatted for the Router to summarize downstream.

### Persephone (Test Runner) Agent

- Adds/updates tests by generating diffs, then emits `handoff_request` asking Styx to integrate.
- After running suites, parses reports into structured JSON (`suite`, `status`, `duration`, `errors`).
- Tracks flaky tests via local cache; alerts Router when failure matches known flake.

### Hermes (Web Automation) Agent

- Owns Playwright config, selectors, and trace triage.
- Uses deterministic template for new specs (naming, fixture imports, screenshot dirs).
- Stores run artifacts under `tests/e2e/.artifacts/<timestamp>` and returns summary links.

## Orchestration Patterns

1. **Single-hop**: Router → Specialist → Router (most tasks).
2. **Two-hop with validation**: Router → Styx (implements change) → Test Runner (validates) → Router.
3. **Ops-first**: Router → Thanatos (gather logs) → Router → Styx (fix) → Test Runner.
4. **Automation feedback loop**: Router → Hermes (Web Automation) (update selector) → Test Runner (run e2e) → Router.

## Next Implementation Steps

1. Scaffold Microsoft Agent Framework project (Python) under `Hades/agent_app/agents/`.
2. Encode tool permissions via framework Policies to enforce guardrails.
3. Build Router prompts + decision schema; log confidence, plan, and fallback instructions.
4. Incrementally migrate existing commands (syntax check, lint, launcher creation) into the new agent boundaries.
5. Wire tracing + runbooks so each agent execution is observable.
6. Define evaluation harness (golden tasks per agent) before enabling auto-routing in production.

This design keeps each capability auditable, predictable, and easier to extend as new specialists are added.
