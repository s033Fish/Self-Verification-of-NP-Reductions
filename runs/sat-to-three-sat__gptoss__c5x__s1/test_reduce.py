"""Independent tests for reduce.py (SAT -> 3-SAT).

We implement our own brute-force solvers for Sat and ThreeSat from the
definitions in problems.py, then compare the answer of every small source
instance with the answer of its reduction.  We also validate that every
reduction result is a legal ThreeSat instance.
"""

from __future__ import annotations

import itertools
import random
import sys

from problems import Sat, ThreeSat, InvalidInstance
from reduce import reduce


# ----------------------------------------------------------------------
# Brute-force solvers written from the problem definitions.

def _lit_true(lit: int, assignment: list[bool]) -> bool:
    """assignment[v-1] is the truth value of variable v (1-indexed)."""
    value = assignment[abs(lit) - 1]
    return value if lit > 0 else not value


def sat_solve(instance: dict) -> bool:
    """Brute-force SAT solver (works for arbitrary clause lengths)."""
    m = instance["num_vars"]
    clauses = instance["clauses"]
    for bits in itertools.product((False, True), repeat=m):
        if all(any(_lit_true(l, bits) for l in clause) for clause in clauses):
            return True
    return False


def three_sat_solve(instance: dict) -> bool:
    """Brute-force 3-SAT solver (identical semantics, separate entry point)."""
    m = instance["num_vars"]
    clauses = instance["clauses"]
    for bits in itertools.product((False, True), repeat=m):
        if all(any(_lit_true(l, bits) for l in clause) for clause in clauses):
            return True
    return False


# ----------------------------------------------------------------------
# Test bookkeeping.

tests_run = 0
tests_passed = 0
failures: list[str] = []


def check(instance: dict, label: str) -> None:
    """Run one comparison test on a source instance."""
    global tests_run, tests_passed

    tests_run += 1

    # The source instance must be valid.
    try:
        Sat.validate(instance)
    except InvalidInstance as exc:
        failures.append(f"[{label}] source instance invalid: {exc}: {instance!r}")
        return

    expected = sat_solve(instance)

    try:
        result = reduce(instance)
    except Exception as exc:  # noqa: BLE001
        failures.append(f"[{label}] reduce raised {type(exc).__name__}: {exc}: {instance!r}")
        return

    # The result must be a valid ThreeSat instance.
    try:
        ThreeSat.validate(result)
    except InvalidInstance as exc:
        failures.append(f"[{label}] reduce output invalid: {exc}: {instance!r} -> {result!r}")
        return

    got = three_sat_solve(result)
    if got != expected:
        failures.append(
            f"[{label}] MISMATCH source={instance!r} (ans={expected}) "
            f"-> target={result!r} (ans={got})"
        )
        return

    tests_passed += 1


# ----------------------------------------------------------------------
# 1. Explicit edge cases.

edge_cases = [
    {"num_vars": 0, "clauses": []},
    {"num_vars": 1, "clauses": []},
    {"num_vars": 5, "clauses": []},
    {"num_vars": 0, "clauses": [[]]},
    {"num_vars": 3, "clauses": [[]]},
    {"num_vars": 3, "clauses": [[1], []]},
    {"num_vars": 1, "clauses": [[1]]},
    {"num_vars": 1, "clauses": [[-1]]},
    {"num_vars": 1, "clauses": [[1], [-1]]},
    {"num_vars": 2, "clauses": [[1, 2]]},
    {"num_vars": 2, "clauses": [[1, 2], [-1, 2], [1, -2], [-1, -2]]},
    {"num_vars": 3, "clauses": [[1, 2, 3]]},
    {"num_vars": 3, "clauses": [[1, 2, 3], [-1, -2, -3]]},
    {"num_vars": 4, "clauses": [[1, 2, 3, 4]]},
    {"num_vars": 4, "clauses": [[1, 2, 3, 4], [-1, -2, -3, -4]]},
    {"num_vars": 5, "clauses": [[1, 2, 3, 4, 5]]},
    {"num_vars": 6, "clauses": [[1, 2, 3, 4, 5, 6]]},
    {"num_vars": 6, "clauses": [[1, 2, 3, 4, 5, 6], [-1, -2, -3, -4, -5, -6]]},
    # tautologies / duplicate literals
    {"num_vars": 3, "clauses": [[1, -1]]},
    {"num_vars": 3, "clauses": [[1, -1, 2]]},
    {"num_vars": 3, "clauses": [[1, 1, 2]]},
    {"num_vars": 3, "clauses": [[1, 1, 1]]},
    {"num_vars": 3, "clauses": [[1, 1, -1, 2, 3]]},
    {"num_vars": 3, "clauses": [[1, 2, 3], [1, -1], [2, 2]]},
    # repeated clauses
    {"num_vars": 3, "clauses": [[1, 2, 3], [1, 2, 3]]},
    {"num_vars": 3, "clauses": [[1], [1], [1]]},
    # unused variables
    {"num_vars": 10, "clauses": [[1, 2, 3]]},
    {"num_vars": 10, "clauses": [[1], [2]]},
]
for i, inst in enumerate(edge_cases):
    check(inst, f"edge{i}")


