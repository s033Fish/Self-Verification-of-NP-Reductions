"""The hidden verifier: decides whether an agent's reduce.py is correct.

A reduction from SOURCE to TARGET is correct only if it passes every check:

1. Exhaustive  For every source instance up to SOURCE.exhaustive_scale, the
               output is a valid TARGET instance and
               SOURCE.is_yes(x) == TARGET.is_yes(reduce(x)).
2. Random      The same check on random instances one and two scales larger.
3. Scaling     reduce runs on random instances over a range of sizes, without
               solving them. Output size must stay polynomial: the fitted
               exponent of output size against input size is at most 4, and
               every output is at most 50 * (input size)^4. Time is fitted
               and reported too.

Verdicts:
  correct       every check passed
  wrong         at least one failure; `category` names the failure behind the
                smallest counterexample, `failures` counts every category
  inconclusive  no failure, but too few instances could be checked because
                the library's own solver timed out on large reduced instances.
                Never counted as correct.

Failure categories: no_reduce_file, crash, solver_call, timeout,
malformed_output, wrong_answer_yes_to_no, wrong_answer_no_to_yes, blowup.

    uv run python -m benchmark.verify                       # every run in runs/
    uv run python -m benchmark.verify --run RUN_ID          # selected runs
    uv run python -m benchmark.verify --reduce gold.py --task TASK_ID
"""

from __future__ import annotations

import argparse
import json
import math
import os
import random
import select
import shutil
import signal
import subprocess
import sys
import tempfile
import time
from concurrent.futures import ProcessPoolExecutor, as_completed
from contextlib import contextmanager
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, Iterator

from benchmark.problems import PROBLEMS, Problem
from benchmark.problems.base import canonical

VERIFIER_VERSION = "1.0"
REPO = Path(__file__).resolve().parents[1]
CHILD = Path(__file__).resolve().parent / "sandbox_child.py"
MAX_STORED_CHARS = 4000  # target instances longer than this are truncated in verdicts
MAX_SOLVED_SIZE = 20_000  # larger reduced instances are left unchecked, not solved


@dataclass(frozen=True)
class Settings:
    call_timeout: float = 2.0          # seconds per reduce call
    startup_timeout: float = 15.0      # seconds to import reduce.py
    solver_timeout: float = 5.0        # seconds for the library to solve one instance pair
    random_extra_scales: tuple[int, ...] = (1, 2)
    random_per_scale: int = 50
    min_random_checked: int = 50       # fewer checked random instances -> inconclusive
    max_random_failures: int = 5
    random_phase_seconds: float = 120.0
    scaling_points: int = 5            # distinct source scales in the scaling phase
    scaling_draws: int = 5             # instances per scale
    max_size_exponent: float = 4.0
    size_constant: float = 50.0
    memory_mb: int = 2048


class SolverTimeout(Exception):
    pass


_alarm_armed = False


def _on_alarm(signum, frame) -> None:
    # Raise only inside time_limit. A late alarm (macOS can deliver the signal
    # after the timer is cancelled) is ignored instead of killing the process.
    if _alarm_armed:
        raise SolverTimeout()


@contextmanager
def time_limit(seconds: float) -> Iterator[None]:
    """Raise SolverTimeout after `seconds` (Unix, main thread only; otherwise
    no limit is applied)."""
    global _alarm_armed
    if not hasattr(signal, "setitimer"):
        yield
        return
    try:
        # Installed once and never removed, so SIGALRM's default action
        # (terminate the process) can never apply.
        if signal.getsignal(signal.SIGALRM) is not _on_alarm:
            signal.signal(signal.SIGALRM, _on_alarm)
    except ValueError:  # not in the main thread
        yield
        return
    _alarm_armed = True
    signal.setitimer(signal.ITIMER_REAL, seconds)
    try:
        yield
    finally:
        _alarm_armed = False
        signal.setitimer(signal.ITIMER_REAL, 0)


# --- Sandbox ----------------------------------------------------------------------


