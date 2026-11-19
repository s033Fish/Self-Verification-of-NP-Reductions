import itertools
import random

import problems
from reduce import reduce


def sat_solve(inst):
    """Brute-force 3-SAT solver."""
    m = inst["num_vars"]
    clauses = inst["clauses"]
    for mask in range(1 << m):
        ok = True
        for clause in clauses:
            if not any(
                ((mask >> (abs(lit) - 1)) & 1) == (1 if lit > 0 else 0)
                for lit in clause
            ):
                ok = False
                break
        if ok:
            return True
    return False


def exact_cover_solve(inst):
    """Backtracking Exact Cover solver."""
    u = inst["universe_size"]
    sets = [frozenset(s) for s in inst["sets"]]
    full = frozenset(range(u))

    def rec(covered):
        if covered == full:
            return True
        # first uncovered element
        e = None
        for x in range(u):
            if x not in covered:
                e = x
                break
        for s in sets:
            if e in s and not (s & covered):
                if rec(covered | s):
                    return True
        return False

    return rec(frozenset())


def check(inst):
    problems.ThreeSat.validate(inst)
    red = reduce(inst)
    problems.ExactCover.validate(red)
    a = sat_solve(inst)
    b = exact_cover_solve(red)
    assert a == b, (inst, red, a, b)
    return 1


def random_instance(rng, max_m=5, max_nc=4):
    m = rng.randint(0, max_m)
    nc = rng.randint(0, max_nc)
    clauses = []
    for _ in range(nc):
        if m < 3:
            break
        vs = rng.sample(range(1, m + 1), 3)
        clause = [v if rng.random() < 0.5 else -v for v in vs]
        clauses.append(clause)
    return {"num_vars": m, "clauses": clauses}


def main():
    tests = 0
    rng = random.Random(12345)

    # Explicit edge cases.
    edge = [
        {"num_vars": 0, "clauses": []},
        {"num_vars": 5, "clauses": []},
        {"num_vars": 3, "clauses": [[1, 2, 3]]},
        {"num_vars": 3, "clauses": [[-1, -2, -3]]},
        {"num_vars": 3, "clauses": [[1, 2, 3], [1, 2, 3]]},
        {"num_vars": 3, "clauses": [[1, -1, 2]]},  # invalid, skipped below
    ]
    for inst in edge:
        try:
            problems.ThreeSat.validate(inst)
        except problems.InvalidInstance:
            continue
        tests += check(inst)

    # Exhaustive small enumeration: m in 0..3, all clauses over distinct vars.
    for m in range(0, 4):
        possible = []
        if m >= 3:
            for vs in itertools.combinations(range(1, m + 1), 3):
                for signs in itertools.product([1, -1], repeat=3):
                    possible.append([s * v for s, v in zip(signs, vs)])
        # all subsets of up to 3 clauses
        for r in range(0, min(3, len(possible)) + 1):
            for combo in itertools.combinations(possible, r):
                inst = {"num_vars": m, "clauses": [list(c) for c in combo]}
                tests += check(inst)

    # Random tests.
    for _ in range(400):
        inst = random_instance(rng)
        tests += check(inst)

    for _ in range(150):
        inst = random_instance(rng, max_m=8, max_nc=6)
        tests += check(inst)

    print(f"tests_run={tests} tests_passed={tests}")
    return tests


if __name__ == "__main__":
    main()
