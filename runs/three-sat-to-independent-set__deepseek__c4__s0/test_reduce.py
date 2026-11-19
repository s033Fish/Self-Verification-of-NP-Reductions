"""Compare brute-force answers on small 3-SAT instances and their reductions."""

from __future__ import annotations

import itertools
import random

from problems import ThreeSat, IndependentSet
from reduce import reduce
from solvers import solve_three_sat, solve_independent_set

tests_run = 0
tests_passed = 0


def check(instance: dict) -> None:
    global tests_run, tests_passed
    tests_run += 1
    ThreeSat.validate(instance)
    reduced = reduce(instance)
    IndependentSet.validate(reduced)
    expected = solve_three_sat(instance)
    got = solve_independent_set(reduced)
    assert got == expected, (
        f"mismatch: instance={instance} reduced={reduced} "
        f"expected={expected} got={got}"
    )
    tests_passed += 1


def all_clauses(m: int):
    out = []
    for vars_ in itertools.combinations(range(1, m + 1), 3):
        for signs in itertools.product([1, -1], repeat=3):
            out.append([s * v for s, v in zip(signs, vars_)])
    return out


def main() -> None:
    # no-clause edge cases
    for m in range(0, 7):
        check({"num_vars": m, "clauses": []})

    # exhaustive: m in 0..4, up to 3 clauses (with repetition)
    for m in range(0, 5):
        clauses = all_clauses(m)
        for r in range(1, 4):
            for combo in itertools.combinations_with_replacement(clauses, r):
                check({"num_vars": m, "clauses": [list(c) for c in combo]})

    # random formulas, including duplicate clauses and unused variables
    rng = random.Random(12345)
    for _ in range(4000):
        m = rng.randint(0, 6)
        clauses = all_clauses(m)
        if not clauses:
            check({"num_vars": m, "clauses": []})
            continue
        r = rng.randint(0, 6)
        chosen = [list(rng.choice(clauses)) for _ in range(r)]
        rng.shuffle(chosen)
        check({"num_vars": m, "clauses": chosen})

    # literal order inside a clause must not matter
    check({"num_vars": 3, "clauses": [[1, 2, 3], [3, -1, 2], [-2, 3, 1]]})

    print(f"tests_run={tests_run} tests_passed={tests_passed}")
    assert tests_run == tests_passed


if __name__ == "__main__":
    main()