class Sandbox:
    """One long-lived child process running the agent's reduce()."""

    def __init__(self, workdir: Path, settings: Settings) -> None:
        self.settings = settings
        self.process = subprocess.Popen(
            [sys.executable, "-I", str(CHILD), str(workdir), str(settings.memory_mb)],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
            cwd=workdir,
            env={"PATH": os.environ.get("PATH", ""), "PYTHONHASHSEED": "0"},
            text=True,
            bufsize=1,
        )
        self.dead = False

    def _receive(self, timeout: float) -> dict[str, Any] | None:
        assert self.process.stdout is not None
        ready, _, _ = select.select([self.process.stdout], [], [], timeout)
        if not ready:
            return None
        line = self.process.stdout.readline()
        if not line:
            self.dead = True
            return {"ok": False, "ready": False, "kind": "crash", "error": "sandbox process exited"}
        return json.loads(line)

    def start(self) -> dict[str, Any]:
        message = self._receive(self.settings.startup_timeout)
        if message is None:
            self.close()
            return {"ready": False, "kind": "timeout", "error": "importing reduce.py timed out"}
        return message

    def call(self, instance: Any) -> dict[str, Any]:
        assert self.process.stdin is not None
        try:
            self.process.stdin.write(json.dumps({"instance": instance}) + "\n")
            self.process.stdin.flush()
        except BrokenPipeError:
            self.dead = True
            return {"ok": False, "kind": "crash", "error": "sandbox process exited"}
        reply = self._receive(self.settings.call_timeout)
        if reply is None:
            self.close()
            return {"ok": False, "kind": "timeout",
                    "error": f"reduce took longer than {self.settings.call_timeout} s"}
        return reply

    def close(self) -> None:
        self.dead = True
        if self.process.poll() is None:
            self.process.kill()
        self.process.wait()


# --- Verdict bookkeeping ----------------------------------------------------------------


@dataclass
class Verdict:
    status: str = "correct"
    category: str | None = None
    counterexample: dict[str, Any] | None = None
    failures: dict[str, int] = field(default_factory=dict)
    checked: dict[str, int] = field(default_factory=lambda: {
        "exhaustive": 0, "exhaustive_unchecked": 0,
        "random": 0, "random_unchecked": 0, "scaling": 0,
    })
    scaling: dict[str, Any] | None = None
    verifier_version: str = VERIFIER_VERSION
    seconds: float = 0.0
    _best_size: float = math.inf

    def fail(self, category: str, phase: str, source: type[Problem], x: Any,
             error: str | None = None, expected: bool | None = None,
             got: bool | None = None, output: Any = None) -> None:
        self.status = "wrong"
        self.failures[category] = self.failures.get(category, 0) + 1
        size = source.size(x) if x is not None else -1
        if size < self._best_size:  # keep the smallest counterexample
            self._best_size = size
            self.category = category
            stored_output = None
            if output is not None:
                text = canonical(output) if isinstance(output, dict) else json.dumps(output)
                stored_output = output if len(text) <= MAX_STORED_CHARS else text[:MAX_STORED_CHARS] + "...(truncated)"
            self.counterexample = {
                "phase": phase, "category": category, "source_instance": x,
                "expected": expected, "got": got, "target_instance": stored_output,
                "error": error,
            }

    def to_json(self) -> dict[str, Any]:
        data = asdict(self)
        data.pop("_best_size")
        return data


# --- Checks -----------------------------------------------------------------------


def _check_pair(verdict: Verdict, phase: str, source: type[Problem], target: type[Problem],
                x: Any, reply: dict[str, Any], settings: Settings) -> bool | None:
    """Record the outcome of one reduce call. True = agreed, False = failure,
    None = could not be checked (library solver timed out)."""
    if not reply.get("ok"):
        verdict.fail(reply["kind"], phase, source, x, error=reply.get("error"))
        return False
    y = reply["output"]
    try:
        target.validate(y)
    except Exception as error:  # InvalidInstance, or any error on a malformed object
        verdict.fail("malformed_output", phase, source, x, error=str(error)[:500], output=y)
        return False
    if target.size(y) > MAX_SOLVED_SIZE:
        return None
    try:
        with time_limit(settings.solver_timeout):
            expected = source.is_yes(x)
            got = target.is_yes(y)
    except (SolverTimeout, MemoryError, RecursionError):
        return None
    if expected != got:
        category = "wrong_answer_yes_to_no" if expected else "wrong_answer_no_to_yes"
        verdict.fail(category, phase, source, x, expected=expected, got=got, output=y)
        return False
    return True


def _fit_exponent(points: list[tuple[float, float]]) -> float | None:
    """Least-squares slope of log(y) against log(x)."""
    usable = [(math.log(x), math.log(y)) for x, y in points if x > 1 and y > 0]
    if len({round(px, 9) for px, _ in usable}) < 2:
        return None
    mean_x = sum(px for px, _ in usable) / len(usable)
    mean_y = sum(py for _, py in usable) / len(usable)
    spread = sum((px - mean_x) ** 2 for px, _ in usable)
    return sum((px - mean_x) * (py - mean_y) for px, py in usable) / spread


