from __future__ import annotations

import argparse
from pathlib import Path

from agent_app.agent_runner import run_basic_task


def main() -> None:
    parser = argparse.ArgumentParser(description="Hades basic CLI")
    parser.add_argument("task", help="High-level instruction, e.g. 'check syntax'")
    parser.add_argument("--start", type=str, help="Optional start path", default=None)
    args = parser.parse_args()

    start = Path(args.start).resolve() if args.start else None
    result = run_basic_task(args.task, start=start)
    print(result)


if __name__ == "__main__":
    main()
