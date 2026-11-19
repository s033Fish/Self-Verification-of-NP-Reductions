"""Run one reduction task through the pinned mini-SWE-agent scaffold on Modal.

Each call gets a fresh container and a temporary workspace holding the task's
input files. The agent works with one bash tool. When it finishes, the runner
collects reduce.py (the reduction), verdict.json (the agent's own claim about
whether its tests pass) and test_reduce.py (its tests), plus token usage.

Adapted from the Assignment 2 `agent_runner.py`: same scaffold, sandbox and
limits; new prompts, collected files, sampling temperature and usage logging.
"""

from __future__ import annotations

import json
import os
import re
import tempfile
import time
from pathlib import Path
from typing import Any

import modal

MINI_SWE_AGENT_VERSION = "2.4.5"
APP_NAME = "reductions-agent-runner"
FUNCTION_NAME = "run_task"
GATEWAY_APP = "reductions-gateway"
GATEWAY_FUNCTION = "complete"

COMMAND_TIMEOUT_SECONDS = 120
WALL_TIME_LIMIT_SECONDS = 15 * 60
MODEL_MAX_TOKENS = 4096  # default; each agent sets its own (workflow/agents.py)
MAX_CONTAINERS = 16  # matches the GLM server's concurrent request slots

# Single-shot conditions may read files but not run code; 6 steps leaves room
# to read problems.py, write reduce.py and submit. (3 was too few: most runs
# ended before reduce.py was written.)
STEP_LIMITS = {"c1": 6, "c2": 6, "c3": 20, "c3n": 20, "c4": 20, "c5": 20, "c5x": 20}

# c5: the writer works exactly as in c3n (its own tests and verdict.json, kept
# as writer_*). Then a fresh tester agent (same model, new workspace, none of
# the writer's messages, tests or verdict) checks the finished reduce.py from
# the definitions alone and issues the graded verdict.json. So c5 and c3n grade
# the same kind of reduction, and only who issues the verdict differs.
TESTER_CONDITIONS = {"c5", "c5x"}
# c5x: the cross-model tester. The request carries the "writer" files of an
# existing c5 run (no new writer is run) and a "tester" model: the other agent.
TESTER_STEP_LIMIT = 20
WRITER_FILE_PREFIX = "writer_"

# c4: on submit, the hidden verifier (with its own seed) checks reduce.py. If it
# finds a problem, the agent gets the smallest counterexample instead of ending
# the run, up to this many times; the next submit is then accepted unchecked
# and graded as usual. Each feedback round also clears verdict.json (kept in the
# oracle log) and adds steps, so a final "verified" claim is always one the
# agent made after seeing the counterexample. (In the first c4 pilot, every
# false positive was a stale verdict.json the agent never revisited.)
ORACLE_CONDITIONS = {"c4"}
MAX_ORACLE_ROUNDS = 3
ORACLE_EXTRA_STEPS = 5  # per feedback round: revise, re-test, re-verdict, submit
ORACLE_TIMEOUT_SECONDS = 8 * 60
MAX_FEEDBACK_INSTANCE_CHARS = 1500
COLLECTED_FILES = ("reduce.py", "verdict.json", "test_reduce.py")
MAX_COLLECTED_BYTES = 200_000

OUTPUT_SPEC = (
    "REQUIRED OUTPUT: create reduce.py in the workspace, defining\n"
    "    reduce(instance) -> instance\n"
    "It takes an instance of the source problem and returns an instance of the "
    "target problem, both in the formats documented in problems.py. The answer "
    "to the returned instance must be yes exactly when the answer to the input "
    "instance is yes, and reduce must run in polynomial time. Do not call the "
    "brute-force solvers inside reduce."
)

