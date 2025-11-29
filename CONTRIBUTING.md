# Contributing to Hades

Thank you for your interest in contributing to Hades! This document provides guidelines and best practices for contributing to the project.

## Development Environment

### Virtual Environment Setup

```powershell
# Create virtual environment
python -m venv .venv

# Activate the environment
.venv\Scripts\Activate.ps1

# Install dependencies
pip install -r requirements.txt
```

### Required Tools

- **Python 3.11+**: The project targets Python 3.11 or higher
- **Ruff**: Fast Python linter and formatter
- **Black**: Code formatter (backup/compatibility)
- **MyPy**: Static type checker
- **Pytest**: Testing framework

All dependencies are pinned in `requirements.txt`.

## Code Style and Standards

### Linting and Formatting

Hades uses **Ruff** as the primary linter and formatter. Code must pass linting checks before merging.

#### Running Lint Checks

```powershell
# Check code for issues
ruff check agent_app/ tests/

# Auto-fix safe issues
ruff check --fix agent_app/ tests/

# Format code
ruff format agent_app/ tests/
```

#### Using the Make Script

The project includes a PowerShell make script for common tasks:

```powershell
# Run linter
.\scripts\make.ps1 lint

# Run all tests
.\scripts\make.ps1 test

# Run smoke tests only
.\scripts\make.ps1 smoke

# Run unit tests only
.\scripts\make.ps1 unit

# Launch the agent
.\scripts\make.ps1 launch

# Clean workspace
.\scripts\make.ps1 clean
```

#### Using VS Code Tasks

Tasks are configured in `.vscode/tasks.json` and can be run via:
- `Ctrl+Shift+B` → Select task
- Terminal → Run Task

Available tasks:
- **Launch Hades**
- **Run All Tests**
- **Run Smoke Tests**
- **Run Unit Tests**
- **Run Lint**
- **Clean Workspace**

### Type Hints

All code should include proper type hints. Use the `types.py` module for project-specific types:

```python
from agent_app.types import AgentConfig, ToolResult, ExecutionContext
```

See `docs/types_usage_guide.md` for detailed guidance.

### Code Organization

- **agent_app/**: Core agent framework and orchestration
- **agent_app/agents/**: Specialized agent implementations
  - `hades/`: Intent classification and planning (Router/Orchestrator)
  - `styx/`: AST inspection, refactoring, launcher generation (Code/Refactor)
  - `furies/`: Ruff/Black/Prettier execution (Lint/Format)
  - `thanatos/`: Guarded shell command execution (Terminal/Ops)
  - `persephone/`: Test runner and QA automation (Test Runner)
  - `hermes/`: Playwright/Puppeteer automation (Web Automation)
- **tests/**: Test suites
  - `unit/`: Unit tests
  - `smoke/`: Smoke tests
  - `eval/`: Evaluation tests (manual trigger)
- **config/**: Configuration files
- **scripts/**: Utility scripts and launchers
- **docs/**: Documentation

## Testing

### Running Tests Locally

Before submitting a PR, ensure all tests pass:

```powershell
# Run all tests
python -m pytest tests/ -v

# Run smoke tests (fast integration checks)
python -m pytest tests/smoke/ -v

# Run unit tests only
python -m pytest tests/unit/ -v

# Run with coverage
coverage run -m pytest tests/smoke/ -v
coverage report
coverage xml
```

### Writing Tests

- **Unit tests**: Test individual functions/classes in isolation
- **Smoke tests**: Test end-to-end workflows with real agent execution
- **Evaluation tests**: Manual trigger only, for performance benchmarks

Follow the existing test structure in `tests/` directories.

## Continuous Integration

GitHub Actions runs automated checks on all PRs:

1. **Lint Job**: Runs Ruff linter on all Python code
2. **Smoke Tests Job**: Executes smoke test suite with coverage reporting

All checks must pass before merging.

### CI Pipeline Details

- Workflow file: `.github/workflows/lint-and-smoke.yml`
- Triggered on: push to `main`/`develop`, PRs to `main`/`develop`
- Python version: 3.11
- Coverage reporting: XML format via `coverage[toml]`

## Project Structure Conventions

### Virtual Environment Location

Use `.venv` in the project root or a custom location configured in your environment. The launcher generation logic will detect virtual environments automatically.

### Project Detection

The agent auto-detects project roots. Entry point detection prioritizes:

1. `main.py`
2. `app.py`
3. `webui.py`
4. `<project>.py`
5. `launch.py`
6. `run.py`
7. Newest `.py` file (fallback)

### Command Safety

Terminal/Ops agent has built-in safety checks:

- **Destructive operations** require explicit `confirm: yes`
- **High-risk commands** (format, diskpart, shutdown) are blocked
- Commands execute in project root with project venv activated

## Documentation

### Updating Documentation

When adding features or making significant changes:

1. Update relevant documentation in `docs/`
2. Update `README.md` if user-facing behavior changes
3. Update `AGENT_SYSTEM_DESIGN.md` for architectural changes
4. Add entries to `ROADMAP.md` for planned work

### Documentation Structure

- `README.md`: Quick start and overview
- `AGENT_SYSTEM_DESIGN.md`: System architecture and design decisions
- `ROADMAP.md`: Planned features and development phases
- `docs/roadmap/`: Per-agent roadmap documents
- `docs/state-check/`: Milestone checkpoints and status updates

## Pull Request Guidelines

### Before Submitting

- [ ] Run linting: `.\scripts\make.ps1 lint`
- [ ] Run tests: `.\scripts\make.ps1 test`
- [ ] Update documentation if needed
- [ ] Add tests for new functionality
- [ ] Ensure type hints are complete

### PR Description

Include:
- **What**: Summary of changes
- **Why**: Motivation and context
- **How**: Implementation approach
- **Testing**: How changes were tested
- **Related Issues**: Reference any related issues

### Review Process

1. CI checks must pass
2. At least one maintainer approval required
3. Address review feedback
4. Squash or rebase before merge

## Getting Help

- **Issues**: Check existing issues or open a new one
- **Discussions**: For questions and design discussions
- **Documentation**: See `docs/` directory for detailed guides

## Code of Conduct

- Be respectful and professional
- Provide constructive feedback
- Focus on the code, not the person
- Help create a welcoming environment

## License

By contributing, you agree that your contributions will be licensed under the same license as the project.
