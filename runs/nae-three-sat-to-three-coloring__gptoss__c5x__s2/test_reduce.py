"""Independent tests for reduce.py (NAE-3-SAT -> 3-Coloring).

We implement our own brute-force solvers for both problems directly from the
definitions in problems.py, then compare the source answer with the answer of
the reduced target instance on many small source instances.

We also check the *polynomial time / no brute-force solver* requirement
behaviourally: a correct polynomial reduction must return quickly on an
instance that is deliberately constructed so that naive exhaustive search over
the NAE-3-SAT assignments would take astronomically long.
"""

from __future__ import annotations

import itertools
import json
import random
import subprocess
import sys
from typing import Any, Dict, List

from problems import NaeThreeSat, ThreeColoring
from reduce import reduce

# ----------------------------------------------------------------------
# Our own brute-force solvers (independent of reduce.py)

def nae_sat_solve(instance: Dict[str, Any]) -> bool:
    """Brute-force NAE-3-SAT solver: try all 2^m assignments."""
    m = instance["num_vars"]
    clauses = instance["clauses"]
    for assignment in itertools.product([False, True], repeat=m):
        ok = True
        for clause in clauses:
            values = []
            for lit in clause:
                val = assignment[abs(lit) - 1]
                values.append(val if lit > 0 else not val)
            if all(values) or not any(values):
                ok = False
                break
        if ok:
            return True
    return False


def three_coloring_solve(instance: Dict[str, Any]) -> bool:
    """Brute-force 3-coloring solver: try all 3^n colourings."""
    n = instance["n"]
    edges = instance["edges"]
    for colouring in itertools.product(range(3), repeat=n):
        good = True
        for u, v in edges:
            if colouring[u] == colouring[v]:
                good = False
                break
        if good:
            return True
    return False


# ----------------------------------------------------------------------
# Instance generation

def all_valid_clauses(m: int) -> List[List[int]]:
    clauses = []
    for combo in itertools.combinations(range(1, m + 1), 3):
        for signs in itertools.product([1, -1], repeat=3):
            clauses.append([s * v for s, v in zip(signs, combo)])
    return clauses


def generate_instances(seed: int = 12345) -> List[Dict[str, Any]]:
    rng = random.Random(seed)
    instances: List[Dict[str, Any]] = []

    # Edge case: no clauses for several m (including m = 0).
    for m in range(0, 7):
        instances.append({"num_vars": m, "clauses": []})

    # Exhaustive-ish small cases.
    for m in range(3, 6):
        clauses = all_valid_clauses(m)
        # all single clauses
        for c in clauses:
            instances.append({"num_vars": m, "clauses": [list(c)]})
        # random subsets, including duplicates
        for _ in range(120):
            k = rng.randint(0, 6)
            chosen = [list(rng.choice(clauses)) for _ in range(k)]
            instances.append({"num_vars": m, "clauses": chosen})

    # A few larger random instances (still small enough to brute force).
    for _ in range(40):
        m = rng.randint(3, 6)
        clauses = all_valid_clauses(m)
        k = rng.randint(0, 8)
        chosen = [list(rng.choice(clauses)) for _ in range(k)]
        instances.append({"num_vars": m, "clauses": chosen})

    return instances


# ----------------------------------------------------------------------
# Test harness

class Harness:
    def __init__(self) -> None:
        self.run = 0
        self.passed = 0
        self.failures: List[str] = []

    def check(self, name: str, condition: bool, detail: str = "") -> None:
        self.run += 1
        if condition:
            self.passed += 1
        else:
            self.failures.append(f"{name}: {detail}")

    def summary(self) -> Dict[str, Any]:
        return {
            "tests_run": self.run,
            "tests_passed": self.passed,
            "failures": self.failures,
        }


def functional_tests(h: Harness) -> None:
    instances = generate_instances()
    for idx, inst in enumerate(instances):
        NaeThreeSat.validate(inst)
        expected = nae_sat_solve(inst)
        target = reduce(inst)
        # The reduction must return a valid target instance.
        try:
            ThreeColoring.validate(target)
            valid = True
        except Exception as exc:  # noqa: BLE001
            valid = False
            detail = repr(exc)
        h.check(
            f"valid_target[{idx}]",
            valid,
            f"reduce returned invalid target for {inst!r}" if not valid else "",
        )
        if not valid:
            continue
        got = three_coloring_solve(target)
        h.check(
            f"answer[{idx}]",
            got == expected,
            f"source={inst!r} expected={expected} target={target!r} got={got}",
        )


def polynomial_time_test(h: Harness) -> None:
    """A correct polynomial reduction must be fast on this trap instance.

    The clause uses variables 1,2,3 while m = 30.  A naive exhaustive search
    that enumerates assignments in itertools.product order keeps variables
    1,2,3 fixed for 2**27 iterations, so it cannot finish in the time limit.
    """
    trap = {"num_vars": 30, "clauses": [[1, 2, 3]]}
    code = (
        "import json;"
        "from reduce import reduce;"
        "print(json.dumps(reduce(" + repr(trap) + ")))"
    )
    try:
        proc = subprocess.run(
            [sys.executable, "-c", code],
            capture_output=True,
            text=True,
            timeout=10,
        )
        ok = proc.returncode == 0
        detail = proc.stderr[-500:]
    except subprocess.TimeoutExpired:
        ok = False
        detail = "reduce() did not finish within 10s on a 30-variable instance"
    h.check("polynomial_time", ok, detail)


def no_bruteforce_static_test(h: Harness) -> None:
    """Static check: reduce must not call the exponential helper."""
    import inspect
    import reduce as reduce_module

    src = inspect.getsource(reduce_module.reduce)
    h.check(
        "no_bruteforce_in_reduce",
        "naesat_bruteforce" not in src,
        "reduce() calls the exponential naesat_bruteforce helper",
    )


def main() -> None:
    h = Harness()
    functional_tests(h)
    polynomial_time_test(h)
    no_bruteforce_static_test(h)
    summary = h.summary()
    print(json.dumps(summary, indent=2))
    verified = summary["tests_run"] == summary["tests_passed"]
    verdict = {
        "verified": verified,
        "tests_run": summary["tests_run"],
        "tests_passed": summary["tests_passed"],
    }
    with open("verdict.json", "w") as fh:
        json.dump(verdict, fh)
    print("VERDICT:", json.dumps(verdict))


if __name__ == "__main__":
    main()
