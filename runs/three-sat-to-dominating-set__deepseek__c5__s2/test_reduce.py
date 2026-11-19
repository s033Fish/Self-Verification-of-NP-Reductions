"""Independent tests for reduce.py (3-SAT -> Dominating Set).

Contains brute-force solvers written directly from the problem definitions,
plus a battery of small-instance comparisons between the source answer and
the answer to the reduced target instance.
"""

from __future__ import annotations

import itertools
import random
import time

from problems import SOURCE, TARGET
from reduce import reduce


# ----------------------------------------------------------------------
# Brute-force solvers (from the definitions, no external solvers)

def solve_three_sat(instance):
    """Return True iff the 3-SAT instance is satisfiable."""
    num_vars = instance["num_vars"]
    clauses = instance["clauses"]
    for bits in itertools.product([False, True], repeat=num_vars):
        # variable v (1..num_vars) -> bits[v-1]
        if all(
            any((literal > 0) == bits[abs(literal) - 1] for literal in clause)
            for clause in clauses
        ):
            return True
    return False


def solve_dominating_set(instance):
    """Return True iff the graph has a dominating set of size <= k."""
    n = instance["n"]
    edges = instance["edges"]
    k = instance["k"]

    if k < 0:
        return False
    if k >= n:
        return True

    adj = [set() for _ in range(n)]
    for u, v in edges:
        adj[u].add(v)
        adj[v].add(u)

    def dominated_by(subset):
        covered = set(subset)
        for u in subset:
            covered |= adj[u]
        return len(covered) == n

    for size in range(0, k + 1):
        for subset in itertools.combinations(range(n), size):
            if dominated_by(subset):
                return True
    return False


# ----------------------------------------------------------------------
# Test harness

_tests_run = 0
_tests_passed = 0
_failures = []


def check(condition, message):
    global _tests_run, _tests_passed
    _tests_run += 1
    if condition:
        _tests_passed += 1
    else:
        _failures.append(message)
        print("FAIL:", message)


def compare(instance, label):
    """Check reduce output is valid and answers agree."""
    SOURCE.validate(instance)
    expected = solve_three_sat(instance)
    target = reduce(instance)
    TARGET.validate(target)
    got = solve_dominating_set(target)
    check(
        expected == got,
        f"{label}: source={expected} target={got} instance={instance} target={target}",
    )


# ----------------------------------------------------------------------
# 1. Fixed edge cases

compare({"num_vars": 0, "clauses": []}, "m=0 no clauses")
compare({"num_vars": 1, "clauses": []}, "m=1 no clauses")
compare({"num_vars": 3, "clauses": []}, "m=3 no clauses")
compare({"num_vars": 3, "clauses": [[1, 2, 3]]}, "single clause")
compare({"num_vars": 3, "clauses": [[1, 2, 3], [1, 2, 3]]}, "duplicate clause")
compare(
    {"num_vars": 3, "clauses": [[1, 2, 3], [-1, -2, -3], [1, -2, 3], [-1, 2, -3]]},
    "unsat-ish 4 clauses",
)
# all 8 clauses on 3 vars -> unsatisfiable
all_clauses = []
for signs in itertools.product([1, -1], repeat=3):
    all_clauses.append([signs[i] * (i + 1) for i in range(3)])
compare({"num_vars": 3, "clauses": all_clauses}, "all 8 clauses unsat")
# 7 of the 8 clauses -> still unsat
compare({"num_vars": 3, "clauses": all_clauses[:7]}, "7 clauses unsat")
# 6 clauses: check a satisfiable subset
compare({"num_vars": 3, "clauses": all_clauses[:6]}, "6 clauses")

# variables that do not appear
compare({"num_vars": 5, "clauses": [[1, 2, 3]]}, "extra unused vars")
compare({"num_vars": 6, "clauses": [[4, 5, 6]]}, "only high vars")

# ----------------------------------------------------------------------
# 2. Random small instances

rng = random.Random(12345)
for trial in range(400):
    num_vars = rng.randint(0, 6)
    if num_vars == 0:
        clauses = []
    else:
        num_clauses = rng.randint(0, 8)
        clauses = []
        for _ in range(num_clauses):
            if num_vars < 3:
                # cannot build a valid 3-literal clause on <3 distinct vars
                break
            variables = rng.sample(range(1, num_vars + 1), 3)
            clause = [v * rng.choice([1, -1]) for v in variables]
            clauses.append(clause)
    compare({"num_vars": num_vars, "clauses": clauses}, f"random trial {trial}")

# ----------------------------------------------------------------------
# 3. Exhaustive-ish over all clause sets on 3 variables (small sizes)

universe = []
for signs in itertools.product([1, -1], repeat=3):
    universe.append(tuple(signs[i] * (i + 1) for i in range(3)))

# all single clauses, all pairs, all triples (with repetition allowed)
for r in (1, 2, 3):
    for combo in itertools.combinations_with_replacement(universe, r):
        compare({"num_vars": 3, "clauses": [list(c) for c in combo]}, f"combo {combo}")

# ----------------------------------------------------------------------
# 4. Structural / polynomial-time sanity checks

# reduce must not import or call a brute-force solver
import inspect
src = inspect.getsource(reduce)
for forbidden in ("solve_", "brute", "itertools", "product", "combinations"):
    check(forbidden not in src, f"reduce source mentions {forbidden!r}")

# scaling: reduction should be fast on a larger instance
big_clauses = []
for _ in range(300):
    vs = rng.sample(range(1, 61), 3)
    big_clauses.append([v * rng.choice([1, -1]) for v in vs])
big = {"num_vars": 60, "clauses": big_clauses}
t0 = time.time()
big_target = reduce(big)
elapsed = time.time() - t0
TARGET.validate(big_target)
check(big_target["n"] == 3 * 60 + 300, "big target n correct")
check(elapsed < 2.0, f"reduction too slow: {elapsed}")

# ----------------------------------------------------------------------
# 5. Directly verify the reduction's structural claim on random instances:
#    minimum dominating set size of the target is >= num_vars, and equals
#    num_vars iff satisfiable.

for trial in range(200):
    num_vars = rng.randint(3, 5)
    num_clauses = rng.randint(0, 6)
    clauses = []
    for _ in range(num_clauses):
        vs = rng.sample(range(1, num_vars + 1), 3)
        clauses.append([v * rng.choice([1, -1]) for v in vs])
    inst = {"num_vars": num_vars, "clauses": clauses}
    target = reduce(inst)
    # find minimum dominating set size by brute force
    n = target["n"]
    adj = [set() for _ in range(n)]
    for u, v in target["edges"]:
        adj[u].add(v)
        adj[v].add(u)
    min_size = None
    for size in range(0, n + 1):
        found = False
        for subset in itertools.combinations(range(n), size):
            covered = set(subset)
            for u in subset:
                covered |= adj[u]
            if len(covered) == n:
                found = True
                break
        if found:
            min_size = size
            break
    sat = solve_three_sat(inst)
    check(min_size >= num_vars, f"min DS {min_size} < num_vars {num_vars}")
    check(
        (min_size == num_vars) == sat,
        f"min DS {min_size} vs num_vars {num_vars} sat={sat} inst={inst}",
    )

# ----------------------------------------------------------------------
print()
print(f"tests_run={_tests_run} tests_passed={_tests_passed}")
if _failures:
    print(f"{len(_failures)} FAILURES")
    raise SystemExit(1)
print("ALL TESTS PASSED")
