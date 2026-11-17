"""Tests for the 1-in-3-SAT -> 3-SAT reduction in reduce.py.

problems.py provides no solvers, so this file implements:

  * brute-force solvers for both problems, written directly from the
    definitions in problems.py, and
  * a small DPLL solver so that larger instances (whose reductions contain
    many auxiliary variables) can still be checked.

It then compares the answers on exhaustive small source instances, random
instances, targeted edge cases, and checks the polynomial size growth of
the reduction.
"""

from __future__ import annotations

import itertools
import random

from problems import SOURCE, TARGET
from reduce import reduce


# ----------------------------------------------------------------------
# Brute-force solvers
# ----------------------------------------------------------------------


def solve_one_in_three(instance: dict) -> bool:
    """True iff some assignment makes exactly one var true per clause."""
    SOURCE.validate(instance)
    m = instance["num_vars"]
    clauses = instance["clauses"]
    for bits in itertools.product([False, True], repeat=m):
        ok = True
        for a, b, c in clauses:
            true_count = bits[a - 1] + bits[b - 1] + bits[c - 1]
            if true_count != 1:
                ok = False
                break
        if ok:
            return True
    return False


def solve_three_sat(instance: dict) -> bool:
    """True iff some assignment makes every clause have a true literal."""
    TARGET.validate(instance)
    m = instance["num_vars"]
    clauses = instance["clauses"]
    for bits in itertools.product([False, True], repeat=m):
        ok = True
        for clause in clauses:
            if not any(bits[abs(lit) - 1] == (lit > 0) for lit in clause):
                ok = False
                break
        if ok:
            return True
    return False


# ----------------------------------------------------------------------
# DPLL solver (handles the auxiliary variables of the reduction)
# ----------------------------------------------------------------------


def _dpll(clauses, assignment):
    reduced = []
    for clause in clauses:
        sat = False
        lits = []
        for lit in clause:
            v = abs(lit)
            if v in assignment:
                if assignment[v] == (lit > 0):
                    sat = True
                    break
            else:
                lits.append(lit)
        if sat:
            continue
        if not lits:
            return False
        reduced.append(lits)
    if not reduced:
        return True
    for lits in reduced:
        if len(lits) == 1:
            lit = lits[0]
            v = abs(lit)
            val = lit > 0
            if v in assignment and assignment[v] != val:
                return False
            if v not in assignment:
                new = dict(assignment)
                new[v] = val
                return _dpll(clauses, new)
    lits = min(reduced, key=len)
    v = abs(lits[0])
    for val in (True, False):
        new = dict(assignment)
        new[v] = val
        if _dpll(clauses, new):
            return True
    return False


def solve_three_sat_dpll(instance: dict) -> bool:
    TARGET.validate(instance)
    return _dpll(instance["clauses"], {})


def solve_one_in_three_dpll(instance: dict) -> bool:
    """Solve 1-in-3-SAT via the same exact-one encoding, then DPLL."""
    SOURCE.validate(instance)
    m = instance["num_vars"]
    clauses = []
    nxt = m + 1
    for a, b, c in instance["clauses"]:
        clauses.append([a, b, c])
        for u, v in ((a, b), (a, c), (b, c)):
            p = nxt
            nxt += 1
            clauses.append([-u, -v, p])
            clauses.append([-u, -v, -p])
    return _dpll(clauses, {})


# ----------------------------------------------------------------------
# Instance helpers
# ----------------------------------------------------------------------


def all_source_instances(max_vars: int = 5, max_clauses: int = 3):
    """Every 1-in-3-SAT instance with num_vars <= max_vars and few clauses."""
    for m in range(0, max_vars + 1):
        triples = [list(t) for t in itertools.combinations(range(1, m + 1), 3)]
        for k in range(0, max_clauses + 1):
            for combo in itertools.combinations_with_replacement(triples, k):
                yield {"num_vars": m, "clauses": [list(c) for c in combo]}


# ----------------------------------------------------------------------
# Tests
# ----------------------------------------------------------------------


def test_exhaustive_small():
    checked = 0
    for inst in all_source_instances(max_vars=5, max_clauses=3):
        red = reduce(inst)
        TARGET.validate(red)
        assert solve_one_in_three(inst) == solve_three_sat(red), (inst, red)
        checked += 1
    return checked


def test_exhaustive_more_clauses():
    checked = 0
    for inst in all_source_instances(max_vars=4, max_clauses=5):
        red = reduce(inst)
        TARGET.validate(red)
        assert solve_one_in_three(inst) == solve_three_sat(red), (inst, red)
        checked += 1
    return checked


