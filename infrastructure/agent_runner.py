"""
Run one reduction task through the pinned mini-SWE-agent scaffold on Modal.

Each call gets a fresh container and a temporary workspace holding the task's
input files. The agent works with one bash tool. When it finishes, the runner
collects reduce.py (the reduction), verdict.json (the agent's own claim about
whether its tests pass) and test_reduce.py (its tests), plus token usage.
"""

from __future__ import annotations

import json
import os
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
MODEL_MAX_TOKENS = 4096
MAX_CONTAINERS = 16 

# Single-shot conditions get a few steps to write the file and submit.
STEP_LIMITS = {"c1": 3, "c2": 3, "c3": 20}
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
        "Write reduce.py in a single command, without running or testing any "
        "code, then submit."
    ),
    # c2: best-of-k. Each sample is an independent c1-style run.
    "c2": (
        "Write reduce.py in a single command, without running or testing any "
        "code, then submit."
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
    # c4 (oracle counterexamples) and c5 (independent tester) will be added in
    # Week 2, once the hidden verifier exists.
}

app = modal.App(APP_NAME)
image = (
    modal.Image.debian_slim(python_version="3.12")
    .apt_install("git")
    .uv_pip_install(f"mini-swe-agent=={MINI_SWE_AGENT_VERSION}", "numpy==2.3.2")
)


def task_prompt(task: dict[str, Any], condition: str) -> str:
    if condition not in CONDITION_INSTRUCTIONS:
        raise NotImplementedError(
            f"condition {condition!r} is not implemented yet "
            f"(available: {', '.join(CONDITION_INSTRUCTIONS)})"
        )
    expected = task["expected_output"]
    inputs = [item["name"] for item in task.get("inputs", [])]
    return (
        f"TASK ID: {task['task_id']}\n\n"
        f"USER REQUEST:\n{task['instructions']}\n\n"
        f"INPUT FILES: {json.dumps(inputs)}\n\n"
        f"{OUTPUT_SPEC}\n\n"
        f"{CONDITION_INSTRUCTIONS[condition]}\n"
        "Do not merely describe code: leave the files at those exact paths."
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

@app.function(image=image, timeout=20 * 60, max_containers=MAX_CONTAINERS)
def run_task(request: dict[str, Any]) -> dict[str, Any]:
    from litellm import ModelResponse
    from minisweagent.agents.default import DefaultAgent
    from minisweagent.config import get_config_from_spec
    from minisweagent.environments.local import LocalEnvironment, _run
    from minisweagent.models.litellm_model import LitellmModel
    from minisweagent.models.utils.actions_toolcall import BASH_TOOL

    task = request["task"]
    condition = request["condition"]
    prompt = task_prompt(task, condition)
    step_limit = STEP_LIMITS[condition]
    temperature = request["temperature"]
    usage_log: list[dict[str, Any] | None] = []
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
                        "max_tokens": MODEL_MAX_TOKENS,
                    },
                }
            )
            usage_log.append(raw.get("usage"))
            return ModelResponse(**raw)

        def _calculate_cost(self, response):
            return {"cost": 0.0}

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
            "step_limit": step_limit,
            "scaffold": f"mini-swe-agent=={MINI_SWE_AGENT_VERSION}",
            "prompt": prompt,
            "outcome": outcome,
            "trajectory": agent.serialize(),
            "files": files,
            "agent_verified": _agent_verified(files["verdict.json"]),
            "usage": usage_log,
            "elapsed_seconds": time.monotonic() - started,
        }
