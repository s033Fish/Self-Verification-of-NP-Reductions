"""Tests for the 3-SAT -> Dominating Set reduction."""

import itertools
import random

from problems import ThreeSat, DominatingSet
from reduce import reduce


def sat_solve(inst):
    """Brute-force 3-SAT solver."""
    m = inst["num_vars"]
    clauses = inst["clauses"]
    for bits in range(1 << m):
        ok = True
        for clause in clauses:
            satisfied = False
            for lit in clause:
                bit = (bits >> (abs(lit) - 1)) & 1
                if (lit > 0 and bit == 1) or (lit < 0 and bit == 0):
                    satisfied = True
                    break
            if not satisfied:
                ok = False
                break
        if ok:
            return True
    return False


def ds_solve(inst):
    """Brute-force Dominating Set solver (at most k)."""
    n = inst["n"]
    k = inst["k"]
    if k < 0:
        return False
    if n == 0:
        return True
    adj = [1 << i for i in range(n)]
    for u, v in inst["edges"]:
        adj[u] |= 1 << v
        adj[v] |= 1 << u
    full = (1 << n) - 1
    for s in range(0, min(k, n) + 1):
        for combo in itertools.combinations(range(n), s):
            dom = 0
            for i in combo:
                dom |= adj[i]
            if dom == full:
                return True
    return False


def random_instance(rng, num_vars, num_clauses):
    clauses = []
    for _ in range(num_clauses):
        vs = rng.sample(range(1, num_vars + 1), 3)
        clause = [v if rng.random() < 0.5 else -v for v in vs]
        clauses.append(clause)
    return {"num_vars": num_vars, "clauses": clauses}


def main():
    rng = random.Random(12345)
    tests = []

    # Edge cases.
    tests.append({"num_vars": 0, "clauses": []})
    tests.append({"num_vars": 1, "clauses": []})
    tests.append({"num_vars": 3, "clauses": []})
    tests.append({"num_vars": 5, "clauses": []})

    # The unique unsatisfiable 3-variable 3-CNF formula (all 8 clauses).
    all_clauses = []
    for signs in itertools.product([1, -1], repeat=3):
        all_clauses.append([signs[0] * 1, signs[1] * 2, signs[2] * 3])
    tests.append({"num_vars": 3, "clauses": all_clauses})

    # A known unsatisfiable 4-variable formula (all 16 clauses).
    all_clauses4 = []
    for signs in itertools.product([1, -1], repeat=4):
        all_clauses4.append([signs[0] * 1, signs[1] * 2, signs[2] * 3])
    tests.append({"num_vars": 4, "clauses": all_clauses4})

    # Random small instances.
    for _ in range(400):
        num_vars = rng.randint(0, 4)
        if num_vars < 3:
            num_clauses = 0
        else:
            num_clauses = rng.randint(0, 5)
        tests.append(random_instance(rng, num_vars, num_clauses))

    tests_run = 0
    tests_passed = 0
    for inst in tests:
        ThreeSat.validate(inst)
        expected = sat_solve(inst)
        target = reduce(inst)
        DominatingSet.validate(target)
        got = ds_solve(target)
        tests_run += 1
        if expected == got:
            tests_passed += 1
        else:
            print("MISMATCH", inst, "expected", expected, "got", got, "target", target)

    print(f"tests_run={tests_run} tests_passed={tests_passed}")
    assert tests_run == tests_passed, "some tests failed"


if __name__ == "__main__":
    main()