CONDITION_INSTRUCTIONS = {
    # c1: single shot, no execution.
    "c1": (
        "You may read files such as problems.py, but do not run, execute or "
        "test any code. Write reduce.py, then submit."
    ),
    # c2: best-of-k. Each sample is an independent c1-style run.
    "c2": (
        "You may read files such as problems.py, but do not run, execute or "
        "test any code. Write reduce.py, then submit."
    ),
    # c3: self-verification. The agent writes and runs its own tests.
    "c3": (
        "Before submitting, check your reduction. Write tests in test_reduce.py "
        "that compare the brute-force solvers in problems.py on many small "
        "source instances and their reductions, run them, and revise reduce.py "
        "until the tests pass. Finally write verdict.json as "
        '{"verified": true or false, "tests_run": <int>, "tests_passed": <int>}, '
        "where verified is true only if all of your tests pass. Then submit."
    ),
    # c3n: self-verification WITHOUT reference solvers. problems.py has only
    # the specs and validate(), so any solver the agent tests with is its own.
    "c3n": (
        "Before submitting, check your reduction. problems.py has no solvers, "
        "so first write your own brute-force solvers for both problems from the "
        "definitions above. Then write tests in test_reduce.py that compare your "
        "solvers' answers on many small source instances and their reductions, "
        "run them, and revise until the tests pass. Finally write verdict.json as "
        '{"verified": true or false, "tests_run": <int>, "tests_passed": <int>}, '
        "where verified is true only if all of your tests pass. Then submit."
    ),
    # c4: c3n plus oracle counterexamples on submit (no reference solvers).
    "c4": (
        "Before submitting, check your reduction. problems.py has no solvers, "
        "so first write your own brute-force solvers for both problems from the "
        "definitions above. Then write tests in test_reduce.py that compare your "
        "solvers' answers on many small source instances and their reductions, "
        "run them, and revise until the tests pass. Finally write verdict.json as "
        '{"verified": true or false, "tests_run": <int>, "tests_passed": <int>}, '
        "where verified is true only if all of your tests pass. Then submit.\n"
        "When you submit, an oracle checks reduce.py. If it finds a problem, it "
        f"replies with a counterexample instead of ending the task (at most "
        f"{MAX_ORACLE_ROUNDS} times): fix reduce.py and "
        "submit again. Each time, verdict.json is cleared: write it again "
        "after re-testing."
    ),
}
# c5's writer gets c3n's instruction word for word.
CONDITION_INSTRUCTIONS["c5"] = CONDITION_INSTRUCTIONS["c3n"]
CONDITION_INSTRUCTIONS["c5x"] = CONDITION_INSTRUCTIONS["c3n"]  # only its tester runs

TESTER_INSTRUCTION = (
    "Someone else wrote reduce.py, claiming it is a correct reduction from SOURCE "
    "to TARGET. Your job is to check it independently; do not change reduce.py. "
    "problems.py has no solvers, so first write your own brute-force solvers for "
    "both problems from the definitions above. Then write tests in test_reduce.py "
    "that compare your solvers' answers on many small source instances and their "
    "reductions, and run them. Finally write verdict.json as "
    '{"verified": true or false, "tests_run": <int>, "tests_passed": <int>}, '
    "where verified is true only if reduce.py meets every requirement above "
    "according to your checks. Then submit."
)

app = modal.App(APP_NAME)
image = (
    modal.Image.debian_slim(python_version="3.12")
    .apt_install("git")
    .uv_pip_install(f"mini-swe-agent=={MINI_SWE_AGENT_VERSION}", "numpy==2.3.2")
)
# The oracle runs in its own container: the agent's container never holds the
# problem library's solvers or the SAT solver, so the agent cannot import them.
oracle_image = (
    modal.Image.debian_slim(python_version="3.12")
    .uv_pip_install("python-sat==1.9.dev22")
    .add_local_python_source("benchmark")
)


def _short_json(value: Any, limit: int = MAX_FEEDBACK_INSTANCE_CHARS) -> str:
    text = json.dumps(value, separators=(",", ":"))
    return text if len(text) <= limit else text[:limit] + " ...(truncated)"


def _answer(value: bool | None) -> str:
    return {True: "yes", False: "no"}.get(value, "unknown")


