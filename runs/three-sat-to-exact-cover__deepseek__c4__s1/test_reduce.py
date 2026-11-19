"""Brute-force solvers and randomized/exhaustive tests for the 3-SAT -> Exact Cover reduction."""

import itertools
import random
import sys

from problems import ThreeSat, ExactCover
from reduce import reduce


# ---------------------------------------------------------------- solvers

def solve_three_sat(instance):
    m = instance["num_vars"]
    clauses = instance["clauses"]
    for bits in itertools.product([False, True], repeat=m):
        ok = True
        for clause in clauses:
            if not any((bits[abs(l) - 1] if l > 0 else not bits[abs(l) - 1]) for l in clause):
                ok = False
                break
        if ok:
            return True
    return False


def solve_exact_cover(instance):
    u = instance["universe_size"]
    full = frozenset(range(u))
    sets = [frozenset(s) for s in instance["sets"]]
    memo = {}

    def rec(covered):
        if covered == full:
            return True
        if covered in memo:
            return memo[covered]
        remaining = full - covered
        e = min(remaining)
        result = False
        for s in sets:
            if e in s and not (s & covered):
                if rec(covered | s):
                    result = True
                    break
        memo[covered] = result
        return result

    return rec(frozenset())


# ---------------------------------------------------------------- generators

def random_three_sat(rng, max_vars=5, max_clauses=6):
    m = rng.randint(0, max_vars)
    if m < 3:
        k = 0
    else:
        k = rng.randint(0, max_clauses)
    clauses = []
    for _ in range(k):
        variables = rng.sample(range(1, m + 1), 3)
        clause = [v if rng.random() < 0.5 else -v for v in variables]
        clauses.append(clause)
    return {"num_vars": m, "clauses": clauses}


def all_clauses_for(m):
    out = []
    for variables in itertools.combinations(range(1, m + 1), 3):
        for signs in itertools.product([1, -1], repeat=3):
            out.append([s * v for s, v in zip(signs, variables)])
    return out


def check(inst, tests):
    ThreeSat.validate(inst)
    reduced = reduce(inst)
    ExactCover.validate(reduced)
    expected = solve_three_sat(inst)
    got = solve_exact_cover(reduced)
    tests[0] += 1
    if expected == got:
        tests[1] += 1
    else:
        print("MISMATCH")
        print("source:", inst)
        print("expected:", expected, "got:", got)
        print("reduced:", reduced)
        return False
    return True


def main():
    rng = random.Random(12345)
    tests = [0, 0]

    # Edge cases.
    fixed = [
        {"num_vars": 0, "clauses": []},
        {"num_vars": 1, "clauses": []},
        {"num_vars": 3, "clauses": []},
        {"num_vars": 3, "clauses": [[1, 2, 3]]},
        {"num_vars": 3, "clauses": [[-1, -2, -3]]},
        {"num_vars": 3, "clauses": [[1, 2, 3], [-1, -2, -3]]},
        {"num_vars": 3, "clauses": [[1, 2, 3], [1, 2, 3]]},          # duplicate clause
        {"num_vars": 4, "clauses": [[1, 2, 3], [-1, 2, 4], [1, -2, -3]]},
        {"num_vars": 5, "clauses": [[1, 2, 3], [-1, -2, -3], [4, 5, -1]]},
    ]
    for inst in fixed:
        if not check(inst, tests):
            return 1

    # Exhaustive: every subset of the 8 clauses over variables {1,2,3}.
    base = all_clauses_for(3)
    for size in range(0, len(base) + 1):
        for subset in itertools.combinations(range(len(base)), size):
            inst = {"num_vars": 3, "clauses": [base[i] for i in subset]}
            if not check(inst, tests):
                return 1

    # Exhaustive-ish: all single clauses and pairs over variables {1,2,3,4}.
    base4 = all_clauses_for(4)
    for c in base4:
        if not check({"num_vars": 4, "clauses": [c]}, tests):
            return 1
    for _ in range(300):
        pair = rng.sample(base4, 2)
        if not check({"num_vars": 4, "clauses": pair}, tests):
            return 1

    # Randomized.
    for _ in range(600):
        inst = random_three_sat(rng)
        if not check(inst, tests):
            return 1

    # Larger random instances (still brute-forceable).
    for _ in range(60):
        inst = random_three_sat(rng, max_vars=7, max_clauses=10)
        if not check(inst, tests):
            return 1

    print(f"tests_run={tests[0]} tests_passed={tests[1]}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
