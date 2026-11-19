"""Independent checks of reduce.py: 1-in-3-SAT -> 3-SAT.

problems.py has no solvers, so we implement our own:
  * brute-force solvers for both problems (used on tiny instances), and
  * an exact DPLL solver for 3-SAT (used when the reduced instance has too
    many variables for brute force).
We then compare source answer vs. reduced answer on many small instances.
"""

from __future__ import annotations

import itertools
import random

from problems import OneInThreeSat, ThreeSat
from reduce import reduce


# ----------------------------------------------------------------------
# Brute-force solvers written from the problem definitions.

def solve_one_in_three_bruteforce(instance) -> bool:
    """True iff some assignment makes EXACTLY ONE var true in every clause."""
    m = instance["num_vars"]
    clauses = instance["clauses"]
    for bits in itertools.product((False, True), repeat=m):
        ok = True
        for (a, b, c) in clauses:
            cnt = int(bits[a - 1]) + int(bits[b - 1]) + int(bits[c - 1])
            if cnt != 1:
                ok = False
                break
        if ok:
            return True
    return False


def solve_three_sat_bruteforce(instance) -> bool:
    """True iff some assignment satisfies every clause (>=1 true literal)."""
    m = instance["num_vars"]
    clauses = instance["clauses"]
    for bits in itertools.product((False, True), repeat=m):
        ok = True
        for clause in clauses:
            sat = False
            for lit in clause:
                val = bits[abs(lit) - 1]
                if lit < 0:
                    val = not val
                if val:
                    sat = True
                    break
            if not sat:
                ok = False
                break
        if ok:
            return True
    return False


# ----------------------------------------------------------------------
# Exact DPLL solver for 3-SAT (unit propagation + branching).

def solve_three_sat_dpll(instance) -> bool:
    m = instance["num_vars"]
    clauses = [tuple(c) for c in instance["clauses"]]

    def dpll(clauses, assign):
        # assign: dict var -> bool
        while True:
            # simplify clauses under current assignment
            new_clauses = []
            unit = None
            for clause in clauses:
                remaining = []
                satisfied = False
                for lit in clause:
                    v = abs(lit)
                    if v in assign:
                        if assign[v] == (lit > 0):
                            satisfied = True
                            break
                    else:
                        remaining.append(lit)
                if satisfied:
                    continue
                if not remaining:
                    return False  # empty clause -> conflict
                if len(remaining) == 1:
                    unit = remaining[0]
                    break
                new_clauses.append(tuple(remaining))
            if unit is None:
                clauses = new_clauses
                break
            v = abs(unit)
            assign[v] = (unit > 0)
        if not clauses:
            return True
        # branch on first literal
        lit = clauses[0][0]
        v = abs(lit)
        for val in (lit > 0, lit < 0):
            a2 = dict(assign)
            a2[v] = val
            if dpll(clauses, a2):
                return True
        return False

    return dpll(clauses, {})


# ----------------------------------------------------------------------
# Instance generation (valid instances only).

def random_source_instance(rng, max_vars, max_clauses):
    m = rng.randint(0, max_vars)
    nclauses = rng.randint(0, max_clauses)
    clauses = []
    if m >= 3:
        for _ in range(nclauses):
            clauses.append(rng.sample(range(1, m + 1), 3))
    return {"num_vars": m, "clauses": clauses}


def all_source_instances(max_vars, max_clauses):
    """Exhaustively enumerate small valid source instances."""
    for m in range(0, max_vars + 1):
        if m < 3:
            yield {"num_vars": m, "clauses": []}
            continue
        triples = list(itertools.combinations(range(1, m + 1), 3))
        for k in range(0, max_clauses + 1):
            for combo in itertools.combinations_with_replacement(triples, k):
                yield {"num_vars": m, "clauses": [list(t) for t in combo]}


def main():
    tests_run = 0
    tests_passed = 0
    failures = []
    dpll_checks = 0

    def check(inst):
        nonlocal tests_run, tests_passed, dpll_checks
        tests_run += 1
        OneInThreeSat.validate(inst)
        out = reduce(inst)
        ThreeSat.validate(out)  # reduction must output a valid target instance
        src = solve_one_in_three_bruteforce(inst)
        if out["num_vars"] <= 14:
            tgt = solve_three_sat_bruteforce(out)
            # cross-check DPLL against brute force on the target
            assert solve_three_sat_dpll(out) == tgt, (out, tgt)
            dpll_checks += 1
        else:
            tgt = solve_three_sat_dpll(out)
        if src == tgt:
            tests_passed += 1
        else:
            failures.append((inst, out, src, tgt))

    # 1) explicit edge cases
    check({"num_vars": 0, "clauses": []})
    check({"num_vars": 1, "clauses": []})
    check({"num_vars": 5, "clauses": []})
    check({"num_vars": 3, "clauses": [[1, 2, 3]]})
    check({"num_vars": 3, "clauses": [[1, 2, 3], [1, 2, 3]]})
    check({"num_vars": 4, "clauses": [
        [1, 2, 3], [1, 2, 4], [1, 3, 4], [2, 3, 4]]})  # unsat

    # 2) exhaustive small instances
    for inst in all_source_instances(max_vars=4, max_clauses=3):
        check(inst)

    # 3) random instances (small enough for brute force on both sides)
    rng = random.Random(12345)
    for _ in range(600):
        check(random_source_instance(rng, max_vars=5, max_clauses=3))

    # 4) random instances with more clauses (target solved by DPLL)
    for _ in range(600):
        check(random_source_instance(rng, max_vars=8, max_clauses=8))

    print(f"tests_run={tests_run} tests_passed={tests_passed} "
          f"(brute-force target cross-checks: {dpll_checks})")
    if failures:
        print(f"FAILURES: {len(failures)}")
        for inst, out, src, tgt in failures[:10]:
            print("  inst=", inst)
            print("  out =", out)
            print("  src=", src, "tgt=", tgt)
    else:
        print("ALL PASSED")


if __name__ == "__main__":
    main()
