"""Tests comparing brute-force solvers on source instances and their reductions."""
import itertools
import random

import problems
import reduce as reduce_mod
import solvers

SAT = problems.SOURCE
COL = problems.TARGET


def check(instance):
    SAT.validate(instance)
    out = reduce_mod.reduce(instance)
    COL.validate(out)
    a = solvers.sat_solve(instance)
    b = solvers.color_solve(out)
    assert a == b, (instance, out, a, b)
    return a


def random_instance(rng, max_vars=4, max_clauses=4):
    m = rng.randint(0, max_vars)
    if m < 3:
        clauses = []
    else:
        nclauses = rng.randint(0, max_clauses)
        clauses = []
        for _ in range(nclauses):
            vs = rng.sample(range(1, m + 1), 3)
            clause = [v if rng.random() < 0.5 else -v for v in vs]
            clauses.append(clause)
    return {"num_vars": m, "clauses": clauses}


def main():
    tests = 0
    passed = 0

    # edge cases
    edge = [
        {"num_vars": 0, "clauses": []},
        {"num_vars": 5, "clauses": []},
        {"num_vars": 3, "clauses": [[1, 2, 3]]},
        {"num_vars": 3, "clauses": [[1, 2, 3], [1, 2, 3]]},
        {"num_vars": 3, "clauses": [[1, 2, 3], [-1, -2, -3]]},
        {"num_vars": 3, "clauses": [[1, 2, 3], [-1, -2, -3], [1, -2, 3], [-1, 2, -3]]},
        {"num_vars": 3, "clauses": [[1, 2, 3], [-1, -2, 3], [1, -2, -3], [-1, 2, -3],
                                     [1, 2, -3], [-1, -2, -3], [1, -2, 3], [-1, 2, 3]]},
    ]
    for inst in edge:
        tests += 1
        check(inst)
        passed += 1

    # exhaustive over all 3-var formulas with up to 2 clauses (small)
    rng = random.Random(12345)
    for _ in range(3000):
        inst = random_instance(rng, max_vars=4, max_clauses=4)
        tests += 1
        check(inst)
        passed += 1

    # exhaustive: all single clauses over 3 vars
    lits = [1, -1, 2, -2, 3, -3]
    for combo in itertools.combinations(lits, 3):
        if len({abs(x) for x in combo}) == 3:
            inst = {"num_vars": 3, "clauses": [list(combo)]}
            tests += 1
            check(inst)
            passed += 1

    # all pairs of clauses over 3 vars
    all_clauses = []
    for combo in itertools.combinations(lits, 3):
        if len({abs(x) for x in combo}) == 3:
            all_clauses.append(list(combo))
    for c1 in all_clauses:
        for c2 in all_clauses:
            inst = {"num_vars": 3, "clauses": [c1, c2]}
            tests += 1
            check(inst)
            passed += 1

    print(f"tests_run={tests} tests_passed={passed}")
    assert tests == passed
    return tests, passed


if __name__ == "__main__":
    main()
