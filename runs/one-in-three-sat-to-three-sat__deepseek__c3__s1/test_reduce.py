"""Tests for the 1-in-3-SAT -> 3-SAT reduction in reduce.py."""

from __future__ import annotations

import random
from itertools import combinations

from problems import SOURCE, TARGET
from reduce import reduce

tests_run = 0
tests_passed = 0


def check(instance):
    global tests_run, tests_passed
    tests_run += 1
    SOURCE.validate(instance)
    reduced = reduce(instance)
    TARGET.validate(reduced)  # must be a well-formed 3-SAT instance
    expected = SOURCE.is_yes(instance)
    got = TARGET.is_yes(reduced)
    if expected != got:
        raise AssertionError(
            f"MISMATCH: source={instance} expected={expected} "
            f"reduced={reduced} got={got}"
        )
    tests_passed += 1


def exhaustive(num_vars):
    """Every subset of the distinct positive 3-clauses on num_vars vars."""
    all_clauses = [list(c) for c in combinations(range(1, num_vars + 1), 3)]
    n = len(all_clauses)
    for mask in range(1 << n):
        clauses = [list(all_clauses[i]) for i in range(n) if mask >> i & 1]
        check({"num_vars": num_vars, "clauses": clauses})


def main():
    # 1. Exhaustive small instances via the problem's own enumerator.
    count = 0
    for instance in SOURCE.enumerate_instances(3):
        check(instance)
        count += 1
    print(f"enumerator scale<=3: {count} instances")

    # 2. Fully exhaustive over all clause subsets for 4 and 5 variables.
    exhaustive(4)
    print("exhaustive num_vars=4 done")
    exhaustive(5)
    print("exhaustive num_vars=5 done")

    # 3. Edge cases.
    check({"num_vars": 0, "clauses": []})
    check({"num_vars": 1, "clauses": []})
    check({"num_vars": 5, "clauses": []})
    check({"num_vars": 6, "clauses": [[1, 2, 3]]})          # unused variables
    check({"num_vars": 3, "clauses": [[1, 2, 3], [1, 2, 3]]})  # duplicates
    check({"num_vars": 4, "clauses": [[1, 2, 3], [1, 2, 3], [2, 3, 4]]})

    # 4. Random instances across scales, including duplicates.
    rng = random.Random(12345)
    for scale in range(0, 10):
        for _ in range(300):
            check(SOURCE.random_instance(rng, scale))
    print("random instances done")

    # 5. Random formulas on 6-7 vars sampled from the full clause set.
    for num_vars in (6, 7):
        all_clauses = [list(c) for c in combinations(range(1, num_vars + 1), 3)]
        for _ in range(2000):
            k = rng.randint(0, len(all_clauses))
            clauses = [list(all_clauses[i]) for i in rng.sample(range(len(all_clauses)), k)]
            if clauses and rng.random() < 0.3:
                clauses.append(list(rng.choice(clauses)))
            check({"num_vars": num_vars, "clauses": clauses})
    print("sampled 6-7 var instances done")

    print(f"RESULT tests_run={tests_run} tests_passed={tests_passed}")


if __name__ == "__main__":
    main()