def oracle_feedback(verdict: dict[str, Any], round_number: int) -> str | None:
    """What the agent sees after a submit in c4, or None to accept the submit.

    Only a "wrong" verdict produces feedback: correct and inconclusive verdicts
    (and oracle errors) let the submit through, to be graded as usual.
    """
    if verdict.get("status") != "wrong":
        return None
    example = verdict.get("counterexample") or {}
    category = verdict.get("category") or example.get("category") or "unknown"
    x = example.get("source_instance")
    error = example.get("error")
    header = (
        f"ORACLE FEEDBACK (round {round_number} of {MAX_ORACLE_ROUNDS}): "
        "reduce.py is not correct, so the task was NOT submitted.\n"
    )
    if category.startswith("wrong_answer"):
        body = (
            f"Source instance: {_short_json(x)}\n"
            f"Its answer is {_answer(example.get('expected'))}, but reduce returned "
            f"{_short_json(example.get('target_instance'))}, whose answer is "
            f"{_answer(example.get('got'))}."
        )
    elif category == "no_reduce_file":
        body = "reduce.py was not found in the working directory."
    elif category in {"blowup", "constant_output", "superpolynomial_time"}:
        what = {
            "blowup": "The output grows too fast with the input: not polynomial.",
            "superpolynomial_time": (
                "reduce's running time grows faster than any polynomial as the "
                "input grows: it is not a polynomial-time reduction."
            ),
            "constant_output": (
                "Many different large inputs all map to one or two fixed output "
                "instances: reduce decides the answer itself instead of "
                "transforming the instance, which no polynomial-time reduction can do."
            ),
        }[category]
        body = what + (f"\nDetail: {error}" if error else "")
        if x is not None:
            body += f"\nInput: {_short_json(x)}"
    else:
        what = {
            "crash": "reduce raised an error",
            "timeout": "reduce took too long (it must run in polynomial time)",
            "malformed_output": "reduce returned an invalid target instance",
            "solver_call": "reduce called a brute-force solver, which is not allowed",
        }.get(category, f"reduce failed ({category})")
        body = f"On source instance {_short_json(x)}, {what}."
        if error:
            body += f"\nDetail: {str(error)[:800]}"
    return header + body + (
        "\nverdict.json has been cleared and you have "
        f"{ORACLE_EXTRA_STEPS} extra steps. Fix reduce.py, re-run your tests, "
        "write verdict.json again, and submit."
    )


@app.function(image=oracle_image, timeout=ORACLE_TIMEOUT_SECONDS + 60)
def oracle_check(request: dict[str, Any]) -> dict[str, Any]:
    """Run the hidden verifier on one reduce.py (c4)."""
    return run_oracle_process(request, package_root="/root")


def run_oracle_process(request: dict[str, Any], package_root: str) -> dict[str, Any]:
    """The verifier sets signal alarms, which need a main thread, so it runs as
    a child process. package_root is the directory that contains benchmark/."""
    import subprocess
    import sys

    with tempfile.TemporaryDirectory(prefix="oracle-") as raw:
        workdir = Path(raw)
        (workdir / "reduce.py").write_text(request["reduce_py"])
        (workdir / "problems.py").write_bytes(request["problems_py"])
        (workdir / "request.json").write_text(json.dumps({
            "reduce_file": str(workdir / "reduce.py"),
            "problems_file": str(workdir / "problems.py"),
            "source": request["source"],
            "target": request["target"],
            "seed": request["seed"],
        }))
        process = subprocess.run(
            [sys.executable, "-m", "benchmark.verify", "--oracle-request",
             str(workdir / "request.json")],
            capture_output=True, text=True, cwd=package_root, timeout=ORACLE_TIMEOUT_SECONDS,
        )
        lines = process.stdout.strip().splitlines()
        if process.returncode != 0 or not lines:
            return {"status": "oracle_error", "error": process.stderr[-2000:]}
        return json.loads(lines[-1])


SUBMIT_COMMAND = "echo COMPLETE_TASK_AND_SUBMIT_FINAL_OUTPUT"


def recover_tool_call(message: dict[str, Any]) -> str | None:
    """The bash command a reply clearly meant to run but wrote as text.

    GPT-OSS on Fireworks sometimes puts the tool call in the reply text instead
    of a real tool call, almost always for the final submit. Only two exact
    shapes count: a JSON object whose only key is "command", or the bare submit
    command. Anything else (prose, code blocks) stays a format error.
    """
    if message.get("tool_calls"):
        return None
    text = (message.get("content") or "").strip()
    if text == SUBMIT_COMMAND:
        return text
    try:
        parsed = json.loads(text)
    except ValueError:
        return None
    if isinstance(parsed, dict) and set(parsed) == {"command"} and isinstance(parsed["command"], str):
        return parsed["command"]
    return None


# Every reply must contain a bash tool call; a plain-text "I'm done" reply is a
# format error, and three in a row end the run. Say exactly how to finish.
FINISH_INSTRUCTION = (
    "Every reply must contain exactly one bash tool call. When you are done, "
    f"finish by running exactly: {SUBMIT_COMMAND}"
)

