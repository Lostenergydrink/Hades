# Hades 🔱

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![Development Status](https://img.shields.io/badge/status-alpha-orange)](https://github.com/Lostenergydrink/Hades/blob/master/docs/project/ROADMAP.md)
[![Phase](https://img.shields.io/badge/phase-1%20complete%20%7C%202%20in%20progress-blue)](https://github.com/Lostenergydrink/Hades/blob/master/docs/project/ROADMAP.md)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Lint: Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)
[![CI](https://github.com/Lostenergydrink/Hades/workflows/Lint%20and%20Smoke%20Tests/badge.svg)](https://github.com/Lostenergydrink/Hades/actions)

> **Multi-agent AI framework with mythology-themed specialists**

Named after the Greek god of the underworld, Hades brings order to the chaos beneath the surface—routing, refactoring, enforcing standards, executing commands, validating tests, and automating workflows.

**🎯 Phase 1 Complete** | **🚧 Phase 2 In Progress** | **📦 MIT Licensed**

> ⚠️ **Alpha Status**: This project is under active development. APIs may change between versions. See [ROADMAP](docs/project/ROADMAP.md) for planned features.

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

## ⚡ Quick Start

```powershell
# Clone and setup
git clone https://github.com/Lostenergydrink/Hades.git
cd Hades

# Create virtual environment
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt

# Verify installation
python scripts/check-env.ps1

# Example usage
python scripts/main.py "check syntax"
python scripts/main.py "lint --fix"
python scripts/main.py "run pytest"
```

## ✨ Features

- **🎭 Six Specialized Agents** - Each with distinct responsibilities and safety guardrails
- **🛡️ Built-in Safety Nets** - Automatic checkpointing, HITL confirmations, output sanitization
- **📊 Structured Types** - Type-safe schemas for all agent interactions
- **🔍 Observability** - OpenTelemetry tracing for debugging and monitoring
- **✅ Comprehensive Testing** - Unit tests, smoke tests, and CI/CD integration
- **📝 Extensive Documentation** - Architecture guides, API docs, and usage examples

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

## 🧪 Testing

Run the test suite to validate functionality:

```powershell
# Unit tests
pytest tests/unit/

# Smoke tests
pytest tests/smoke/

# Full test suite with coverage
pytest --cov=agent_app tests/
```

## 📚 Documentation

- **[Architecture Design](docs/project/AGENT_SYSTEM_DESIGN.md)** - System overview and design principles
- **[Safety Nets](docs/guides/SAFETY_NETS_SUMMARY.md)** - Built-in protection mechanisms
- **[Types Guide](docs/types_usage_guide.md)** - Type system and schemas
- **[Contributing](CONTRIBUTING.md)** - Development guidelines
- **[Roadmap](docs/project/ROADMAP.md)** - Future plans and phases

## 🤝 Contributing

Contributions are welcome! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

Built with:
- [Python 3.11+](https://www.python.org/)
- [Ruff](https://github.com/astral-sh/ruff) - Fast Python linter
- [Black](https://github.com/psf/black) - Code formatter
- [OpenTelemetry](https://opentelemetry.io/) - Observability framework

---

**Made with ⚡ by the Hades team**
