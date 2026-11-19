"""Independent verification of reduce.py (3-SAT -> Independent Set).

We implement our own brute-force solvers for both problems directly from the
definitions in problems.py, generate many small valid source instances, run
reduce on them, and compare the answers.
"""

import itertools
import random

import problems
from problems import ThreeSat, IndependentSet
from reduce import reduce


# ----------------------------------------------------------------------
# Brute-force solvers written from the definitions.

def sat_solve(instance):
    """True iff some assignment satisfies every clause (brute force)."""
    num_vars = instance["num_vars"]
    clauses = instance["clauses"]
    for bits in itertools.product([False, True], repeat=num_vars):
        # variable v (1..num_vars) is bits[v-1]
        ok = True
        for clause in clauses:
            if not any((bits[abs(lit) - 1] if lit > 0 else not bits[abs(lit) - 1])
                       for lit in clause):
                ok = False
                break
        if ok:
            return True
    return False


def is_solve(instance):
    """True iff the graph has an independent set of size >= k (brute force)."""
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
    for size in range(k, n + 1):
        for subset in itertools.combinations(range(n), size):
            s = set(subset)
            if all(not (adj[u] & s) for u in subset):
                return True
    return False


# ----------------------------------------------------------------------
# Instance generation.

def gen_sat(rng, max_vars=4, max_clauses=4):
    m = rng.randint(0, max_vars)
    nclauses = rng.randint(0, max_clauses)
    clauses = []
    for _ in range(nclauses):
        if m < 3:
            # cannot form a valid clause; stop
            break
        vs = rng.sample(range(1, m + 1), 3)
        clause = [v if rng.random() < 0.5 else -v for v in vs]
        clauses.append(clause)
    return {"num_vars": m, "clauses": clauses}


def main():
    rng = random.Random(12345)
    tests_run = 0
    tests_passed = 0
    failures = []

    def check(inst, tag):
        nonlocal tests_run, tests_passed
        tests_run += 1
        try:
            ThreeSat.validate(inst)
            src = sat_solve(inst)
            out = reduce(inst)
            IndependentSet.validate(out)
            tgt = is_solve(out)
            if src == tgt:
                tests_passed += 1
            else:
                failures.append((tag, inst, out, src, tgt))
        except Exception as e:  # noqa: BLE001
            failures.append((tag + " EXC", inst, repr(e), None, None))

    # Deterministic edge cases.
    check({"num_vars": 0, "clauses": []}, "empty m=0")
    check({"num_vars": 5, "clauses": []}, "empty m=5")
    check({"num_vars": 3, "clauses": [[1, 2, 3]]}, "single clause")
    check({"num_vars": 3, "clauses": [[1, 2, 3], [-1, -2, -3]]}, "two clauses")
    check({"num_vars": 3, "clauses": [[1, 2, 3], [-1, 2, 3], [1, -2, 3],
                                      [1, 2, -3], [-1, -2, -3]]}, "unsat-ish")
    # Duplicate clauses.
    check({"num_vars": 3, "clauses": [[1, 2, 3], [1, 2, 3]]}, "dup clause")
    # All 8 clauses over 3 vars (unsatisfiable).
    allc = []
    for signs in itertools.product([1, -1], repeat=3):
        allc.append([signs[i] * (i + 1) for i in range(3)])
    check({"num_vars": 3, "clauses": allc}, "all 8 clauses unsat")
    # Variables unused.
    check({"num_vars": 6, "clauses": [[1, 2, 3], [-1, -2, -3]]}, "unused vars")

    # Random instances.
    for _ in range(4000):
        inst = gen_sat(rng)
        check(inst, "random")

    # Exhaustive-ish: all formulas with m=3, up to 2 clauses.
    lits = [1, -1, 2, -2, 3, -3]
    clauses3 = []
    for combo in itertools.combinations(range(3), 3):
        pass
    # all valid clauses on vars 1..3
    valid_clauses = []
    for vs in itertools.combinations([1, 2, 3], 3):
        for signs in itertools.product([1, -1], repeat=3):
            valid_clauses.append([s * v for s, v in zip(signs, vs)])
    for c1 in valid_clauses:
        check({"num_vars": 3, "clauses": [c1]}, "exh1")
    for c1 in valid_clauses:
        for c2 in valid_clauses:
            check({"num_vars": 3, "clauses": [c1, c2]}, "exh2")

    print("tests_run:", tests_run)
    print("tests_passed:", tests_passed)
    print("failures:", len(failures))
    for f in failures[:10]:
        print("FAIL", f)

    with open("verdict.json", "w") as fh:
        import json
        json.dump({"verified": len(failures) == 0 and tests_run == tests_passed,
                   "tests_run": tests_run,
                   "tests_passed": tests_passed}, fh)


if __name__ == "__main__":
    main()