NO_CODE_CONDITIONS = {"c1", "c2"}
_HEREDOC = re.compile(r"<<-?\s*['\"]?(\w+)['\"]?[^\n]*\n.*?\n\s*\1\b", re.DOTALL)
_RUNS_CODE = re.compile(r"(?:^|[;&|(`]|\n)\s*(?:sudo\s+)?(?:python\d*(?:\.\d+)?|pytest|pip\d*)\b")


def runs_code(command: str) -> bool:
    """Whether a shell command starts a Python interpreter, pytest or pip.
    Here-document bodies (file contents being written) are ignored, so a
    reduce.py that mentions "python" can still be written."""
    return bool(_RUNS_CODE.search(_HEREDOC.sub("<<heredoc", command)))


def task_prompt(task: dict[str, Any], condition: str, workspace: str = ".") -> str:
    if condition not in CONDITION_INSTRUCTIONS:
        raise NotImplementedError(
            f"condition {condition!r} is not implemented yet "
            f"(available: {', '.join(CONDITION_INSTRUCTIONS)})"
        )
    inputs = [item["name"] for item in task.get("inputs", [])]
    spec = task.get("spec")
    definitions = (
        "PROBLEM DEFINITIONS (the SOURCE and TARGET docstrings from problems.py, "
        "complete as given here):\n\n"
        f"{spec}\n\n"
        if spec else ""
    )
    if task.get("solvers_provided", True):
        contents = (
            "problems.py is long (about 500 lines): you do not need to read it to "
            "know the formats, which are given above. It provides SOURCE and TARGET "
            "with is_yes(instance), validate(instance) and random_instance(rng, "
            "scale); search it (e.g. with grep) only if you need something specific."
        )
    else:
        contents = (
            "problems.py provides SOURCE and TARGET with validate(instance) only. "
            "It has NO solvers and NO instance generators."
        )
    files = (
        f"WORKING DIRECTORY: {workspace}\n"
        "All input files are in this directory; run every command from it and "
        f"write your files here. {contents}\n\n"
    )
    return (
        f"TASK ID: {task['task_id']}\n\n"
        f"USER REQUEST:\n{task['instructions']}\n\n"
        f"{definitions}"
        f"INPUT FILES: {json.dumps(inputs)}\n"
        f"{files}"
        f"{OUTPUT_SPEC}\n\n"
        f"{CONDITION_INSTRUCTIONS[condition]}\n"
        "Do not merely describe code: leave the files at those exact paths.\n"
        f"{FINISH_INSTRUCTION}"
    )


def review_prompt(task: dict[str, Any], workspace: str = ".") -> str:
    """c5's tester: the definitions, the requirements and the finished
    reduce.py; nothing from the writer's run."""
    spec = task.get("spec")
    definitions = (
        "PROBLEM DEFINITIONS (the SOURCE and TARGET docstrings from problems.py, "
        "complete as given here):\n\n"
        f"{spec}\n\n"
        if spec else ""
    )
    return (
        f"TASK ID: {task['task_id']} (review)\n\n"
        f"{definitions}"
        'INPUT FILES: ["problems.py", "reduce.py"]\n'
        f"WORKING DIRECTORY: {workspace}\n"
        "All input files are in this directory; run every command from it and "
        "write your files here. problems.py provides SOURCE and TARGET with "
        "validate(instance) only. It has NO solvers and NO instance generators.\n\n"
        "REQUIREMENTS for reduce.py: it defines reduce(instance) -> instance, "
        "taking an instance of the source problem and returning an instance of "
        "the target problem, both in the formats documented above. The answer to "
        "the returned instance must be yes exactly when the answer to the input "
        "instance is yes, and reduce must run in polynomial time without calling "
        "brute-force solvers.\n\n"
        f"{TESTER_INSTRUCTION}\n"
        "Do not merely describe code: leave the files at those exact paths.\n"
        f"{FINISH_INSTRUCTION}"
    )


def _within_workspace(workspace: Path, relative: str) -> Path:
    candidate = (workspace / relative).resolve()
    if Path(relative).is_absolute() or not candidate.is_relative_to(
        workspace.resolve()
    ):
        raise ValueError(f"unsafe task path: {relative!r}")
    return candidate


