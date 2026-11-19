"""Generate agent runs: tasks x agents x conditions x seeds, in parallel on Modal.

Each run is written to runs/<run_id>/ with result.json and the files the agent
left (reduce.py, verdict.json, test_reduce.py). Runs that already exist are
skipped, so an interrupted batch resumes where it stopped.

    uv run python -m workflow generate --split dev --conditions c1 c3 --seeds 1

Adapted from the Assignment 2 `workflow/generate.py`. Runs go out in
parallel and are saved as they finish; the runner caps concurrency.
"""

from __future__ import annotations

import argparse
import inspect
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
CONDITIONS = ("c1", "c2", "c3", "c3n", "c4", "c5", "c5x")
IMPLEMENTED = CONDITIONS
# Conditions whose agents get problems_nosolver.py (specs and validate() only)
# as their problems.py. The verifier always judges with the full library.
NO_SOLVER_CONDITIONS = {"c3n", "c4", "c5", "c5x"}
# c5x: the cross-model tester. It reviews the reduce.py of the c5 run with the
# same task, writer and seed, so c5 and c5x judge identical reductions and only
# the tester's model differs. Run c5 first.
REVIEW_CONDITIONS = {"c5x": "c5"}
NOSOLVER_FILE = "problems_nosolver.py"


@dataclass(frozen=True)
class Job:
    task: ReductionTask
    descriptor: Path
    agent: Agent
    condition: str
    seed: int
    sample: int | None = None  # best-of-k sample index, c2 only

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


def cross_tester(agent: Agent) -> Agent:
    """The other model: each writer is reviewed by the next agent in AGENTS."""
    keys = list(AGENT_BY_KEY)
    return AGENT_BY_KEY[keys[(keys.index(agent.key) + 1) % len(keys)]]


def writer_run(job: Job, runs: Path) -> Path:
    """For a review condition, the run whose writer it reviews."""
    source = REVIEW_CONDITIONS[job.condition]
    return runs / job.run_id.replace(f"__{job.condition}__", f"__{source}__", 1)


def _read_optional(path: Path) -> str | None:
    return path.read_text() if path.is_file() else None


def problem_spec(task: ReductionTask) -> str:
    """The SOURCE and TARGET docstrings, as the agent sees them in the prompt.
    Taken from the trusted library, which make_task bundles into problems.py."""
    from benchmark.problems import PROBLEMS

    by_name = {problem.name: problem for problem in PROBLEMS.values()}
    parts = []
    for role, name in (("SOURCE", task.source_problem), ("TARGET", task.target_problem)):
        problem = by_name[name]
        parts.append(f"{role} = {problem.__name__}\n{inspect.cleandoc(problem.__doc__ or '')}")
    return "\n\n".join(parts)


def build_request(job: Job, runs: Path = REPO / "runs") -> dict[str, Any]:
    task = job.task
    input_files = {
        item.name: (job.descriptor.parent / item.path).read_bytes() for item in task.inputs
    }
    solvers_provided = job.condition not in NO_SOLVER_CONDITIONS
    if not solvers_provided:
        input_files["problems.py"] = (
            job.descriptor.parent / "inputs" / NOSOLVER_FILE
        ).read_bytes()
    review: dict[str, Any] = {}
    if job.condition in REVIEW_CONDITIONS:
        source = writer_run(job, runs)
        record = json.loads((source / "result.json").read_text())
        tester = cross_tester(job.agent)
        review = {
            "writer": {
                "run_id": source.name,
                "exit_status": record.get("exit_status"),
                "files": {
                    "reduce.py": _read_optional(source / "reduce.py"),
                    "verdict.json": _read_optional(source / "writer_verdict.json"),
                    "test_reduce.py": _read_optional(source / "writer_test_reduce.py"),
                },
            },
            "tester": {
                "key": tester.key,
                "model": tester.model,
                "temperature": tester.temperature,
                "max_tokens": tester.max_tokens,
            },
        }
    return {
        **review,
        "run_id": job.run_id,
        "task": {
            "task_id": task.task_id,
            "instructions": task.instructions,
            "inputs": [item.model_dump() for item in task.inputs],
            "spec": problem_spec(task),
            "source_problem": task.source_problem,
            "target_problem": task.target_problem,
            "solvers_provided": solvers_provided,
        },
        "model": job.agent.model,
        "condition": job.condition,
        "temperature": job.agent.temperature,
        "max_tokens": job.agent.max_tokens,
        "input_files": input_files,
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
            "solvers_provided": job.condition not in NO_SOLVER_CONDITIONS,
            "seed": job.seed,
            "sample": job.sample,
            "files_present": {name: text is not None for name, text in files.items()},
            **{
                key: _json_safe(result.get(key))
                for key in (
                    "exit_status", "temperature", "max_tokens", "step_limit", "scaffold", "agent_verified",
                    "usage", "replies_without_tool_calls", "oracle_log", "elapsed_seconds", "prompt",
                    "outcome", "trajectory", "writer_verified", "tester_first_call",
                    "tester_exit_status", "tester_prompt", "tester_trajectory",
                    "tester_model", "writer_run",
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
    # k = 3: close to c3n's token cost for both models (dev pilot: a c1 run is
    # about 35k / 28k tokens, c3n about 70k / 84k for DeepSeek / GPT-OSS).
    parser.add_argument("--samples", type=int, default=3, help="k for best-of-k (c2)")
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
    missing = [
        job for job in pending
        if job.condition in REVIEW_CONDITIONS
        and not (writer_run(job, arguments.runs) / "result.json").exists()
    ]
    if missing:
        print(f"skipping {len(missing)} review run(s) whose writer run does not exist yet "
              f"(e.g. {writer_run(missing[0], arguments.runs).name}); generate it first")
        pending = [job for job in pending if job not in missing]
    print(f"{len(jobs)} run(s) requested, {len(jobs) - len(pending)} already done, "
          f"{len(pending)} to start")
    if arguments.dry_run or not pending:
        for job in pending:
            print(f"  {job.run_id}")
        return

    remote = modal.Function.from_name(RUNNER_APP, RUNNER_FUNCTION)
    by_run_id = {job.run_id: job for job in pending}
    failures = 0
    # order_outputs=False: each run is saved as soon as it finishes. The runner
    # returns failures as {"run_id", "error"} instead of raising.
    results = remote.map(
        [build_request(job, arguments.runs) for job in pending],
        order_outputs=False,
        return_exceptions=True,
    )
    for result in tqdm(results, total=len(pending), unit="run"):
        if isinstance(result, BaseException) or result.get("error"):
            failures += 1
            run_id = None if isinstance(result, BaseException) else result.get("run_id")
            message = result if isinstance(result, BaseException) else result["error"]
            tqdm.write(f"ERROR {run_id or '(unknown run)'}: {message}")
            continue
        job = by_run_id[result["run_id"]]
        written = write_result(job, arguments.runs, result)
        tqdm.write(f"wrote {written.name}  [{result.get('exit_status') or 'no exit status'}]")
    if failures:
        raise SystemExit(f"{failures} run(s) failed; rerun the same command to resume")