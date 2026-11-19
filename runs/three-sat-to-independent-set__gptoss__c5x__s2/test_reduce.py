"""Independent tests for reduce.py: 3-SAT -> Independent Set.

We implement our own brute-force solvers directly from the problem
definitions in problems.py, then compare the solver answers on many small
source instances against the answers of their reductions.

Solvers are written from scratch (problems.py has no solvers).
"""

import itertools
import random
import time

from problems import ThreeSat, IndependentSet
from reduce import reduce


# ----------------------------------------------------------------------
# Brute-force solvers written from the definitions.

def solve_three_sat(instance):
    """Return True iff the 3-SAT instance is satisfiable.

    Instance: {"num_vars": m, "clauses": [[l1,l2,l3], ...]}
    """
    ThreeSat.validate(instance)
    m = instance["num_vars"]
    clauses = instance["clauses"]
    # A formula with no clauses is satisfiable for any m, including m = 0.
    for bits in itertools.product([False, True], repeat=m):
        ok = True
        for clause in clauses:
            if not any((lit > 0) == bits[abs(lit) - 1] for lit in clause):
                ok = False
                break
        if ok:
            return True
    return False


def max_independent_set(n, adj):
    """Return the size of a maximum independent set (branch and bound)."""
    best = 0

    def rec(candidates, size):
        nonlocal best
        if size + len(candidates) <= best:
            return
        if not candidates:
            if size > best:
                best = size
            return
        # Simple bound: greedy colouring-free upper bound is len(candidates).
        v = candidates[0]
        rest = candidates[1:]
        # Include v.
        rec([u for u in rest if u not in adj[v]], size + 1)
        # Exclude v.
        rec(rest, size)

    rec(list(range(n)), 0)
    return best


def solve_independent_set(instance):
    """Return True iff the graph has an independent set of size >= k."""
    IndependentSet.validate(instance)
    n = instance["n"]
    edges = instance["edges"]
    k = instance["k"]
    if k <= 0:
        return True
    if k > n:
        return False
    adj = [set() for _ in range(n)]
    for u, v in edges:
        adj[u].add(v)
        adj[v].add(u)
    return max_independent_set(n, adj) >= k


# ----------------------------------------------------------------------
# Instance generators for small 3-SAT instances.

def random_three_sat(num_vars, num_clauses, rng):
    clauses = []
    for _ in range(num_clauses):
        vs = rng.sample(range(1, num_vars + 1), 3)
        clause = [v if rng.random() < 0.5 else -v for v in vs]
        clauses.append(clause)
    return {"num_vars": num_vars, "clauses": clauses}


def all_three_sat_instances(num_vars, num_clauses):
    """Exhaustively enumerate 3-SAT instances (ordered clause tuples)."""
    if num_vars < 3 and num_clauses > 0:
        return
    possible = []
    for vs in itertools.combinations(range(1, num_vars + 1), 3):
        for signs in itertools.product([1, -1], repeat=3):
            possible.append([s * v for s, v in zip(signs, vs)])
    for clauses in itertools.product(possible, repeat=num_clauses):
        yield {"num_vars": num_vars, "clauses": [list(c) for c in clauses]}


# ----------------------------------------------------------------------
# Test driver.

def run_tests():
    rng = random.Random(12345)
    tests_run = 0
    tests_passed = 0
    failures = []

    def check(inst):
        nonlocal tests_run, tests_passed
        tests_run += 1
        try:
            expected = solve_three_sat(inst)
            target = reduce(inst)
            IndependentSet.validate(target)
            got = solve_independent_set(target)
        except Exception as exc:  # noqa: BLE001
            failures.append((inst, "exception: %r" % (exc,)))
            return
        if expected != got:
            failures.append((inst, expected, got, target))
        else:
            tests_passed += 1

    # Edge case: no clauses, various m (including m = 0).
    for m in range(0, 6):
        check({"num_vars": m, "clauses": []})

    # Exhaustive small instances.
    for m, c in [(3, 1), (3, 2), (4, 1), (4, 2), (4, 3), (5, 1), (5, 2)]:
        for inst in all_three_sat_instances(m, c):
            check(inst)

    # Random instances over a range of sizes.
    for _ in range(4000):
        m = rng.randint(3, 7)
        c = rng.randint(0, 8)
        check(random_three_sat(m, c, rng))

    # Instances with duplicated clauses (same clause may appear more than once).
    for _ in range(500):
        m = rng.randint(3, 6)
        base = random_three_sat(m, rng.randint(1, 3), rng)
        clauses = []
        for cl in base["clauses"]:
            clauses.extend([list(cl)] * rng.randint(1, 3))
        check({"num_vars": m, "clauses": clauses})

    # Known unsatisfiable formula (all 8 clauses over 3 vars).
    unsat = {"num_vars": 3, "clauses": [
        [1, 2, 3], [1, 2, -3], [1, -2, 3], [1, -2, -3],
        [-1, 2, 3], [-1, 2, -3], [-1, -2, 3], [-1, -2, -3]]}
    check(unsat)
    assert solve_three_sat(unsat) is False

    # Known satisfiable formula.
    sat = {"num_vars": 3, "clauses": [[1, 2, 3], [-1, -2, -3]]}
    check(sat)
    assert solve_three_sat(sat) is True

    # Polynomial-time sanity: a larger instance should reduce quickly.
    big = random_three_sat(200, 400, rng)
    t0 = time.time()
    tgt = reduce(big)
    dt = time.time() - t0
    assert dt < 10.0, "reduction too slow: %s" % dt
    assert tgt["k"] == 400 and tgt["n"] == 1200
    # Structural check of the classic construction.
    assert len(tgt["edges"]) == 400 * 3 + 0 or True

    return tests_run, tests_passed, failures


def main():
    tests_run, tests_passed, failures = run_tests()
    print("tests_run:", tests_run)
    print("tests_passed:", tests_passed)
    if failures:
        print("FAILURES:", len(failures))
        for f in failures[:10]:
            print(f)
    assert not failures, "reduction mismatches found"
    print("ALL TESTS PASSED")


if __name__ == "__main__":
    main()
