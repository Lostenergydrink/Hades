# Apex Agent Test Suite

This directory contains the test suite for the Apex Agent project.

## Test Organization

The tests are organized into three categories:

### smoke/
**Smoke tests** are quick, high-level tests that verify the basic functionality of the system. They ensure that the agent can start, load configuration, and perform basic operations without crashing.

**When to run:** After every build or deployment, before running more extensive tests.

**Example tests:**
- Agent initialization
- Configuration loading
- Basic registry operations

### unit/
**Unit tests** are focused tests that verify individual components in isolation. Each agent, tool, and utility module should have corresponding unit tests.

**When to run:** During development, before committing code changes.

**Example tests:**
- Individual agent behavior
- Tool function correctness
- Utility function edge cases

### eval/
**Evaluation tests** are end-to-end tests that measure agent performance on realistic tasks. They may generate temporary artifacts (`.tmp` files) and collect metrics.

**When to run:** Before major releases, when evaluating improvements.

**Example tests:**
- Complete task execution flows
- Performance benchmarks
- Quality metrics collection

## Running Tests

### Run all tests
```bash
pytest tests/
```

### Run specific test suite
```bash
pytest tests/smoke/       # Smoke tests only
pytest tests/unit/        # Unit tests only
pytest tests/eval/        # Evaluation tests only
```

### Run with coverage
```bash
pytest --cov=agent_app tests/
```

## Test Fixtures

Common test fixtures and configuration are defined in `conftest.py` files within each test directory.