def scaling_scales(source: type[Problem], points: int) -> list[int]:
    low = max(source.exhaustive_scale, 2)
    high = max(4 * source.exhaustive_scale, source.exhaustive_scale + 12)
    return sorted({round(low + (high - low) * i / (points - 1)) for i in range(points)})


def verify_reduction(
    reduce_file: Path,
    problems_file: Path,
    source: type[Problem],
    target: type[Problem],
    settings: Settings = Settings(),
    seed: str = "verifier",
) -> Verdict:
    """Run every check on one reduce.py. See the module docstring."""
    started = time.monotonic()
    verdict = Verdict()
    if not reduce_file.is_file():
        verdict.fail("no_reduce_file", "setup", source, None, error=f"{reduce_file.name} not found")
        verdict.seconds = round(time.monotonic() - started, 3)
        return verdict

    with tempfile.TemporaryDirectory(prefix="verify-") as raw:
        workdir = Path(raw)
        shutil.copy(problems_file, workdir / "problems.py")
        shutil.copy(reduce_file, workdir / "reduce.py")
        sandbox = Sandbox(workdir, settings)
        try:
            _run_phases(verdict, sandbox, source, target, settings, seed)
        finally:
            sandbox.close()

    if verdict.status == "correct" and (
        verdict.checked["exhaustive_unchecked"] > 0
        or verdict.checked["random"] < settings.min_random_checked
    ):
        verdict.status = "inconclusive"
    verdict.seconds = round(time.monotonic() - started, 3)
    return verdict


def _run_phases(verdict: Verdict, sandbox: Sandbox, source: type[Problem],
                target: type[Problem], settings: Settings, seed: str) -> None:
    ready = sandbox.start()
    if not ready.get("ready"):
        verdict.fail(ready.get("kind", "crash"), "setup", source, None, error=ready.get("error"))
        return

    # 1. Exhaustive small instances.
    for x in source.enumerate_instances(source.exhaustive_scale):
        outcome = _check_pair(verdict, "exhaustive", source, target, x, sandbox.call(x), settings)
        if outcome is None:
            verdict.checked["exhaustive_unchecked"] += 1
        else:
            verdict.checked["exhaustive"] += 1
        if sandbox.dead:
            return

    # 2. Random instances at larger scales.
    rng = random.Random(f"{seed}:random")
    deadline = time.monotonic() + settings.random_phase_seconds
    random_failures = 0
    for extra in settings.random_extra_scales:
        for _ in range(settings.random_per_scale):
            if time.monotonic() > deadline or random_failures >= settings.max_random_failures:
                break
            x = source.random_instance(rng, source.exhaustive_scale + extra)
            outcome = _check_pair(verdict, "random", source, target, x, sandbox.call(x), settings)
            if outcome is None:
                verdict.checked["random_unchecked"] += 1
            elif outcome:
                verdict.checked["random"] += 1
            else:
                random_failures += 1
            if sandbox.dead:
                return

    if verdict.status == "wrong":
        return  # already wrong; skip the scaling phase

    # 3. Scaling: output size and time against input size, without solving.
    rng = random.Random(f"{seed}:scaling")
    size_points: list[tuple[float, float]] = []
    time_points: list[tuple[float, float]] = []
    for scale in scaling_scales(source, settings.scaling_points):
        for _ in range(settings.scaling_draws):
            x = source.random_instance(rng, scale)
            reply = sandbox.call(x)
            if not reply.get("ok"):
                verdict.fail(reply["kind"], "scaling", source, x, error=reply.get("error"))
                return
            y = reply["output"]
            try:
                target.validate(y)
            except Exception as error:
                verdict.fail("malformed_output", "scaling", source, x, error=str(error)[:500], output=y)
                return
            n_in, n_out = source.size(x), target.size(y)
            verdict.checked["scaling"] += 1
            size_points.append((n_in, max(n_out, 1)))
            if reply["seconds"] >= 1e-4:
                time_points.append((n_in, reply["seconds"]))
            if n_out > settings.size_constant * max(n_in, 1) ** settings.max_size_exponent:
                verdict.fail("blowup", "scaling", source, x,
                             error=f"output size {n_out} for input size {n_in}")
                return

    size_exponent = _fit_exponent(size_points)
    verdict.scaling = {
        "size_exponent": None if size_exponent is None else round(size_exponent, 3),
        "time_exponent": (lambda e: None if e is None else round(e, 3))(_fit_exponent(time_points)),
        "max_input_size": max((p[0] for p in size_points), default=0),
        "max_output_size": max((p[1] for p in size_points), default=0),
    }
    if size_exponent is not None and size_exponent > settings.max_size_exponent:
        worst = max(size_points, key=lambda p: p[1])
        verdict.fail("blowup", "scaling", source, None,
                     error=f"output size grows like input^{size_exponent:.2f} "
                           f"(largest: {worst[1]} for input size {worst[0]})")


