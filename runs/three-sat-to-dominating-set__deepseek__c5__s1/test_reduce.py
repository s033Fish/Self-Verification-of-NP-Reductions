"""Independent tests for reduce.py: 3-SAT -> Dominating Set.

We implement our own brute-force solvers for both problems from the
docstrings in problems.py, generate many small source instances, reduce
them, and compare answers.  We also validate every produced target
instance against DominatingSet.validate.
"""

import itertools
import json
import random

from problems import ThreeSat, DominatingSet
import reduce as red


# ----------------------------------------------------------------------
# Brute-force solvers (independent of reduce.py)
# ----------------------------------------------------------------------

def sat_solve(instance):
    """Return True iff the 3-SAT instance is satisfiable."""
    m = instance["num_vars"]
    clauses = instance["clauses"]
    for bits in itertools.product([False, True], repeat=m):
        good = True
        for clause in clauses:
            if not any(
                (bits[abs(lit) - 1] if lit > 0 else not bits[abs(lit) - 1])
                for lit in clause
            ):
                good = False
                break
        if good:
            return True
    return False


def ds_solve(instance):
    """Return True iff there is a dominating set of size <= k."""
    n = instance["n"]
    edges = instance["edges"]
    k = instance["k"]
    if k < 0:
        return False
    if k >= n:
        return True
    closed = [set([i]) for i in range(n)]
    for u, v in edges:
        closed[u].add(v)
        closed[v].add(u)
    for size in range(0, k + 1):
        for comb in itertools.combinations(range(n), size):
            dom = set()
            for x in comb:
                dom |= closed[x]
            if len(dom) == n:
                return True
    return False


# ----------------------------------------------------------------------
# Instance generation
# ----------------------------------------------------------------------

def all_clauses(m):
    out = []
    for vars_ in itertools.combinations(range(1, m + 1), 3):
        for signs in itertools.product([1, -1], repeat=3):
            out.append([s * v for s, v in zip(signs, vars_)])
    return out


def gen_instances():
    instances = []
    # Empty-clause formulas for m = 0,1,2 (and a few larger).
    for m in range(0, 5):
        instances.append({"num_vars": m, "clauses": []})
    # m = 3: every subset of the 8 possible clauses.
    for r in range(0, 9):
        for combo in itertools.combinations(all_clauses(3), r):
            instances.append({"num_vars": 3, "clauses": [list(c) for c in combo]})
    # m = 4,5,6: random formulas (with possible duplicate clauses).
    rng = random.Random(12345)
    for m in (4, 5, 6):
        pool = all_clauses(m)
        for _ in range(400):
            t = rng.randint(0, 6)
            clauses = [list(rng.choice(pool)) for _ in range(t)]
            instances.append({"num_vars": m, "clauses": clauses})
    # Formulas where some variables never appear.
    for m in (4, 5, 6):
        pool = all_clauses(m)
        for _ in range(150):
            t = rng.randint(0, 5)
            clauses = [list(rng.choice(pool)) for _ in range(t)]
            instances.append({"num_vars": m, "clauses": clauses})
    return instances


def main():
    instances = gen_instances()
    tests_run = 0
    tests_passed = 0
    failures = []

    for inst in instances:
        ThreeSat.validate(inst)          # source must be well formed
        target = red.reduce(inst)
        DominatingSet.validate(target)   # target must be well formed
        expected = sat_solve(inst)
        got = ds_solve(target)
        tests_run += 1
        if expected == got:
            tests_passed += 1
        else:
            failures.append((inst, target, expected, got))

    # Extra explicit edge cases.
    edge = [
        {"num_vars": 0, "clauses": []},
        {"num_vars": 1, "clauses": []},
        {"num_vars": 2, "clauses": []},
        {"num_vars": 3, "clauses": [[1, 2, 3]]},
        {"num_vars": 3, "clauses": [[-1, -2, -3]]},
        {"num_vars": 3, "clauses": [[1, 2, 3], [1, 2, 3]]},
    ]
    for inst in edge:
        target = red.reduce(inst)
        DominatingSet.validate(target)
        tests_run += 1
        if sat_solve(inst) == ds_solve(target):
            tests_passed += 1
        else:
            failures.append((inst, target, sat_solve(inst), ds_solve(target)))

    print(f"tests_run={tests_run} tests_passed={tests_passed}")
    if failures:
        print("FAILURES:")
        for f in failures[:10]:
            print(f)
    else:
        print("All tests passed.")

    verified = (tests_run == tests_passed) and tests_run > 0
    with open("verdict.json", "w") as fh:
        json.dump(
            {"verified": verified, "tests_run": tests_run, "tests_passed": tests_passed},
            fh,
        )
    print("verdict.json written")


if __name__ == "__main__":
    main()
