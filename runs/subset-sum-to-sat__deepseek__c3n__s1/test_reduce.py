"""Tests for the Subset Sum -> SAT reduction.

Brute-force solvers are written directly from the problem definitions in
problems.py (which provides no solvers), then compared on many small
instances against the reduction's output.
"""

from __future__ import annotations

import itertools
import random

from problems import Sat, SubsetSum
from reduce import reduce


# ----------------------------------------------------------------------
# Solvers


def solve_subset_sum(instance: dict) -> bool:
    """Yes iff some sub-list sums to exactly target (exact DP)."""
    numbers = instance["numbers"]
    target = instance["target"]
    if target < 0:
        return False
    reachable = {0}
    for number in numbers:
        reachable |= {s + number for s in reachable}
    return target in reachable


def _brute_sat(num_vars: int, clauses: list) -> bool:
    for bits in itertools.product([False, True], repeat=num_vars):
        ok = True
        for clause in clauses:
            if not any(
                (bits[abs(lit) - 1] if lit > 0 else not bits[abs(lit) - 1])
                for lit in clause
            ):
                ok = False
                break
        if ok:
            return True
    return False


def _dpll_sat(num_vars: int, clauses: list) -> bool:
    """Exact DPLL with unit propagation and pure-literal elimination."""
    # Clauses as frozensets of literals.
    work = [frozenset(c) for c in clauses]
    # Empty clause => unsat.
    if any(len(c) == 0 for c in work):
        return False

    def simplify(clauses, literal):
        result = []
        for c in clauses:
            if literal in c:
                continue  # clause satisfied
            if -literal in c:
                c = c - {-literal}
                if not c:
                    return None  # conflict
            result.append(c)
        return result

    def dpll(clauses):
        if not clauses:
            return True
        # Unit propagation.
        while True:
            unit = None
            for c in clauses:
                if len(c) == 1:
                    unit = next(iter(c))
                    break
            if unit is None:
                break
            clauses = simplify(clauses, unit)
            if clauses is None:
                return False
            if not clauses:
                return True
        # Pure literal elimination.
        all_lits = set()
        for c in clauses:
            all_lits |= c
        pure = None
        for lit in all_lits:
            if -lit not in all_lits:
                pure = lit
                break
        if pure is not None:
            clauses = simplify(clauses, pure)
            if clauses is None:
                return False
            return dpll(clauses)
        # Branch on the literal in the shortest clause.
        shortest = min(clauses, key=len)
        lit = next(iter(shortest))
        for choice in (lit, -lit):
            reduced = simplify(clauses, choice)
            if reduced is not None and dpll(reduced):
                return True
        return False

    return dpll(work)


def solve_sat(instance: dict) -> bool:
    """Yes iff some assignment satisfies every clause."""
    num_vars = instance["num_vars"]
    clauses = instance["clauses"]
    if num_vars <= 16:
        return _brute_sat(num_vars, clauses)
    return _dpll_sat(num_vars, clauses)


# ----------------------------------------------------------------------
# Tests


def check(instance: dict) -> None:
    SubsetSum.validate(instance)
    reduced = reduce(instance)
    Sat.validate(reduced)
    expected = solve_subset_sum(instance)
    got = solve_sat(reduced)
    assert got == expected, (
        f"mismatch on {instance}: expected {expected}, got {got}\n"
        f"reduction: {reduced}"
    )


def test_edge_cases() -> int:
    cases = [
        {"numbers": [], "target": 0},
        {"numbers": [], "target": 1},
        {"numbers": [], "target": -5},
        {"numbers": [5], "target": 0},
        {"numbers": [5], "target": 5},
        {"numbers": [5], "target": 4},
        {"numbers": [0, 0, 0], "target": 0},
        {"numbers": [0, 0, 0], "target": 1},
        {"numbers": [1, 2, 3], "target": 6},
        {"numbers": [1, 2, 3], "target": 7},
        {"numbers": [2, 4, 6], "target": 5},
        {"numbers": [1, 1, 1, 1], "target": 2},
        {"numbers": [1, 1, 1, 1], "target": 3},
        {"numbers": [10**18, 10**18 + 1], "target": 2 * 10**18 + 1},
        {"numbers": [10**18, 10**18 + 1], "target": 10**18},
        {"numbers": [10**18, 10**18 + 1], "target": 1},
        {"numbers": [0], "target": -1},
        {"numbers": [3, 3, 3], "target": 9},
        {"numbers": [3, 3, 3], "target": 8},
        {"numbers": [10**30, 1], "target": 10**30 + 1},
        {"numbers": [10**30, 1], "target": 10**30},
        {"numbers": [10**30, 1], "target": 2},
    ]
    for case in cases:
        check(case)
    return len(cases)


def test_random() -> int:
    rng = random.Random(12345)
    count = 0
    for _ in range(3000):
        n = rng.randint(0, 8)
        numbers = [rng.randint(0, 12) for _ in range(n)]
        target = rng.randint(-2, sum(numbers) + 2)
        check({"numbers": numbers, "target": target})
        count += 1
    for _ in range(500):
        n = rng.randint(0, 6)
        numbers = [rng.randint(0, 10**6) for _ in range(n)]
        target = rng.choice([
            rng.randint(-1, sum(numbers) + 1),
            sum(numbers),
            sum(numbers) // 2,
        ])
        check({"numbers": numbers, "target": target})
        count += 1
    for _ in range(500):
        n = rng.randint(0, 9)
        numbers = [rng.choice([0, 1, 2, 5]) for _ in range(n)]
        target = rng.randint(-1, sum(numbers) + 1)
        check({"numbers": numbers, "target": target})
        count += 1
    return count


def main() -> None:
    tests_run = 0
    tests_passed = 0
    failures = []

    for name, fn in [("edge_cases", test_edge_cases), ("random", test_random)]:
        try:
            n = fn()
            tests_run += n
            tests_passed += n
            print(f"PASS {name}: {n} cases")
        except AssertionError as exc:
            tests_run += 1
            failures.append((name, exc))
            print(f"FAIL {name}: {exc}")

    print(f"tests_run={tests_run} tests_passed={tests_passed}")
    if failures:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
