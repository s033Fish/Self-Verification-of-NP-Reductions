"""Independent tests for reduce.py (SAT -> 3-SAT).

We implement our own brute-force solvers for both problems directly from the
definitions in problems.py, generate many small source instances (including
edge cases), reduce them, and compare answers.  A DPLL solver is used as a
backup for reduced instances that are too large to brute force, and we also
cross-check DPLL against brute force on small instances.
"""

from __future__ import annotations

import itertools
import random
import time

from problems import Sat, ThreeSat
import reduce as reduce_mod


# ----------------------------------------------------------------------
# Brute-force solvers (from the definitions)
# ----------------------------------------------------------------------

def _lit_true(lit: int, assignment: dict[int, bool]) -> bool:
    val = assignment[abs(lit)]
    return val if lit > 0 else (not val)


def brute_solve(instance: dict) -> bool:
    """Brute force over all 2^m assignments.  Works for Sat and ThreeSat."""
    m = instance["num_vars"]
    clauses = instance["clauses"]
    for bits in range(1 << m):
        assignment = {v: bool((bits >> (v - 1)) & 1) for v in range(1, m + 1)}
        if all(any(_lit_true(l, assignment) for l in clause) for clause in clauses):
            return True
    return False


# ----------------------------------------------------------------------
# DPLL solver (exact, used for larger reduced instances)
# ----------------------------------------------------------------------

def _dpll(clauses: list[list[int]], assignment: dict[int, bool]) -> bool:
    assignment = dict(assignment)

    def simplify(clauses, assignment):
        out = []
        for clause in clauses:
            satisfied = False
            rest = []
            for lit in clause:
                v = abs(lit)
                if v in assignment:
                    if (lit > 0) == assignment[v]:
                        satisfied = True
                        break
                else:
                    rest.append(lit)
            if satisfied:
                continue
            if not rest:
                return None  # empty clause -> conflict
            out.append(rest)
        return out

    while True:
        clauses = simplify(clauses, assignment)
        if clauses is None:
            return False
        if not clauses:
            return True
        unit = None
        for clause in clauses:
            if len(clause) == 1:
                unit = clause[0]
                break
        if unit is not None:
            assignment[abs(unit)] = unit > 0
            continue
        break

    shortest = min(clauses, key=len)
    v = abs(shortest[0])
    for val in (True, False):
        a2 = dict(assignment)
        a2[v] = val
        if _dpll(clauses, a2):
            return True
    return False


def dpll_solve(instance: dict) -> bool:
    return _dpll(instance["clauses"], {})


def solve(instance: dict) -> bool:
    """Exact answer; brute force when small, DPLL otherwise."""
    if instance["num_vars"] <= 16:
        return brute_solve(instance)
    return dpll_solve(instance)


# ----------------------------------------------------------------------
# Instance generation
# ----------------------------------------------------------------------

def edge_case_instances() -> list[dict]:
    return [
        {"num_vars": 0, "clauses": []},
        {"num_vars": 1, "clauses": []},
        {"num_vars": 5, "clauses": []},
        {"num_vars": 0, "clauses": [[]]},
        {"num_vars": 1, "clauses": [[]]},
        {"num_vars": 3, "clauses": [[1], []]},
        {"num_vars": 3, "clauses": [[], [1, 2, 3]]},
        {"num_vars": 1, "clauses": [[1]]},
        {"num_vars": 1, "clauses": [[-1]]},
        {"num_vars": 1, "clauses": [[1], [-1]]},
        {"num_vars": 2, "clauses": [[1], [-2]]},
        {"num_vars": 1, "clauses": [[1, -1]]},
        {"num_vars": 2, "clauses": [[1, -1], [2]]},
        {"num_vars": 2, "clauses": [[1, 2, -1]]},
        {"num_vars": 1, "clauses": [[1, 1, 1]]},
        {"num_vars": 1, "clauses": [[-1, -1]]},
        {"num_vars": 2, "clauses": [[1, 1, -2, -2]]},
        {"num_vars": 2, "clauses": [[1, 2]]},
        {"num_vars": 2, "clauses": [[1, 2], [-1, 2], [1, -2], [-1, -2]]},
        {"num_vars": 2, "clauses": [[1, 2], [-1, -2]]},
        {"num_vars": 3, "clauses": [[1, 2, 3]]},
        {"num_vars": 3, "clauses": [[1, 2, 3], [-1, -2, -3]]},
        {"num_vars": 4, "clauses": [[1, 2, 3, 4]]},
        {"num_vars": 4, "clauses": [[-1, -2, -3, -4]]},
        {"num_vars": 5, "clauses": [[1, 2, 3, 4, 5]]},
        {"num_vars": 5, "clauses": [[-1, -2, -3, -4, -5]]},
        {"num_vars": 6, "clauses": [[1, -2, 3, -4, 5, -6]]},
        {"num_vars": 6, "clauses": [[-1, -2, -3, -4, -5, -6]]},
        {"num_vars": 3, "clauses": [[1], [2, 3], [1, -2, 3, -3]]},
        {"num_vars": 4, "clauses": [[1, 2], [-1, -2], [3, 4], [-3, -4]]},
        {"num_vars": 4, "clauses": [[1, 2, 3, 4], [-1], [-2], [-3], [-4]]},
        {"num_vars": 2, "clauses": [[1, 2], [1, 2], [-1, -2]]},
        # long clauses with many distinct variables (exercise Tseitin chain)
        {"num_vars": 7, "clauses": [[1, 2, 3, 4, 5, 6, 7]]},
        {"num_vars": 7, "clauses": [[-1, -2, -3, -4, -5, -6, -7]]},
        {"num_vars": 8, "clauses": [[1, -2, 3, -4, 5, -6, 7, -8]]},
        {"num_vars": 8, "clauses": [[1, 2, 3, 4, 5, 6, 7, 8], [-1], [-2], [-3],
                                    [-4], [-5], [-6], [-7], [-8]]},
        {"num_vars": 9, "clauses": [[1, 2, 3, 4, 5, 6, 7, 8, 9]]},
        {"num_vars": 10, "clauses": [[1, 2, 3, 4, 5, 6, 7, 8, 9, 10]]},
        # long clause that is unsat only together with units
        {"num_vars": 8, "clauses": [[1, 2, 3, 4, 5, 6, 7, 8]] + [[-i] for i in range(1, 9)]},
    ]


