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
STEP_LIMITS = {"c1": 6, "c2": 6, "c3": 20, "c3n": 20}
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
    # c4 (oracle counterexamples) and c5 (independent tester) come next.
}

app = modal.App(APP_NAME)
image = (
    modal.Image.debian_slim(python_version="3.12")
    .apt_install("git")
    .uv_pip_install(f"mini-swe-agent=={MINI_SWE_AGENT_VERSION}", "numpy==2.3.2")
)


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


# 30 minutes: the agent's 15-minute wall limit is only checked between steps,
# so one long model call can carry a run past it.
@app.function(image=image, timeout=30 * 60, max_containers=MAX_CONTAINERS)
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
                    "generation": {
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

    with tempfile.TemporaryDirectory(prefix="reduction-") as raw_workspace:
        workspace = Path(raw_workspace)
        prompt = task_prompt(task, condition, str(workspace))
        for name, content in request.get("input_files", {}).items():
            target = _within_workspace(workspace, name)
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(content)

        os.environ["PYTHONUNBUFFERED"] = "1"
        baseline = get_config_from_spec("mini")
        model = GatewayModel(
            model_name=request["model"],
            model_kwargs={},
            cost_tracking="ignore_errors",
            observation_template=baseline["model"]["observation_template"],
            format_error_template=baseline["model"]["format_error_template"],
        )
        # Do not retry a call that ended the run (mini-swe-agent retries others).
        model.abort_exceptions = [*model.abort_exceptions, LimitsExceeded]
        environment = CredentialScrubbedEnvironment(
            cwd=str(workspace),
            timeout=COMMAND_TIMEOUT_SECONDS,
            env=baseline["environment"]["env"] | {"PYTHONUNBUFFERED": "1"},
        )
        agent = DefaultAgent(
            model,
            environment,
            system_template=baseline["agent"]["system_template"],
            instance_template=baseline["agent"]["instance_template"],
            step_limit=step_limit,
            cost_limit=0,
            wall_time_limit_seconds=WALL_TIME_LIMIT_SECONDS,
        )
        outcome = agent.run(prompt)

        files = {name: _read_text(workspace / name) for name in COLLECTED_FILES}
        return {
            "run_id": request["run_id"],
            "task_id": task["task_id"],
            "model": request["model"],
            "condition": condition,
            "temperature": temperature,
            "max_tokens": max_tokens,
            "step_limit": step_limit,
            "scaffold": f"mini-swe-agent=={MINI_SWE_AGENT_VERSION}",
            "prompt": prompt,
            "outcome": outcome,
            "exit_status": (outcome or {}).get("exit_status"),
            "trajectory": agent.serialize(),
            "files": files,
            "agent_verified": _agent_verified(files["verdict.json"]),
            "usage": usage_log,
            "replies_without_tool_calls": replies_without_tool_calls,
            "elapsed_seconds": time.monotonic() - started,
        }