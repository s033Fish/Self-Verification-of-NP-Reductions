"""Project workflow: validate tasks, generate runs, score them.

    uv run python -m workflow validate-tasks
    uv run python -m workflow generate --split dev --conditions c1 c3 --seeds 1
    uv run python -m workflow score --split dev
"""

from __future__ import annotations

import argparse
import sys
from collections.abc import Callable

from . import generate, score, tasks

COMMANDS: dict[str, tuple[str, Callable[[list[str]], None]]] = {
    "validate-tasks": ("validate task descriptors and inputs", tasks.main),
    "generate": ("run agents on tasks (resumable)", generate.main),
    "score": ("summarize runs against hidden-verifier verdicts", score.main),
}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, add_help=False)
    parser.add_argument("command", nargs="?")
    arguments, _ = parser.parse_known_args(sys.argv[1:2])
    if arguments.command in {None, "-h", "--help"}:
        print("usage: python -m workflow <command> [options]\n\ncommands:")
        for command, (description, _) in COMMANDS.items():
            print(f"  {command:15} {description}")
        return
    if arguments.command not in COMMANDS:
        parser.error(f"unknown command: {arguments.command}")
    COMMANDS[arguments.command][1](sys.argv[2:])


if __name__ == "__main__":
    main()