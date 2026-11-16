"""Runs an agent's reduce.py inside the verifier's sandbox process.

The verifier starts this script with `python -I sandbox_child.py WORKDIR
MEMORY_MB`, where WORKDIR holds copies of the task's problems.py and the
agent's reduce.py. It is never imported by the benchmark package, and -I keeps
the repository off sys.path, so the reduction cannot reach the verifier or the
trusted problem library.

Before reduce.py is imported, every brute-force solver in problems.py is
replaced with a stub that raises: a reduction must transform instances, not
solve them.

Protocol: one JSON object per line. The child first sends
{"ready": true} or {"ready": false, "kind": ..., "error": ...}. Then, for each
{"instance": ...} it reads on stdin, it replies with
{"ok": true, "output": ..., "seconds": ...} or
{"ok": false, "kind": ..., "error": ...}. Anything the reduction prints is
redirected away from the protocol channel.
"""

from __future__ import annotations

import json
import os
import sys
import time

# Solver helpers in the bundled problems.py; each class's is_yes is stubbed too.
SOLVER_FUNCTIONS = (
    "_satisfiable",
    "satisfiable",
    "max_independent_set_size",
    "min_dominating_set_size",
    "three_colourable",
    "hamiltonian_path_exists",
    "hamiltonian_cycle_exists",
    "min_set_cover",
    "exact_cover_exists",
    "subset_sum_reachable",
)


class SolverCalled(BaseException):
    """BaseException, so `except Exception` in agent code does not hide it."""


solver_was_called = False


def _forbidden(*args, **kwargs):
    global solver_was_called
    solver_was_called = True
    raise SolverCalled("reduce called a brute-force solver from problems.py")


def _forbidden_method(cls, *args, **kwargs):
    _forbidden()


def stub_solvers(problems) -> None:
    for value in list(vars(problems).values()):
        if isinstance(value, type) and hasattr(value, "is_yes"):
            value.is_yes = classmethod(_forbidden_method)
    for name in SOLVER_FUNCTIONS:
        if hasattr(problems, name):
            setattr(problems, name, _forbidden)


def describe(error: BaseException) -> str:
    text = f"{type(error).__name__}: {error}"
    return text[:500]


def limit_memory(megabytes: int) -> None:
    try:
        import resource

        limit = megabytes * 1024 * 1024
        resource.setrlimit(resource.RLIMIT_AS, (limit, limit))
    except (ImportError, ValueError, OSError):
        pass  # not enforceable on every platform (e.g. macOS); the time limit still applies


def main() -> None:
    global solver_was_called
    workdir, memory_mb = sys.argv[1], int(sys.argv[2])
    limit_memory(memory_mb)

    # Keep the protocol on a private copy of stdout; send prints to stderr.
    protocol = os.fdopen(os.dup(1), "w", buffering=1)
    os.dup2(2, 1)
    sys.stdout = sys.stderr

    def send(message: dict) -> None:
        protocol.write(json.dumps(message) + "\n")
        protocol.flush()

    sys.path.insert(0, workdir)
    try:
        import problems

        stub_solvers(problems)
        import reduce as module
    except SolverCalled as error:
        send({"ready": False, "kind": "solver_call", "error": describe(error)})
        return
    except BaseException as error:
        send({"ready": False, "kind": "crash", "error": "importing reduce.py: " + describe(error)})
        return
    reduce = getattr(module, "reduce", None)
    if not callable(reduce):
        send({"ready": False, "kind": "crash", "error": "reduce.py does not define reduce(instance)"})
        return
    send({"ready": True})

    for line in sys.stdin:
        instance = json.loads(line)["instance"]
        solver_was_called = False
        start = time.perf_counter()
        try:
            output = reduce(instance)
        except SolverCalled as error:
            send({"ok": False, "kind": "solver_call", "error": describe(error)})
            continue
        except MemoryError as error:
            send({"ok": False, "kind": "blowup", "error": describe(error)})
            continue
        except BaseException as error:
            send({"ok": False, "kind": "crash", "error": describe(error)})
            continue
        seconds = time.perf_counter() - start
        if solver_was_called:  # the agent caught our exception and carried on
            send({"ok": False, "kind": "solver_call", "error": "solver called (exception was caught)"})
            continue
        try:
            text = json.dumps({"ok": True, "output": output, "seconds": seconds})
        except (TypeError, ValueError) as error:
            send({"ok": False, "kind": "malformed_output", "error": "output is not JSON data: " + describe(error)})
            continue
        protocol.write(text + "\n")
        protocol.flush()


if __name__ == "__main__":
    main()