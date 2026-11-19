"""Independent verification of reduce.py: 1-in-3-SAT -> Exact Cover.

We implement our own brute-force solvers from the problem definitions and
compare source answer with target answer on many small instances, including
exhaustive enumeration and edge cases.
"""

from __future__ import annotations

import itertools
import random
import sys
from functools import lru_cache

import problems
from reduce import reduce


# ----------------------------------------------------------------------
# Brute-force solver for SOURCE = OneInThreeSat
# ----------------------------------------------------------------------

def one_in_three_sat_bruteforce(instance: dict) -> bool:
    num_vars = instance["num_vars"]
    clauses = instance["clauses"]
    # Try every assignment of variables 1..num_vars.
    for bits in itertools.product((False, True), repeat=num_vars):
        # bits[i] is the value of variable i+1
        ok = True
        for clause in clauses:
            true_count = sum(1 for v in clause if bits[v - 1])
            if true_count != 1:
                ok = False
                break
        if ok:
            return True
    return False


# ----------------------------------------------------------------------
# Brute-force solver for TARGET = ExactCover
# ----------------------------------------------------------------------

def exact_cover_bruteforce(instance: dict) -> bool:
    u = instance["universe_size"]
    masks = []
    for subset in instance["sets"]:
        m = 0
        for e in subset:
            m |= 1 << e
        masks.append(m)
    # Deduplicate; empty sets never matter.
    masks = sorted({m for m in masks if m != 0})
    target = (1 << u) - 1

    @lru_cache(maxsize=None)
    def rec(covered: int) -> bool:
        if covered == target:
            return True
        # Lowest uncovered element; the set covering it must contain it.
        uncovered = target & ~covered
        b = uncovered & (-uncovered)
        for m in masks:
            if (m & b) and not (m & covered):
                if rec(covered | m):
                    return True
        return False

    return rec(0)


# ----------------------------------------------------------------------
# Instance generators
# ----------------------------------------------------------------------

def all_clauses(num_vars: int) -> list[tuple[int, int, int]]:
    return list(itertools.combinations(range(1, num_vars + 1), 3))


def make_instance(num_vars: int, clauses) -> dict:
    return {"num_vars": num_vars, "clauses": [list(c) for c in clauses]}


def random_instance(rng: random.Random, max_vars: int, max_clauses: int) -> dict:
    num_vars = rng.randint(0, max_vars)
    possible = all_clauses(num_vars)
    if not possible:
        return make_instance(num_vars, [])
    n = rng.randint(0, max_clauses)
    clauses = [rng.choice(possible) for _ in range(n)]
    return make_instance(num_vars, clauses)


# ----------------------------------------------------------------------
# Test driver
# ----------------------------------------------------------------------

tests_run = 0
tests_passed = 0
failures: list[str] = []


def check(instance: dict, label: str) -> None:
    global tests_run, tests_passed
    tests_run += 1
    try:
        # Validate the source instance per the definitions.
        problems.OneInThreeSat.validate(instance)
        src = one_in_three_sat_bruteforce(instance)
        reduced = reduce(instance)
        # The reduction must produce a well-formed target instance.
        problems.ExactCover.validate(reduced)
        tgt = exact_cover_bruteforce(reduced)
        if src != tgt:
            failures.append(
                f"{label}: mismatch src={src} tgt={tgt}\n  instance={instance}\n  reduced={reduced}"
            )
        else:
            tests_passed += 1
    except Exception as exc:  # noqa: BLE001
        failures.append(f"{label}: exception {type(exc).__name__}: {exc}\n  instance={instance}")


def main() -> int:
    # 1. Explicit edge cases.
    check(make_instance(0, []), "edge: m=0 no clauses")
    check(make_instance(5, []), "edge: m=5 no clauses")
    check(make_instance(3, [(1, 2, 3)]), "edge: single clause")
    check(make_instance(3, [(1, 2, 3), (1, 2, 3)]), "edge: duplicate clause")
    check(make_instance(3, [(1, 2, 3), (1, 2, 3), (1, 2, 3)]), "edge: triplicate clause")
    # Variable not appearing in any clause.
    check(make_instance(4, [(1, 2, 3)]), "edge: unused variable")

    # 2. Exhaustive over all subsets of distinct clauses for m = 0..5.
    for m in range(0, 6):
        possible = all_clauses(m)
        for r in range(len(possible) + 1):
            for subset in itertools.combinations(possible, r):
                check(make_instance(m, subset), f"exhaustive m={m} subset={subset}")

    # 3. Exhaustive with clause multiplicities for m = 3 (small).
    possible3 = all_clauses(3)
    for counts in itertools.product(range(3), repeat=len(possible3)):
        clauses = []
        for c, k in zip(possible3, counts):
            clauses.extend([c] * k)
        check(make_instance(3, clauses), f"multiplicity m=3 counts={counts}")

    # 4. Random instances, including duplicates and unused variables.
    rng = random.Random(20240607)
    for i in range(4000):
        inst = random_instance(rng, max_vars=6, max_clauses=6)
        check(inst, f"random #{i}")


    # 5. Larger random instances (more vars/clauses), still brute-forceable.
    rng2 = random.Random(987654321)
    for i in range(3000):
        m = rng2.randint(0, 8)
        possible = all_clauses(m)
        if not possible:
            inst = make_instance(m, [])
        else:
            k = rng2.randint(0, 12)
            inst = make_instance(m, [rng2.choice(possible) for _ in range(k)])
        check(inst, f"large-random #{i}")

    print(f"tests_run={tests_run}")
    print(f"tests_passed={tests_passed}")
    if failures:
        print(f"FAILURES ({len(failures)}):")
        for f in failures[:20]:
            print(f)
        return 1
    print("ALL TESTS PASSED")
    return 0


if __name__ == "__main__":
    sys.exit(main())