def test_dpll_agrees_with_brute_force():
    checked = 0
    for inst in all_source_instances(max_vars=4, max_clauses=3):
        red = reduce(inst)
        assert solve_one_in_three(inst) == solve_one_in_three_dpll(inst)
        assert solve_three_sat(red) == solve_three_sat_dpll(red)
        checked += 1
    return checked


def test_edge_cases():
    checked = 0
    cases = [
        {"num_vars": 0, "clauses": []},
        {"num_vars": 1, "clauses": []},
        {"num_vars": 7, "clauses": []},
        {"num_vars": 3, "clauses": [[1, 2, 3]]},
        {"num_vars": 3, "clauses": [[1, 2, 3], [1, 2, 3]]},
        {"num_vars": 4, "clauses": [[1, 2, 3], [1, 2, 4]]},
        {"num_vars": 4, "clauses": [[1, 2, 3], [1, 2, 4], [1, 3, 4]]},
        {"num_vars": 4, "clauses": [[1, 2, 3], [1, 2, 4], [1, 3, 4], [2, 3, 4]]},
        {"num_vars": 5, "clauses": [[1, 2, 3], [3, 4, 5]]},
        {"num_vars": 6, "clauses": [[1, 2, 3], [4, 5, 6], [1, 4, 2]]},
    ]
    for inst in cases:
        red = reduce(inst)
        TARGET.validate(red)
        assert solve_one_in_three(inst) == solve_three_sat(red), (inst, red)
        checked += 1
    return checked


def test_no_clause_yes():
    for m in range(0, 9):
        inst = {"num_vars": m, "clauses": []}
        red = reduce(inst)
        assert red["clauses"] == []
        assert solve_one_in_three(inst) is True
        assert solve_three_sat(red) is True


def test_known_unsat():
    inst = {"num_vars": 4, "clauses": [[1, 2, 3], [1, 2, 4], [1, 3, 4], [2, 3, 4]]}
    assert solve_one_in_three(inst) is False
    assert solve_three_sat(reduce(inst)) is False


def test_random_small():
    random.seed(20240607)
    checked = 0
    for _ in range(600):
        m = random.randint(3, 5)
        k = random.randint(0, 3)
        clauses = [sorted(random.sample(range(1, m + 1), 3)) for _ in range(k)]
        inst = {"num_vars": m, "clauses": clauses}
        red = reduce(inst)
        TARGET.validate(red)
        assert solve_one_in_three(inst) == solve_three_sat(red), (inst, red)
        checked += 1
    return checked


def test_random_large_dpll():
    random.seed(31337)
    checked = 0
    for _ in range(1500):
        m = random.randint(3, 12)
        k = random.randint(0, 12)
        clauses = [sorted(random.sample(range(1, m + 1), 3)) for _ in range(k)]
        inst = {"num_vars": m, "clauses": clauses}
        red = reduce(inst)
        TARGET.validate(red)
        assert solve_one_in_three_dpll(inst) == solve_three_sat_dpll(red), (
            inst,
            red,
        )
        checked += 1
    return checked


def test_size_growth():
    # 7 output clauses and 3 fresh variables per source clause.
    for k in (0, 1, 5, 20, 100):
        clauses = [[1, 2, 3]] * k
        inst = {"num_vars": 3, "clauses": clauses}
        red = reduce(inst)
        assert len(red["clauses"]) == 7 * k
        assert red["num_vars"] == 3 + 3 * k


def main():
    tests_run = 0
    tests_passed = 0

    checks = [
        ("exhaustive_small", test_exhaustive_small),
        ("exhaustive_more_clauses", test_exhaustive_more_clauses),
        ("dpll_agrees_with_brute_force", test_dpll_agrees_with_brute_force),
        ("edge_cases", test_edge_cases),
        ("no_clause_yes", test_no_clause_yes),
        ("known_unsat", test_known_unsat),
        ("random_small", test_random_small),
        ("random_large_dpll", test_random_large_dpll),
        ("size_growth", test_size_growth),
    ]

    for name, fn in checks:
        tests_run += 1
        try:
            result = fn()
            tests_passed += 1
            extra = f" ({result} instances)" if isinstance(result, int) else ""
            print(f"PASS {name}{extra}")
        except AssertionError as exc:
            print(f"FAIL {name}: {exc}")
        except Exception as exc:  # noqa: BLE001
            print(f"ERROR {name}: {type(exc).__name__}: {exc}")

    print(f"\n{tests_passed}/{tests_run} tests passed")
    return tests_run, tests_passed


if __name__ == "__main__":
    main()