# ----------------------------------------------------------------------
# 2. Exhaustive small formulas.

# Curated clause pool over variables 1..4, covering empty, unit, binary,
# ternary, longer, duplicate-literal and tautological clauses.
POOL = [
    [],
    [1], [-1], [2], [-2],
    [1, 1], [1, -1], [1, 2], [1, -2], [-1, -2],
    [1, 2, 3], [1, 2, -3], [1, -1, 2], [1, 1, 2], [-1, -2, -3],
    [1, 2, 3, 4], [1, 2, 3, -4], [-1, -2, -3, -4], [1, 1, 2, 3],
    [1, 2, 2, 3], [1, 2, 3, 3, 4], [1, 2, 3, 4, 4],
]

for r in range(0, 4):
    for combo in itertools.combinations_with_replacement(POOL, r):
        inst = {"num_vars": 4, "clauses": [list(c) for c in combo]}
        check(inst, f"exh-r{r}")

# Also exhaustive with fewer variables (num_vars 0..3) using a pool whose
# literals fit.
for m in range(0, 4):
    small_pool = []
    for length in range(0, 4):
        for tup in itertools.product(
            [x for v in range(1, m + 1) for x in (v, -v)], repeat=length
        ):
            small_pool.append(list(tup))
    # Cap the pool for m == 3 (size 1+6+36+216 = 259) by sampling subsets.
    for r in range(0, 3):
        combos = itertools.combinations_with_replacement(small_pool, r)
        for idx, combo in enumerate(combos):
            if idx > 4000:
                break
            inst = {"num_vars": m, "clauses": [list(c) for c in combo]}
            check(inst, f"exh-m{m}-r{r}")


# ----------------------------------------------------------------------
# 3. Randomised formulas.

rng = random.Random(12345)
for t in range(4000):
    m = rng.randint(0, 6)
    n_clauses = rng.randint(0, 8)
    clauses = []
    for _ in range(n_clauses):
        length = rng.randint(0, 6)
        clause = []
        for _ in range(length):
            if m == 0:
                break
            v = rng.randint(1, m)
            clause.append(v if rng.random() < 0.5 else -v)
        clauses.append(clause)
    inst = {"num_vars": m, "clauses": clauses}
    check(inst, f"rand{t}")


# ----------------------------------------------------------------------
# 4. Polynomial-size sanity: output size must be linear in input size.

size_ok = True
for t in range(200):
    m = rng.randint(1, 8)
    n_clauses = rng.randint(1, 20)
    clauses = []
    for _ in range(n_clauses):
        length = rng.randint(1, 12)
        clauses.append([rng.choice([1, -1]) * rng.randint(1, m) for _ in range(length)])
    inst = {"num_vars": m, "clauses": clauses}
    in_size = m + sum(len(c) for c in clauses)
    out = reduce(inst)
    out_size = out["num_vars"] + sum(len(c) for c in out["clauses"])
    if out_size > 10 * in_size + 50:
        size_ok = False
        failures.append(f"[size] output too large: {in_size} -> {out_size}")

tests_run += 1
if size_ok:
    tests_passed += 1


# ----------------------------------------------------------------------
# Report.

print(f"tests_run={tests_run}")
print(f"tests_passed={tests_passed}")
if failures:
    print(f"FAILURES ({len(failures)}):")
    for f in failures[:20]:
        print("  " + f)
else:
    print("ALL TESTS PASSED")

verified = (tests_run > 0 and tests_passed == tests_run and not failures)

import json
with open("verdict.json", "w") as fh:
    json.dump({"verified": verified, "tests_run": tests_run, "tests_passed": tests_passed}, fh)
print("verdict:", verified)

sys.exit(0 if verified else 1)