# --- Runs, tasks and the CLI -------------------------------------------------------


def problem_by_name(name: str) -> type[Problem]:
    for problem in PROBLEMS.values():
        if problem.name == name:
            return problem
    raise ValueError(f"no problem named {name!r} in the library")


def task_problems(task_dir: Path) -> tuple[type[Problem], type[Problem], Path]:
    descriptor = json.loads((task_dir / "task.json").read_text())
    return (
        problem_by_name(descriptor["source_problem"]),
        problem_by_name(descriptor["target_problem"]),
        task_dir / "inputs" / "problems.py",
    )


def verify_run(run_dir: Path, tasks_dir: Path, settings: Settings = Settings()) -> dict[str, Any]:
    record = json.loads((run_dir / "result.json").read_text())
    source, target, problems_file = task_problems(tasks_dir / record["task_id"])
    verdict = verify_reduction(
        run_dir / "reduce.py", problems_file, source, target, settings, seed=record["task_id"]
    )
    return {"run_id": record["run_id"], "task_id": record["task_id"], **verdict.to_json()}


def _write_atomically(path: Path, data: dict[str, Any]) -> None:
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n")
    temporary.replace(path)


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument("--runs", type=Path, default=REPO / "runs")
    parser.add_argument("--tasks", type=Path, default=REPO / "tasks")
    parser.add_argument("--out", type=Path, default=REPO / "verdicts.json")
    parser.add_argument("--run", nargs="+", help="verify only these run IDs")
    parser.add_argument("--force", action="store_true", help="re-verify runs already in --out")
    parser.add_argument("--jobs", type=int, default=os.cpu_count() or 4)
    parser.add_argument("--reduce", type=Path, help="verify one reduce.py (with --task)")
    parser.add_argument("--task", help="task ID for --reduce")
    arguments = parser.parse_args(argv)

    if arguments.reduce:
        if not arguments.task:
            parser.error("--reduce needs --task")
        source, target, problems_file = task_problems(arguments.tasks / arguments.task)
        verdict = verify_reduction(arguments.reduce, problems_file, source, target, seed=arguments.task)
        print(json.dumps(verdict.to_json(), indent=2))
        return

    verdicts = json.loads(arguments.out.read_text()) if arguments.out.exists() else {}
    run_dirs = sorted(p.parent for p in arguments.runs.glob("*/result.json"))
    if arguments.run:
        wanted = set(arguments.run)
        run_dirs = [d for d in run_dirs if d.name in wanted]
    pending = [
        d for d in run_dirs
        if arguments.force
        or verdicts.get(d.name, {}).get("verifier_version") != VERIFIER_VERSION
    ]
    print(f"{len(run_dirs)} run(s), {len(run_dirs) - len(pending)} already verified, "
          f"{len(pending)} to verify with {arguments.jobs} job(s)")

    from tqdm import tqdm

    with ProcessPoolExecutor(max_workers=arguments.jobs) as pool:
        futures = {pool.submit(verify_run, d, arguments.tasks): d for d in pending}
        for future in tqdm(as_completed(futures), total=len(futures), unit="run"):
            run_dir = futures[future]
            try:
                result = future.result()
            except Exception as error:  # a verifier bug, not an agent failure
                tqdm.write(f"ERROR verifying {run_dir.name}: {error}")
                continue
            verdicts[result["run_id"]] = result
            _write_atomically(arguments.out, verdicts)

    counts: dict[str, int] = {}
    for verdict in verdicts.values():
        counts[verdict["status"]] = counts.get(verdict["status"], 0) + 1
    print("verdicts: " + ", ".join(f"{n} {status}" for status, n in sorted(counts.items())))


if __name__ == "__main__":
    main()