def random_instances(rng: random.Random, count: int, max_m: int, max_len: int,
                     max_clauses: int) -> list[dict]:
    out = []
    for _ in range(count):
        m = rng.randint(0, max_m)
        nclauses = rng.randint(0, max_clauses)
        clauses = []
        for _ in range(nclauses):
            length = rng.randint(0, max_len)
            if m == 0:
                clause = []
            else:
                clause = [rng.choice([1, -1]) * rng.randint(1, m) for _ in range(length)]
            clauses.append(clause)
        out.append({"num_vars": m, "clauses": clauses})
    return out


def exhaustive_small_instances() -> list[dict]:
    out = []
    for m in (0, 1, 2):
        pool = [[]]
        if m >= 1:
            lits = [1, -1] if m == 1 else [1, -1, 2, -2]
            pool += [[l] for l in lits]
            pool += [list(c) for c in itertools.combinations(lits, 2)]
            pool += [list(c) for c in itertools.combinations(lits, 3)]
            if m == 2:
                pool += [[1, -1], [2, -2]]
        for c in pool:
            out.append({"num_vars": m, "clauses": [list(c)]})
        seen = set()
        for c1 in pool:
            for c2 in pool:
                key = (tuple(sorted(c1)), tuple(sorted(c2)))
                if key in seen:
                    continue
                seen.add(key)
                out.append({"num_vars": m, "clauses": [list(c1), list(c2)]})
    return out


# ----------------------------------------------------------------------
# Test runner
# ----------------------------------------------------------------------

def main() -> int:
    rng = random.Random(12345)
    instances = edge_case_instances()
    instances += exhaustive_small_instances()
    instances += random_instances(rng, 4000, max_m=4, max_len=6, max_clauses=4)
    instances += random_instances(rng, 3000, max_m=6, max_len=9, max_clauses=3)
    instances += random_instances(rng, 1000, max_m=8, max_len=10, max_clauses=2)

    tests_run = 0
    tests_passed = 0
    failures = []

    # sanity: brute force vs DPLL on small source instances
    solver_mismatches = 0
    for inst in instances:
        if inst["num_vars"] <= 12:
            if brute_solve(inst) != dpll_solve(inst):
                solver_mismatches += 1
                failures.append(("solver-mismatch", inst))
    print(f"solver cross-check mismatches: {solver_mismatches}")

    for inst in instances:
        tests_run += 1
        try:
            Sat.validate(inst)
        except Exception as exc:
            failures.append(("source-invalid", inst, repr(exc)))
            continue
        try:
            reduced = reduce_mod.reduce(inst)
        except Exception as exc:
            failures.append(("reduce-raised", inst, repr(exc)))
            continue
        try:
            ThreeSat.validate(reduced)
        except Exception as exc:
            failures.append(("target-invalid", inst, repr(exc), reduced))
            continue

        src_answer = solve(inst)
        tgt_answer = solve(reduced)
        if src_answer != tgt_answer:
            failures.append(("answer-mismatch", inst, src_answer, reduced, tgt_answer))
            continue
        tests_passed += 1

    print(f"tests_run={tests_run} tests_passed={tests_passed}")
    if failures:
        print(f"FAILURES: {len(failures)}")
        for f in failures[:20]:
            print("  ", f)
        return 1
    print("ALL TESTS PASSED")

    # explicit unsat gadget check
    unsat_inst = {"num_vars": 2, "clauses": [[1], []]}
    red = reduce_mod.reduce(unsat_inst)
    assert solve(red) is False, "empty clause must reduce to unsat 3-SAT"
    print("unsat gadget ok:", red)

    # polynomial-time smoke test: large instance must finish quickly
    big = {
        "num_vars": 500,
        "clauses": [[((i + j) % 500) + 1 if (i + j) % 2 == 0 else -(((i + j) % 500) + 1)
                     for j in range(12)] for i in range(500)],
    }
    t0 = time.time()
    big_reduced = reduce_mod.reduce(big)
    dt = time.time() - t0
    ThreeSat.validate(big_reduced)
    print(f"big instance: {big['num_vars']} vars, {len(big['clauses'])} clauses -> "
          f"{big_reduced['num_vars']} vars, {len(big_reduced['clauses'])} clauses, {dt:.4f}s")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
