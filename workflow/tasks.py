"""Load and validate reduction task descriptors.

Each task is a directory tasks/<task_id>/ holding task.json and its input
files (at least problems.py, which defines both problems, their instance
formats and brute-force solvers). Paths are relative to the task directory;
absolute paths and `..` are rejected.

Adapted from the Assignment 2 `workflow/tasks.py`.
"""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, ValidationError, model_validator

TASK_ID = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]{0,63}$")
RESERVED_NAMES = {"reduce.py", "verdict.json", "test_reduce.py"}
REPO = Path(__file__).resolve().parents[1]


class TaskInput(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: str = Field(min_length=1, max_length=255)
    path: str = Field(min_length=1)

    @model_validator(mode="after")
    def safe_names(self) -> "TaskInput":
        if Path(self.name).name != self.name or self.name in {".", ".."}:
            raise ValueError("input name must be a plain filename")
        if self.name in RESERVED_NAMES:
            raise ValueError(f"input name {self.name!r} is reserved for agent output")
        path = Path(self.path)
        if path.is_absolute() or ".." in path.parts:
            raise ValueError("input path must be relative and may not contain '..'")
        return self


class ReductionTask(BaseModel):
    model_config = ConfigDict(extra="forbid")

    task_id: str
    source_problem: str = Field(min_length=1)
    target_problem: str = Field(min_length=1)
    famous: bool                  # textbook pair (likely memorized) or less common
    split: Literal["dev", "test"]  # tune prompts on dev only; report on test
    instructions: str = Field(min_length=1)
    inputs: list[TaskInput]

    @model_validator(mode="after")
    def valid_task(self) -> "ReductionTask":
        if not TASK_ID.fullmatch(self.task_id):
            raise ValueError(
                "task_id may contain only letters, digits, '.', '_' and '-'"
            )
        if "problems.py" not in {item.name for item in self.inputs}:
            raise ValueError("every task needs a problems.py input")
        return self


def load_tasks(root: Path) -> list[tuple[ReductionTask, Path]]:
    """Every task under root, as (task, path to its task.json), sorted by ID."""
    loaded = []
    errors = []
    for descriptor in sorted(root.glob("*/task.json")):
        try:
            task = ReductionTask.model_validate(json.loads(descriptor.read_text()))
        except (json.JSONDecodeError, ValidationError) as error:
            errors.append(f"{descriptor}: {error}")
            continue
        if task.task_id != descriptor.parent.name:
            errors.append(f"{descriptor}: task_id must match its directory name")
        for item in task.inputs:
            if not (descriptor.parent / item.path).is_file():
                errors.append(f"{descriptor}: missing input {item.path}")
        loaded.append((task, descriptor))
    if errors:
        raise ValueError("\n".join(errors))
    if not loaded:
        raise ValueError(f"no tasks found under {root}")
    return loaded


def main(argv: list[str]) -> None:
    parser = argparse.ArgumentParser(description="validate task descriptors")
    parser.add_argument("--tasks", type=Path, default=REPO / "tasks")
    arguments = parser.parse_args(argv)
    try:
        tasks = load_tasks(arguments.tasks)
    except (OSError, ValueError) as error:
        parser.error(str(error))
    by_split: dict[str, int] = {}
    for task, _ in tasks:
        by_split[task.split] = by_split.get(task.split, 0) + 1
    famous = sum(task.famous for task, _ in tasks)
    print(
        f"{len(tasks)} valid task(s): "
        + ", ".join(f"{count} {split}" for split, count in sorted(by_split.items()))
        + f"; {famous} famous, {len(tasks) - famous} less common"
    )
