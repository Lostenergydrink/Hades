# Hades

Multi-agent debugging and development assistant for Windows Python projects.
Named after the Greek god of the underworld, Hades brings order to the chaos beneath the surface—routing, refactoring, enforcing standards, executing commands, validating tests, and automating workflows.

## The Pantheon

Each agent is named after a figure from Greek mythology, reflecting its role:

| Agent | Mythological Role | Function |
|-------|------------------|----------|
| **Hades** | King of the Underworld, supreme judge | Router/Orchestrator - classifies intent and routes to specialists |
| **Styx** | River of binding oaths, foundation | Code/Refactor - AST analysis, code transformations |
| **Furies** | Enforcers of cosmic law | Lint/Format - Ruff, Black, style enforcement |
| **Thanatos** | God of death and execution | Terminal/Ops - executes shell commands with safety checks |
| **Persephone** | Goddess of spring and rebirth | Test Runner - validation, pytest execution |
| **Hermes** | Messenger god, swift traveler | Hermes (Web Automation) - Playwright/Puppeteer orchestration |

## Quick start

```powershell
# Clone and setup
cd <your-projects-directory>
git clone https://github.com/yourusername/hades
cd hades

# Create virtual environment
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt

# Example usage
.\launch_hades.ps1 "check syntax"
.\launch_hades.ps1 "create launcher" --start <path-to-your-project>
.\launch_hades.ps1 "lint webui"
.\launch_hades.ps1 "import status"
```

## Architecture

**Hades** (the router) applies a deterministic keyword matrix to classify user intent and delegates to specialist agents:

- **Styx** handles code refactoring, AST inspections, and launcher generation (safe file edits only)
- **Furies** enforces code style with Ruff/Black/Prettier
- **Thanatos** executes shell commands with safety guardrails and confirmation prompts
- **Persephone** runs test suites (pytest/npm) and parses reports
- **Hermes** orchestrates web automation with Playwright, managing traces and selectors

Multi-step plans like `[styx -> persephone]` (refactor then test) are supported. Hades falls back to Styx when intent is ambiguous. All agents have read-only access to the project registry (metadata, file lists)
and Furiess currently execute real work.

## Built-in tasks

- `check syntax` — **Styx** parses the detected project entry point via Python's AST
- `lint webui [--fix]` — **Furies** runs Ruff and optionally applies safe fixes
- `import status` — **Styx** inspects imports, showing which resolve locally or via installed packages
- `create launcher` — **Styx** generates PowerShell and batch launcher scripts

Entry point detection prioritizes `main.py`, `app.py`, `webui.py`, `<project>.py`, `launch.py`, or `run.py` before falling back to the newest `.py` file.

### Thanatos (Terminal) usage

- Provide commands via `run <cmd>` or `command: <cmd>` in the task text, e.g. `run git status`
- Destructive operations (installers, file moves, `git clean`) are paused unless you append `confirm: yes`
- High-risk commands such as `format`, `diskpart`, and `shutdown` are blocked outright
- Execution happens inside the detected project root with the project venv activated

## Tracing & observability

Tracing is wired through `agent_framework.observability.setup_observability`. To
view spans in the AI Toolkit collector:

```powershell
# Inside VS Code, run the AI Toolkit "Open Tracing" command once per session.
ai-mlstudio.tracing.open

# The orchestrator will auto-connect to http://localhost:4317 on first use.
```

## Smoke test

Validate the current routing + command implementations:

```powershell
python tests_smoke.py --start <path-to-your-project>
```

`--start` makes the smoke tasks explicit so legacy projects (e.g., StyleTTS) do not influence new work. If omitted, the script falls back to the first `default_projects` entry (currently empty). The script only prints the first few lines of each command for readability.
