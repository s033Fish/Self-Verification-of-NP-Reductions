"""Independent tests for reduce.py: 1-in-3-SAT -> 3-SAT.

We implement our own solvers from the problem definitions:
  * naive brute force over all assignments (used for tiny instances and as a
    cross-check), and
  * an exact DPLL solver (used for the larger reduced 3-SAT instances, whose
    auxiliary variables make naive enumeration too slow).

For every source instance we check:
  * the source instance is valid,
  * reduce() returns a valid TARGET instance,
  * our source solver and our target solver agree on the reduced instance.
"""
from __future__ import annotations

import itertools
import random

from problems import OneInThreeSat, ThreeSat
from reduce import reduce


# ----------------------------------------------------------------------
# Naive brute-force solvers (straight from the definitions)

def solve_one_in_three_brute(instance: dict) -> bool:
    m = instance["num_vars"]
    clauses = instance["clauses"]
    for bits in itertools.product((False, True), repeat=m):
        if all(int(bits[a - 1]) + int(bits[b - 1]) + int(bits[c - 1]) == 1
               for a, b, c in clauses):
            return True
    return not clauses


def solve_three_sat_brute(instance: dict) -> bool:
    m = instance["num_vars"]
    clauses = instance["clauses"]
    for bits in itertools.product((False, True), repeat=m):
        ok = True
        for clause in clauses:
            if not any((bits[abs(l) - 1] if l > 0 else not bits[abs(l) - 1])
                       for l in clause):
                ok = False
                break
        if ok:
            return True
    return not clauses


# ----------------------------------------------------------------------
# Exact DPLL solver for 3-SAT (TARGET)

def _simplify(clauses, var, value):
    true_lit = var if value else -var
    false_lit = -true_lit
    out = []
    for clause in clauses:
        if true_lit in clause:
            continue
        if false_lit in clause:
            out.append(tuple(l for l in clause if l != false_lit))
        else:
            out.append(clause)
    return out


def solve_three_sat_dpll(instance: dict) -> bool:
    clauses = [tuple(c) for c in instance["clauses"]]

    def dpll(clauses):
        while True:
            units = [c[0] for c in clauses if len(c) == 1]
            if not units:
                break
            for u in units:
                if -u in units:
                    return False
            for u in units:
                clauses = _simplify(clauses, abs(u), u > 0)
        if not clauses:
            return True
        if any(len(c) == 0 for c in clauses):
            return False
        # pure literal elimination
        lits = set(l for c in clauses for l in c)
        for l in list(lits):
            if -l not in lits:
                clauses = _simplify(clauses, abs(l), l > 0)
        if not clauses:
            return True
        if any(len(c) == 0 for c in clauses):
            return False
        var = abs(clauses[0][0])
        for value in (True, False):
            if dpll(_simplify(clauses, var, value)):
                return True
        return False

    return dpll(clauses)


def solve_one_in_three(instance: dict) -> bool:
    """Exact source solver: brute force (source var count stays small)."""
    return solve_one_in_three_brute(instance)


def solve_three_sat(instance: dict) -> bool:
    return solve_three_sat_dpll(instance)


# ----------------------------------------------------------------------
# Tests

def random_source_instance(rng, max_vars, max_clauses):
    m = rng.randint(0, max_vars)
    nclauses = rng.randint(0, max_clauses)
    clauses = []
    if m >= 3:
        for _ in range(nclauses):
            a, b, c = rng.sample(range(1, m + 1), 3)
            clauses.append([a, b, c])
    return {"num_vars": m, "clauses": clauses}


def main() -> int:
    rng = random.Random(20240517)
    tests_run = 0
    tests_passed = 0
    failures = []

    def check(instance, label):
        nonlocal tests_run, tests_passed
        tests_run += 1
        try:
            OneInThreeSat.validate(instance)
        except Exception as exc:
            failures.append((label, instance, f"source invalid: {exc}"))
            return
        reduced = reduce(instance)
        try:
            ThreeSat.validate(reduced)
        except Exception as exc:
            failures.append((label, instance, f"reduced invalid: {exc}"))
            return
        src = solve_one_in_three(instance)
        tgt = solve_three_sat(reduced)
        if src == tgt:
            tests_passed += 1
        else:
            failures.append((label, instance,
                             f"mismatch src={src} tgt={tgt} reduced={reduced}"))

    # --- cross-check the two target solvers on tiny reduced instances ---
    cross_checks = 0
    for _ in range(150):
        inst = random_source_instance(rng, max_vars=3, max_clauses=2)
        red = reduce(inst)
        if red["num_vars"] <= 14:
            cross_checks += 1
            assert solve_three_sat_brute(red) == solve_three_sat_dpll(red), red
    print(f"solver cross-checks: {cross_checks}")

    # --- explicit edge cases ---
    check({"num_vars": 0, "clauses": []}, "m=0 no clauses")
    check({"num_vars": 1, "clauses": []}, "m=1 no clauses")
    check({"num_vars": 5, "clauses": []}, "m=5 no clauses")
    check({"num_vars": 3, "clauses": [[1, 2, 3]]}, "single clause")
    check({"num_vars": 3, "clauses": [[1, 2, 3], [1, 2, 3]]}, "duplicate clause")
    check({"num_vars": 3, "clauses": [[1, 2, 3]] * 3}, "duplicate x3")
    check({"num_vars": 6, "clauses": [[1, 2, 3]]}, "unused vars")
    # 4 clauses on 4 vars: 1-in-3 unsat
    check({"num_vars": 4, "clauses": [[1, 2, 3], [1, 2, 4], [1, 3, 4], [2, 3, 4]]},
          "K4 clauses (unsat)")
    # two clauses sharing two variables are unsat for 1-in-3
    check({"num_vars": 4, "clauses": [[1, 2, 3], [1, 2, 4]]}, "shared pair (unsat)")

    # --- exhaustive over all multisets of the 4 triples on 4 vars, len<=3 ---
    triples4 = [[1, 2, 3], [1, 2, 4], [1, 3, 4], [2, 3, 4]]
    for length in range(0, 4):
        for combo in itertools.combinations_with_replacement(triples4, length):
            check({"num_vars": 4, "clauses": [list(c) for c in combo]},
                  f"exhaustive4 {combo}")

    # --- exhaustive over all triples on 5 vars, subsets up to size 3 ---
    triples5 = [list(c) for c in itertools.combinations(range(1, 6), 3)]
    for length in range(0, 4):
        for combo in itertools.combinations(triples5, length):
            check({"num_vars": 5, "clauses": [list(c) for c in combo]},
                  f"exhaustive5 {combo}")

    # --- random small instances ---
    for i in range(500):
        check(random_source_instance(rng, max_vars=5, max_clauses=6), f"random {i}")

    # --- random denser instances (more likely unsat) ---
    for i in range(300):
        check(random_source_instance(rng, max_vars=4, max_clauses=10), f"dense {i}")

    print(f"tests_run={tests_run} tests_passed={tests_passed}")
    if failures:
        print(f"FAILURES: {len(failures)}")
        for label, inst, msg in failures[:10]:
            print(" -", label, inst, msg)
        return 1
    print("ALL TESTS PASSED")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
