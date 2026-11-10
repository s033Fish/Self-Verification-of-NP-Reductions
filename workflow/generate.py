"""Run authored tasks through the original pinned mini-SWE-agent scaffold."""

from __future__ import annotations

import argparse
import json
import shutil
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import modal
from tqdm import tqdm

from .agents import AGENT_BY_KEY, Agent
from .tasks import REPO, ReductionTask, load_tasks

RUNNER_APP = "reductions-agent-runner"
RUNNER_FUNCTION = "run_task"
CONDITIONS = ("c1", "c2", "c3", "c4", "c5")
IMPLEMENTED = ("c1", "c2", "c3")

@dataclass(frozen=True)
class Job:
    task: ReductionTask
    descriptor: Path
    agent: Agent
    condition: str
    seed: int
    sample: int | None = None

    @property
    def run_id(self) -> str:
        run_id = f"{self.task.task_id}__{self.agent.key}__{self.condition}__s{self.seed}"
        return run_id if self.sample is None else f"{run_id}__k{self.sample}"


def _json_safe(value: Any) -> Any:
    if isinstance(value, bytes):
        return {"byte_count": len(value)}
    if isinstance(value, dict):
        return {str(key): _json_safe(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [_json_safe(item) for item in value]
    if isinstance(value, (str, int, float, bool)) or value is None:
        return value
    return repr(value)


def build_jobs(
    tasks: list[tuple[ReductionTask, Path]],
    agents: list[Agent],
    conditions: list[str],
    seeds: int,
    samples: int,
) -> list[Job]:
    jobs = []
    for task, descriptor in tasks:
        for agent in agents:
            for condition in conditions:
                for seed in range(seeds):
                    if condition == "c2":
                        jobs.extend(
                            Job(task, descriptor, agent, condition, seed, sample)
                            for sample in range(samples)
                        )
                    else:
                        jobs.append(Job(task, descriptor, agent, condition, seed))
    return jobs


def build_request(job: Job) -> dict[str, Any]:
    task = job.task
    return {
        "run_id": job.run_id,
        "task": {
            "task_id": task.task_id,
            "instructions": task.instructions,
            "inputs": [item.model_dump() for item in task.inputs],
        },
        "model": job.agent.model,
        "condition": job.condition,
        "temperature": job.agent.temperature,
        "input_files": {
            item.name: (job.descriptor.parent / item.path).read_bytes()
            for item in task.inputs
        },
    }


def write_result(job: Job, runs: Path, result: dict[str, Any]) -> Path:
    destination = runs / job.run_id
    runs.mkdir(parents=True, exist_ok=True)
    staging = Path(tempfile.mkdtemp(prefix=f".{job.run_id}-", dir=runs))
    try:
        files = result.get("files") or {}
        for name, text in files.items():
            if text is not None:
                (staging / name).write_text(text)
        record = {
            "run_id": job.run_id,
            "task_id": job.task.task_id,
            "source_problem": job.task.source_problem,
            "target_problem": job.task.target_problem,
            "famous": job.task.famous,
            "split": job.task.split,
            "agent": {"key": job.agent.key, "model": job.agent.model},
            "condition": job.condition,
            "seed": job.seed,
            "sample": job.sample,
            "files_present": {name: text is not None for name, text in files.items()},
            **{
                key: _json_safe(result.get(key))
                for key in (
                    "temperature", "step_limit", "scaffold", "agent_verified",
                    "usage", "elapsed_seconds", "prompt", "outcome", "trajectory",
                )
            },
        }
        (staging / "result.json").write_text(json.dumps(record, indent=2) + "\n")
        if destination.exists():
            shutil.rmtree(destination)
        staging.rename(destination)
    except BaseException:
        shutil.rmtree(staging, ignore_errors=True)
        raise
    return destination


def main(argv: list[str]) -> None:
    parser = argparse.ArgumentParser(description="generate agent runs")
    parser.add_argument("--tasks", type=Path, default=REPO / "tasks")
    parser.add_argument("--runs", type=Path, default=REPO / "runs")
    parser.add_argument("--split", choices=("dev", "test", "all"), default="dev")
    parser.add_argument(
        "--models", nargs="+", choices=tuple(AGENT_BY_KEY), default=list(AGENT_BY_KEY)
    )
    parser.add_argument(
        "--conditions", nargs="+", choices=CONDITIONS, default=list(IMPLEMENTED)
    )
    parser.add_argument("--seeds", type=int, default=3)
    parser.add_argument("--samples", type=int, default=4, help="k for best-of-k (c2)")
    parser.add_argument("--force", action="store_true", help="replace existing runs")
    parser.add_argument(
        "--dry-run", action="store_true", help="list the runs without starting them"
    )
    arguments = parser.parse_args(argv)

    not_ready = sorted(set(arguments.conditions) - set(IMPLEMENTED))
    if not_ready:
        parser.error(f"condition(s) not implemented yet: {', '.join(not_ready)}")
    agents = [AGENT_BY_KEY[key] for key in arguments.models]
    for agent in agents:
        if agent.missing_settings():
            parser.error(f"{agent.key}: set {', '.join(agent.missing_settings())} in .env")
    try:
        tasks = load_tasks(arguments.tasks)
    except (OSError, ValueError) as error:
        parser.error(str(error))
    if arguments.split != "all":
        tasks = [(task, path) for task, path in tasks if task.split == arguments.split]

    jobs = build_jobs(tasks, agents, arguments.conditions, arguments.seeds, arguments.samples)
    pending = [
        job for job in jobs
        if arguments.force or not (arguments.runs / job.run_id).exists()
    ]
    print(f"{len(jobs)} run(s) requested, {len(jobs) - len(pending)} already done, "
          f"{len(pending)} to start")
    if arguments.dry_run or not pending:
        for job in pending:
            print(f"  {job.run_id}")
        return

    remote = modal.Function.from_name(RUNNER_APP, RUNNER_FUNCTION)
    calls = [(job, remote.spawn(build_request(job))) for job in pending]
    failures = 0
    for job, call in tqdm(calls, unit="run"):
        try:
            written = write_result(job, arguments.runs, call.get())
            tqdm.write(f"wrote {written.name}")
        except Exception as error:
            failures += 1
            tqdm.write(f"ERROR {job.run_id}: {error}")
    if failures:
        raise SystemExit(f"{failures} run(s) failed; rerun the same command to resume")