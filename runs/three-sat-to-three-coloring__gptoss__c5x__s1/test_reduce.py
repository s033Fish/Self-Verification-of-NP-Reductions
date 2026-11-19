"""Independent tests for reduce.py (3-SAT -> 3-Coloring).

We implement our own brute-force solvers for both problems directly from the
definitions in problems.py, then compare answers on many small source
instances.  We also check the *polynomial-time / no brute-force* requirement
empirically.
"""

from __future__ import annotations

import itertools
import random
import subprocess
import sys

from problems import ThreeSat, ThreeColoring
import reduce as reduce_mod


# ----------------------------------------------------------------------
# Brute-force solvers written from the problem definitions.

def sat_solve(inst: dict) -> bool:
    """True iff the 3-SAT instance is satisfiable (exhaustive)."""
    m = inst["num_vars"]
    clauses = inst["clauses"]
    for bits in itertools.product([False, True], repeat=m):
        ok = True
        for clause in clauses:
            if not any((lit > 0) == bits[abs(lit) - 1] for lit in clause):
                ok = False
                break
        if ok:
            return True
    return False


def color_solve(inst: dict) -> bool:
    """True iff the graph is 3-colorable (backtracking)."""
    n = inst["n"]
    adj = [set() for _ in range(n)]
    for u, v in inst["edges"]:
        adj[u].add(v)
        adj[v].add(u)
    colors = [None] * n

    def bt(i: int) -> bool:
        if i == n:
            return True
        for c in range(3):
            if all(colors[j] != c for j in adj[i] if j < i):
                colors[i] = c
                if bt(i + 1):
                    return True
                colors[i] = None
        return False

    return bt(0)


# ----------------------------------------------------------------------
# Tiny test harness.

tests_run = 0
tests_passed = 0
failures: list[str] = []


def check(name: str, condition: bool) -> None:
    global tests_run, tests_passed
    tests_run += 1
    if condition:
        tests_passed += 1
    else:
        failures.append(name)


# ----------------------------------------------------------------------
# Sanity checks of our own solvers against the documented edge cases.

check("sat: no clauses is yes (m=0)", sat_solve({"num_vars": 0, "clauses": []}) is True)
check("sat: no clauses is yes (m=5)", sat_solve({"num_vars": 5, "clauses": []}) is True)
check("sat: (x1 or x2 or x3) is yes", sat_solve({"num_vars": 3, "clauses": [[1, 2, 3]]}) is True)
check("sat: all-false clause is no",
      sat_solve({"num_vars": 3, "clauses": [[-1, -2, -3], [1, 2, 3], [1, 2, -3],
                                            [1, -2, 3], [1, -2, -3], [-1, 2, 3],
                                            [-1, 2, -3], [-1, -2, 3]]}) is False)
check("color: n=0 is yes", color_solve({"n": 0, "edges": []}) is True)
check("color: triangle is yes",
      color_solve({"n": 3, "edges": [[0, 1], [1, 2], [0, 2]]}) is True)
check("color: K4 is no",
      color_solve({"n": 4, "edges": [[0, 1], [0, 2], [0, 3], [1, 2], [1, 3], [2, 3]]}) is False)


# ----------------------------------------------------------------------
# Random small 3-SAT instances; compare solver answers on source and reduce().

def random_sat(rng: random.Random, m: int, num_clauses: int) -> dict:
    clauses = []
    for _ in range(num_clauses):
        vs = rng.sample(range(1, m + 1), 3)
        clause = [v if rng.random() < 0.5 else -v for v in vs]
        clauses.append(clause)
    return {"num_vars": m, "clauses": clauses}


rng = random.Random(12345)
for trial in range(300):
    m = rng.randint(0, 6)
    if m < 3:
        num_clauses = 0
    else:
        num_clauses = rng.randint(0, 12)
    inst = random_sat(rng, m, num_clauses)
    ThreeSat.validate(inst)  # input is well-formed

    expected = sat_solve(inst)
    graph = reduce_mod.reduce(inst)

    # reduce must return a valid target instance
    try:
        ThreeColoring.validate(graph)
        valid = True
    except Exception:
        valid = False
    check(f"trial {trial}: reduce output valid", valid)

    got = color_solve(graph) if valid else None
    check(f"trial {trial}: answers agree (sat={expected}, color={got})", got == expected)


# ----------------------------------------------------------------------
# Requirement: reduce must run in polynomial time and must not call a
# brute-force solver.  We test this empirically with a large instance that
# any polynomial reduction would handle instantly.  The formula below is
# unsatisfiable (all 8 clauses over 3 variables) but has num_vars=40, so the
# exhaustive 2^40 search inside reduce.py cannot finish.

BIG = {
    "num_vars": 40,
    "clauses": [
        [1, 2, 3], [1, 2, -3], [1, -2, 3], [1, -2, -3],
        [-1, 2, 3], [-1, 2, -3], [-1, -2, 3], [-1, -2, -3],
    ],
}

runner = (
    "import sys, time\n"
    "sys.path.insert(0, '.')\n"
    "from reduce import reduce\n"
    "inst = " + repr(BIG) + "\n"
    "t = time.time()\n"
    "g = reduce(inst)\n"
    "print('elapsed', time.time() - t)\n"
)

try:
    proc = subprocess.run(
        [sys.executable, "-c", runner],
        capture_output=True, text=True, timeout=10, cwd=".",
    )
    finished = proc.returncode == 0
    detail = proc.stdout.strip() or proc.stderr.strip()
except subprocess.TimeoutExpired:
    finished = False
    detail = "TIMEOUT after 10s"

check(
    "reduce runs in polynomial time on large instance (no brute force)",
    finished,
)

# Static check: does reduce.py contain / call an exhaustive search?
src = open("reduce.py").read()
check(
    "reduce.py does not perform exhaustive 2^num_vars search",
    "itertools.product" not in src and "_is_satisfiable" not in src,
)


# ----------------------------------------------------------------------
print("tests_run =", tests_run)
print("tests_passed =", tests_passed)
if failures:
    print("FAILURES:")
    for f in failures:
        print("  -", f)
print("large-instance detail:", detail)
