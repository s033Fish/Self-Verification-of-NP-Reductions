"""Independent tests for reduce.py (3-SAT -> Subset Sum).

We implement our own brute-force solvers from the definitions in problems.py
(which provides no solvers), generate many small 3-SAT instances, and check
that each reduced Subset-Sum instance has the same answer as the source.

We also check the *requirements* on reduce.py: it must run in polynomial time
and must not call a brute-force solver.
"""

from __future__ import annotations

import ast
import itertools
import json
import random
import time
from typing import Any, Dict, List

import problems
from problems import ThreeSat, SubsetSum
import reduce as reduce_mod


# ----------------------------------------------------------------------
# Our own brute-force solvers (from the documented definitions)

def solve_three_sat(instance: Dict[str, Any]) -> bool:
    """Brute force 3-SAT: try every assignment of variables 1..num_vars."""
    m = instance["num_vars"]
    clauses = instance["clauses"]
    for bits in itertools.product([False, True], repeat=m):
        # bits[i] is the value of variable i+1
        ok = True
        for clause in clauses:
            if not any(
                (lit > 0 and bits[abs(lit) - 1]) or (lit < 0 and not bits[abs(lit) - 1])
                for lit in clause
            ):
                ok = False
                break
        if ok:
            return True
    return False


def solve_subset_sum(instance: Dict[str, Any]) -> bool:
    """Brute force Subset Sum: try every subset of the numbers."""
    numbers = instance["numbers"]
    target = instance["target"]
    n = len(numbers)
    for mask in range(1 << n):
        total = 0
        for i in range(n):
            if (mask >> i) & 1:
                total += numbers[i]
        if total == target:
            return True
    return False


# ----------------------------------------------------------------------
# Instance generation

def random_three_sat(rng: random.Random, num_vars: int, num_clauses: int) -> Dict[str, Any]:
    clauses: List[List[int]] = []
    if num_vars >= 3:
        for _ in range(num_clauses):
            vars_ = rng.sample(range(1, num_vars + 1), 3)
            clause = [v if rng.random() < 0.5 else -v for v in vars_]
            clauses.append(clause)
    return {"num_vars": num_vars, "clauses": clauses}


def generate_instances() -> List[Dict[str, Any]]:
    rng = random.Random(12345)
    instances: List[Dict[str, Any]] = []

    # Edge cases: no clauses, any m including 0.
    for m in range(0, 6):
        instances.append({"num_vars": m, "clauses": []})

    # All small formulas exhaustively-ish: m in 3..4, all clause sets of size 0..3
    # drawn from all possible clauses.
    for m in (3, 4):
        all_clauses = []
        for vars_ in itertools.combinations(range(1, m + 1), 3):
            for signs in itertools.product([1, -1], repeat=3):
                all_clauses.append([s * v for s, v in zip(signs, vars_)])
        for k in range(0, 4):
            for combo in itertools.combinations(all_clauses, k):
                instances.append({"num_vars": m, "clauses": [list(c) for c in combo]})

    # Random instances with 3..6 vars.
    for _ in range(400):
        m = rng.randint(3, 6)
        k = rng.randint(0, 8)
        instances.append(random_three_sat(rng, m, k))

    # Instances with unused variables.
    for _ in range(50):
        m = rng.randint(3, 7)
        k = rng.randint(1, 4)
        inst = random_three_sat(rng, m, k)
        instances.append(inst)

    return instances


# ----------------------------------------------------------------------
# Static / structural check that reduce does not call a brute-force solver

def reduce_source_uses_bruteforce() -> bool:
    """Return True if reduce.py contains an exponential search loop."""
    src = open("reduce.py").read()
    tree = ast.parse(src)
    # Look for a shift by a variable (e.g. 1 << m) which signals 2^m search.
    for node in ast.walk(tree):
        if isinstance(node, ast.BinOp) and isinstance(node.op, ast.LShift):
            return True
    # Also look for the helper name pattern.
    return "_is_sat" in src


def timing_check() -> bool:
    """A correct polynomial reduction should handle many variables quickly.

    We use an *unsatisfiable* formula over 24 variables: the 8 clauses on
    variables 1..3 (all sign combinations) are unsatisfiable, and variables
    4..24 are unused. A brute-force reduction must try all 2^24 assignments.
    We run reduce in a subprocess with a timeout so the test cannot hang.
    """
    import subprocess
    import sys

    m = 24
    clauses = []
    for signs in itertools.product([1, -1], repeat=3):
        clauses.append([s * v for s, v in zip(signs, (1, 2, 3))])
    inst = {"num_vars": m, "clauses": clauses}

    runner = (
        "import json, sys; sys.path.insert(0, '.');"
        "import reduce;"
        "inst = json.loads(sys.argv[1]);"
        "print(json.dumps(reduce.reduce(inst)))"
    )
    try:
        proc = subprocess.run(
            [sys.executable, "-c", runner, json.dumps(inst)],
            capture_output=True, text=True, timeout=5.0,
        )
        return proc.returncode == 0
    except subprocess.TimeoutExpired:
        return False


# ----------------------------------------------------------------------
# Run tests

def main() -> None:
    tests_run = 0
    tests_passed = 0
    failures: List[str] = []

    instances = generate_instances()
    for inst in instances:
        tests_run += 1
        try:
            ThreeSat.validate(inst)
            expected = solve_three_sat(inst)
            out = reduce_mod.reduce(inst)
            SubsetSum.validate(out)
            got = solve_subset_sum(out)
            if got == expected:
                tests_passed += 1
            else:
                failures.append(f"mismatch: {inst} -> {out} expected {expected} got {got}")
        except Exception as exc:  # noqa: BLE001
            failures.append(f"error on {inst}: {exc!r}")

    # Requirement checks.
    tests_run += 1
    if reduce_source_uses_bruteforce():
        failures.append("reduce.py uses an exponential/brute-force search (violates polynomial-time requirement)")
    else:
        tests_passed += 1

    tests_run += 1
    try:
        if timing_check():
            tests_passed += 1
        else:
            failures.append("reduce.py is too slow on a 24-variable unsatisfiable instance (brute-force behaviour)")
    except Exception as exc:  # noqa: BLE001
        failures.append(f"timing check raised: {exc!r}")

    print(f"tests_run={tests_run} tests_passed={tests_passed}")
    if failures:
        print("FAILURES:")
        for f in failures[:20]:
            print("  -", f)
        print(f"  ... total failures: {len(failures)}")
    else:
        print("All checks passed.")

    # Write verdict.json
    import json
    verified = (tests_passed == tests_run) and not failures
    with open("verdict.json", "w") as fh:
        json.dump({"verified": verified, "tests_run": tests_run, "tests_passed": tests_passed}, fh)
    print("verdict:", {"verified": verified, "tests_run": tests_run, "tests_passed": tests_passed})


if __name__ == "__main__":
    main()
