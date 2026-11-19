"""Brute-force solvers and tests for the 1-in-3-SAT -> Exact Cover reduction."""

from __future__ import annotations

import itertools
import random

from problems import OneInThreeSat, ExactCover
from reduce import reduce


# ----------------------------------------------------------------------
# Brute-force solvers written directly from the problem definitions.
# ----------------------------------------------------------------------

def solve_one_in_three(instance) -> bool:
    num_vars = instance["num_vars"]
    clauses = instance["clauses"]
    for bits in itertools.product([False, True], repeat=num_vars):
        ok = True
        for clause in clauses:
            true_count = sum(1 for lit in clause if bits[lit - 1])
            if true_count != 1:
                ok = False
                break
        if ok:
            return True
    return False


def solve_exact_cover(instance) -> bool:
    universe_size = instance["universe_size"]
    sets = [frozenset(s) for s in instance["sets"]]

    full = (1 << universe_size) - 1

    # Index sets by element for faster search.
    by_elem = [[] for _ in range(universe_size)]
    for idx, s in enumerate(sets):
        for e in s:
            by_elem[e].append(idx)

    def rec(covered: int) -> bool:
        if covered == full:
            return True
        # smallest uncovered element
        e = 0
        while (covered >> e) & 1:
            e += 1
        for idx in by_elem[e]:
            s = sets[idx]
            if covered & sum(1 << x for x in s):
                continue
            new_covered = covered
            for x in s:
                new_covered |= 1 << x
            if rec(new_covered):
                return True
        return False

    return rec(0)


# ----------------------------------------------------------------------
# Tests
# ----------------------------------------------------------------------

TESTS_RUN = 0
TESTS_PASSED = 0


def check(source_instance, label=""):
    global TESTS_RUN, TESTS_PASSED
    TESTS_RUN += 1
    OneInThreeSat.validate(source_instance)
    target = reduce(source_instance)
    ExactCover.validate(target)
    expected = solve_one_in_three(source_instance)
    got = solve_exact_cover(target)
    if expected != got:
        print(f"FAIL {label}: source={source_instance}")
        print(f"  expected={expected} got={got} target={target}")
        return False
    TESTS_PASSED += 1
    return True


def main():
    random.seed(12345)

    # Edge cases: no clauses, various m.
    for m in range(0, 9):
        check({"num_vars": m, "clauses": []}, f"no-clauses m={m}")

    # All clauses over small variable sets, exhaustive for m=3,4.
    for m in (3, 4):
        all_clauses = list(itertools.combinations(range(1, m + 1), 3))
        # random subsets of clauses
        for _ in range(300):
            k = random.randint(1, len(all_clauses))
            clauses = [list(c) for c in random.sample(all_clauses, k)]
            # sometimes duplicate a clause
            if random.random() < 0.3 and clauses:
                clauses.append(list(random.choice(clauses)))
            random.shuffle(clauses)
            check({"num_vars": m, "clauses": clauses}, f"m={m}")

    # Exhaustive over all clause multisets for m=3 (up to 2 clauses).
    all_clauses = list(itertools.combinations(range(1, 4), 3))
    for k in range(0, 4):
        for combo in itertools.product(all_clauses, repeat=k):
            clauses = [list(c) for c in combo]
            check({"num_vars": 3, "clauses": clauses}, "exhaustive m=3")

    # Random larger instances.
    for _ in range(400):
        m = random.randint(3, 7)
        t = random.randint(0, 12)
        clauses = []
        for _ in range(t):
            clauses.append(random.sample(range(1, m + 1), 3))
        check({"num_vars": m, "clauses": clauses}, "random")

    # Some structured satisfiable / unsatisfiable instances.
    # Every clause true exactly once: all vars true? then 3 true -> no.
    # Use partition-like: vars 1,2,3 with clauses (1,2,3) twice -> no
    # (exactly one true each time is possible: set 1 true, 2,3 false -> yes).
    check({"num_vars": 3, "clauses": [[1, 2, 3], [1, 2, 3]]}, "dup clause")
    # Two clauses sharing vars requiring conflict.
    check({"num_vars": 4, "clauses": [[1, 2, 3], [1, 2, 4], [1, 3, 4]]}, "shared")

    print(f"tests_run={TESTS_RUN} tests_passed={TESTS_PASSED}")
    assert TESTS_RUN == TESTS_PASSED, "some tests failed"


if __name__ == "__main__":
    main()