def _read_text(path: Path) -> str | None:
    if not path.is_file():
        return None
    return path.read_bytes()[:MAX_COLLECTED_BYTES].decode("utf-8", errors="replace")


def _agent_verified(verdict_text: str | None) -> bool | None:
    """The agent's own claim: True, False, or None when absent or malformed."""
    if verdict_text is None:
        return None
    try:
        verified = json.loads(verdict_text).get("verified")
    except (json.JSONDecodeError, AttributeError):
        return None
    return verified if isinstance(verified, bool) else None


# 45 minutes: the agent's 15-minute wall limit is only checked between steps,
# so one long model call can carry a run past it, and c5 runs two agents.
@app.function(image=image, timeout=45 * 60, max_containers=MAX_CONTAINERS)
def run_task(request: dict[str, Any]) -> dict[str, Any]:
    """Run one task. Never raises: an unexpected failure comes back as
    {"run_id": ..., "error": ...} so the caller always knows which run failed."""
    import traceback

    try:
        return _run_task(request)
    except Exception as error:
        return {
            "run_id": request.get("run_id"),
            "error": f"{type(error).__name__}: {error}"[:2000],
            "traceback": traceback.format_exc()[-4000:],
        }


def _run_task(request: dict[str, Any]) -> dict[str, Any]:
    from litellm import ModelResponse
    from minisweagent.agents.default import DefaultAgent
    from minisweagent.config import get_config_from_spec
    from minisweagent.environments.local import LocalEnvironment, _run
    from minisweagent.exceptions import LimitsExceeded
    from minisweagent.models.litellm_model import LitellmModel
    from minisweagent.models.utils.actions_toolcall import BASH_TOOL

    task = request["task"]
    condition = request["condition"]
    task_prompt(task, condition)  # fail fast on an unknown condition
    max_tokens = request.get("max_tokens", MODEL_MAX_TOKENS)
    step_limit = STEP_LIMITS[condition]
    temperature = request["temperature"]
    usage_log: list[dict[str, Any] | None] = []
    oracle_log: list[dict[str, Any]] = []
    # mini-swe-agent drops a reply without a tool call before it reaches the
    # trajectory (it raises FormatError first), so keep those replies here.
    replies_without_tool_calls: list[dict[str, Any]] = []

    def _record_if_no_tool_call(raw: dict[str, Any], call_index: int) -> None:
        choice = (raw.get("choices") or [{}])[0]
        message = choice.get("message") or {}
        if message.get("tool_calls"):
            return
        replies_without_tool_calls.append({
            "call": call_index,
            "finish_reason": choice.get("finish_reason"),
            "content": message.get("content"),
            "reasoning_content": message.get("reasoning_content"),
            "message_keys": sorted(message),
        })
    started = time.monotonic()

    class GatewayModel(LitellmModel):
        def _query(self, messages: list[dict[str, Any]], **kwargs: Any):
            gateway = modal.Function.from_name(GATEWAY_APP, GATEWAY_FUNCTION)
            raw = gateway.remote(
                {
                    "model": self.config.model_name,
                    "messages": messages,
                    "tools": [BASH_TOOL],
                    "generation": getattr(self, "generation", None) or {
                        "temperature": temperature,
                        "max_tokens": max_tokens,
                    },
                }
            )
            if "gateway_error" in raw:
                error = raw["gateway_error"]
                if error.get("kind") == "context_exceeded":
                    # The conversation no longer fits the model: end the run the
                    # way the step and time limits do, keeping its files.
                    raise LimitsExceeded({
                        "role": "exit",
                        "content": "ContextExceeded",
                        "extra": {"exit_status": "ContextExceeded", "submission": ""},
                    })
                raise RuntimeError(f"gateway error: {error}")
            usage_log.append(raw.get("usage"))
            _record_if_no_tool_call(raw, len(usage_log) - 1)
            message = ((raw.get("choices") or [{}])[0]).get("message") or {}
            command = recover_tool_call(message)
            if command is not None:
                message["tool_calls"] = [{
                    "id": f"recovered_{len(usage_log) - 1}",
                    "type": "function",
                    "function": {"name": "bash", "arguments": json.dumps({"command": command})},
                }]
                replies_without_tool_calls[-1]["recovered_command"] = command
            return ModelResponse(**raw)

        def _calculate_cost(self, response):
            return {"cost": 0.0}  # cost is computed offline from usage_log

    class CredentialScrubbedEnvironment(LocalEnvironment):
        """Keep infrastructure credentials out of model-written processes."""

        def execute(
            self,
            action: dict[str, Any],
            cwd: str = "",
            *,
            timeout: int | None = None,
        ):
            command = action.get("command", "")
            if condition in NO_CODE_CONDITIONS and runs_code(command):
                output = {
                    "output": (
                        "Not allowed: this task does not permit running, executing "
                        "or testing code. Write reduce.py, then submit."
                    ),
                    "returncode": 1,
                    "exception_info": "",
                }
                self._check_finished(output)
                return output
            cwd = cwd or self.config.cwd or os.getcwd()
            child_env = {
                key: value
                for key, value in (os.environ | self.config.env).items()
                if not any(marker in key for marker in ("TOKEN", "SECRET", "API_KEY"))
            }
            try:
                result = _run(command, cwd, child_env, timeout or self.config.timeout)
                output = {
                    "output": result.stdout,
                    "returncode": result.returncode,
                    "exception_info": "",
                }
            except Exception as error:
                raw_output = getattr(error, "output", None)
                if isinstance(raw_output, bytes):
                    raw_output = raw_output.decode("utf-8", errors="replace")
                output = {
                    "output": raw_output or "",
                    "returncode": -1,
                    "exception_info": (
                        f"An error occurred while executing the command: {error}"
                    ),
                    "extra": {
                        "exception_type": type(error).__name__,
                        "exception": str(error),
                    },
                }
            self._check_finished(output)
            return output

        def _check_finished(self, output: dict[str, Any]) -> None:
            if condition in ORACLE_CONDITIONS and _is_submit(output) and (
                sum(1 for entry in oracle_log if entry.get("feedback")) < MAX_ORACLE_ROUNDS
            ):
                feedback = _consult_oracle()
                if feedback is not None:
                    output["output"] = feedback  # not submitted: the agent continues
                    output["returncode"] = 1
                    return
            super()._check_finished(output)

    def _is_submit(output: dict[str, Any]) -> bool:
        lines = output.get("output", "").lstrip().splitlines()
        return bool(lines) and lines[0].strip() == "COMPLETE_TASK_AND_SUBMIT_FINAL_OUTPUT" \
            and output.get("returncode") == 0

    def _consult_oracle() -> str | None:
        reduce_file = workspace / "reduce.py"
        round_number = sum(1 for entry in oracle_log if entry.get("feedback")) + 1
        entry: dict[str, Any] = {"step": len(usage_log), "round": round_number}
        oracle_started = time.monotonic()
        try:
            if not reduce_file.is_file():
                verdict: dict[str, Any] = {"status": "wrong", "category": "no_reduce_file"}
            else:
                verdict = modal.Function.from_name(APP_NAME, "oracle_check").remote({
                    "reduce_py": reduce_file.read_text(errors="replace"),
                    "problems_py": pristine_problems,
                    "source": task["source_problem"],
                    "target": task["target_problem"],
                    "seed": f"{task['task_id']}:oracle",
                })
        except Exception as error:  # an infrastructure failure: accept the submit
            verdict = {"status": "oracle_error", "error": f"{type(error).__name__}: {error}"[:2000]}
        feedback = oracle_feedback(verdict, round_number)
        if feedback is not None:
            verdict_file = workspace / "verdict.json"
            entry["verdict_before"] = _read_text(verdict_file)
            verdict_file.unlink(missing_ok=True)
            agent.config.step_limit += ORACLE_EXTRA_STEPS
        entry |= {
            "status": verdict.get("status"),
            "category": verdict.get("category"),
            "error": verdict.get("error"),
            "seconds": round(time.monotonic() - oracle_started, 1),
            "feedback": feedback,
        }
        oracle_log.append(entry)
        return feedback

    with tempfile.TemporaryDirectory(prefix="reduction-") as raw_workspace:
        workspace = Path(raw_workspace)
        prompt = task_prompt(task, condition, str(workspace))
        for name, content in request.get("input_files", {}).items():
            target = _within_workspace(workspace, name)
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(content)
        # The oracle verifies against the problems.py the run started with, not
        # whatever the agent may have edited.
        pristine_problems = request.get("input_files", {}).get("problems.py", b"")

        os.environ["PYTHONUNBUFFERED"] = "1"
        baseline = get_config_from_spec("mini")

        def make_agent(cwd: Path, limit: int, settings: dict[str, Any] | None = None) -> DefaultAgent:
            """settings: another model's {"model", "temperature", "max_tokens"}
            (the c5x tester); by default the run's own model."""
            model = GatewayModel(
                model_name=(settings or {}).get("model") or request["model"],
                model_kwargs={},
                cost_tracking="ignore_errors",
                observation_template=baseline["model"]["observation_template"],
                format_error_template=baseline["model"]["format_error_template"],
            )
            if settings:
                model.generation = {
                    "temperature": settings["temperature"],
                    "max_tokens": settings["max_tokens"],
                }
            # Do not retry a call that ended the run (mini-swe-agent retries others).
            model.abort_exceptions = [*model.abort_exceptions, LimitsExceeded]
            environment = CredentialScrubbedEnvironment(
                cwd=str(cwd),
                timeout=COMMAND_TIMEOUT_SECONDS,
                env=baseline["environment"]["env"] | {"PYTHONUNBUFFERED": "1"},
            )
            return DefaultAgent(
                model,
                environment,
                system_template=baseline["agent"]["system_template"],
                instance_template=baseline["agent"]["instance_template"],
                step_limit=limit,
                cost_limit=0,
                wall_time_limit_seconds=WALL_TIME_LIMIT_SECONDS,
            )

        writer = request.get("writer")  # c5x: review an existing writer's files
        if writer is not None:
            agent = None
            outcome = {"exit_status": writer.get("exit_status")}
            files = {name: writer["files"].get(name) for name in COLLECTED_FILES}
        else:
            agent = make_agent(workspace, step_limit)
            outcome = agent.run(prompt)
            files = {name: _read_text(workspace / name) for name in COLLECTED_FILES}
        tester: dict[str, Any] = {}
        if condition in TESTER_CONDITIONS:
            writer_files = files
            # The graded files: the writer's reduce.py, the tester's verdict and tests.
            files = {
                "reduce.py": writer_files["reduce.py"],
                "verdict.json": None,
                "test_reduce.py": None,
                **{f"{WRITER_FILE_PREFIX}{name}": text
                   for name, text in writer_files.items() if name != "reduce.py"},
            }
            tester = {"writer_verified": _agent_verified(writer_files["verdict.json"]),
                      "tester_first_call": len(usage_log)}
            if writer_files["reduce.py"] is None:
                tester["tester_exit_status"] = "NoReduction"  # nothing to review
            else:
                with tempfile.TemporaryDirectory(prefix="review-") as raw_review:
                    review = Path(raw_review)
                    (review / "problems.py").write_bytes(pristine_problems)
                    (review / "reduce.py").write_text(writer_files["reduce.py"])
                    review_text = review_prompt(task, str(review))
                    tester_settings = request.get("tester")
                    tester_agent = make_agent(review, TESTER_STEP_LIMIT, tester_settings)
                    tester_outcome = tester_agent.run(review_text)
                    files["verdict.json"] = _read_text(review / "verdict.json")
                    files["test_reduce.py"] = _read_text(review / "test_reduce.py")
                    tester |= {
                        "tester_prompt": review_text,
                        "tester_exit_status": (tester_outcome or {}).get("exit_status"),
                        "tester_trajectory": tester_agent.serialize(),
                        "tester_model": (tester_settings or {}).get("model") or request["model"],
                    }
            if writer is not None:
                tester["writer_run"] = writer.get("run_id")
        return {
            "run_id": request["run_id"],
            "task_id": task["task_id"],
            "model": request["model"],
            "condition": condition,
            "temperature": temperature,
            "max_tokens": max_tokens,
            # c4 adds steps per feedback round; c5x runs no writer of its own.
            "step_limit": agent.config.step_limit if agent else None,
            "scaffold": f"mini-swe-agent=={MINI_SWE_AGENT_VERSION}",
            "prompt": prompt if agent else None,
            "outcome": outcome,
            "exit_status": (outcome or {}).get("exit_status"),
            "trajectory": agent.serialize() if agent else None,
            "files": files,
            "agent_verified": _agent_verified(files["verdict.json"]),
            "usage": usage_log,
            "replies_without_tool_calls": replies_without_tool_calls,
            "oracle_log": oracle_log,
            **tester,
            "elapsed_seconds": time.monotonic() - started,
        }