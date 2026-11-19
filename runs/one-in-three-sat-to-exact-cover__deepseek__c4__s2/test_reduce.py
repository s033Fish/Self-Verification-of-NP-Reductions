"""Brute-force solvers and randomized tests for the 1-in-3-SAT -> Exact Cover reduction."""

from __future__ import annotations

import itertools
import random

from problems import SOURCE, TARGET
from reduce import reduce


# ----------------------------------------------------------------------
# Brute-force solvers written from the problem definitions.

def solve_one_in_three_sat(instance: dict) -> bool:
    SOURCE.validate(instance)
    m = instance["num_vars"]
    clauses = instance["clauses"]
    for bits in itertools.product([False, True], repeat=m):
        ok = True
        for clause in clauses:
            if sum(1 for v in clause if bits[v - 1]) != 1:
                ok = False
                break
        if ok:
            return True
    return True if not clauses else False


def solve_exact_cover(instance: dict) -> bool:
    TARGET.validate(instance)
    u = instance["universe_size"]
    sets = instance["sets"]
    full = (1 << u) - 1
    # DP over reachable covered masks (only disjoint unions arise naturally).
    reachable = {0}
    for s in sets:
        mask = 0
        for e in s:
            mask |= 1 << e
        if mask == 0:
            continue
        new = set(reachable)
        for cur in reachable:
            if cur & mask == 0:
                new.add(cur | mask)
        reachable = new
    return full in reachable


# ----------------------------------------------------------------------
# Tests

def check(instance: dict) -> bool:
    """Return True if reduction preserves the answer for this instance."""
    src = solve_one_in_three_sat(instance)
    red = reduce(instance)
    tgt = solve_exact_cover(red)
    return src == tgt


def random_instance(rng: random.Random) -> dict:
    m = rng.randint(0, 6)
    if m < 3:
        n = 0
    else:
        n = rng.randint(0, 6)
    clauses = []
    for _ in range(n):
        clause = rng.sample(range(1, m + 1), 3)
        clauses.append(clause)
    return {"num_vars": m, "clauses": clauses}


def main() -> None:
    tests_run = 0
    tests_passed = 0

    def run(instance, label):
        nonlocal tests_run, tests_passed
        tests_run += 1
        try:
            good = check(instance)
        except Exception as exc:  # noqa: BLE001
            print(f"FAIL {label}: exception {exc!r}")
            return
        if good:
            tests_passed += 1
        else:
            print(f"FAIL {label}: {instance}")
            print("  reduced:", reduce(instance))
            print("  src:", solve_one_in_three_sat(instance),
                  "tgt:", solve_exact_cover(reduce(instance)))

    # Hand-picked edge cases.
    run({"num_vars": 0, "clauses": []}, "m=0 no clauses")
    run({"num_vars": 5, "clauses": []}, "no clauses")
    run({"num_vars": 3, "clauses": [[1, 2, 3]]}, "single clause")
    run({"num_vars": 3, "clauses": [[1, 2, 3], [1, 2, 3]]}, "duplicate clause")
    run({"num_vars": 4, "clauses": [[1, 2, 3], [2, 3, 4], [1, 3, 4]]}, "chain")
    # Unsatisfiable-ish: variables 1,2,3 all forced patterns.
    run({"num_vars": 3, "clauses": [[1, 2, 3], [1, 2, 3], [1, 2, 3]]}, "triple dup")
    # Variables not appearing anywhere.
    run({"num_vars": 6, "clauses": [[4, 5, 6]]}, "unused vars")

    # Exhaustive small instances.
    for m in range(0, 5):
        vars_ = list(range(1, m + 1))
        if m < 3:
            clause_pool = []
        else:
            clause_pool = [list(c) for c in itertools.combinations(vars_, 3)]
        # all subsets of clause pool up to size 3, with repetition allowed via product
        for r in range(0, 4):
            for combo in itertools.combinations_with_replacement(clause_pool, r):
                run({"num_vars": m, "clauses": [list(c) for c in combo]},
                    f"exhaustive m={m} r={r}")

    # Randomized tests.
    rng = random.Random(12345)
    for _ in range(4000):
        run(random_instance(rng), "random")

    print(f"tests_run={tests_run} tests_passed={tests_passed}")
    assert tests_run == tests_passed, "some tests failed"

    import json
    with open("verdict.json", "w") as fh:
        json.dump({"verified": True, "tests_run": tests_run,
                   "tests_passed": tests_passed}, fh)
    print("verdict.json written")


if __name__ == "__main__":
    main()

def stress_extra() -> None:
    import random
    from reduce import reduce as _reduce
    rng = random.Random(999)
    runs = 0
    for _ in range(300):
        m = rng.randint(3, 8)
        n = rng.randint(0, 10)
        clauses = [rng.sample(range(1, m + 1), 3) for _ in range(n)]
        inst = {"num_vars": m, "clauses": clauses}
        assert solve_one_in_three_sat(inst) == solve_exact_cover(_reduce(inst)), inst
        runs += 1
    # large instance: check polynomial-size output & validity
    m = 2000
    clauses = [[rng.randint(1, m), rng.randint(1, m), rng.randint(1, m)] for _ in range(3000)]
    for c in clauses:
        while len(set(c)) < 3:
            c[:] = [rng.randint(1, m), rng.randint(1, m), rng.randint(1, m)]
    inst = {"num_vars": m, "clauses": clauses}
    red = _reduce(inst)
    TARGET.validate(red)
    assert red["universe_size"] == m + len(clauses)
    print(f"stress_extra ok ({runs} extra + 1 large)")


if __name__ == "__main__":
    main()
    stress_extra()
