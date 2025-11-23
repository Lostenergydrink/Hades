from __future__ import annotations

import argparse
from pathlib import Path

from agent_app.agent_runner import run_basic_task
from agent_app.config import CONFIG


def summarize(text: str, max_lines: int = 8) -> str:
    lines = text.strip().splitlines()
    if len(lines) <= max_lines:
        return "\n".join(lines)
    shown = "\n".join(lines[:max_lines])
    return f"{shown}\n... ({len(lines) - max_lines} more lines)"


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run Hades smoke tasks")
    parser.add_argument("--start", type=Path, default=None, help="Project root to analyze")
    args = parser.parse_args()

    if args.start is not None:
        root = args.start.resolve()
    elif CONFIG.default_projects:
        root = CONFIG.default_projects[0]
    else:
        parser.print_help()
        raise SystemExit("Provide --start so the smoke script knows which project to inspect.")
    for task in [
        "check syntax",
        "lint webui",
        "import status",
        "create launcher",
    ]:
        print(f"\n=== {task} ===")
        result = run_basic_task(task, start=root)
        print(summarize(result))
