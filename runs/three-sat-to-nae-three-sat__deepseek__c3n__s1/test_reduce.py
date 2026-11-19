"""Tests for the 3-SAT -> NAE-3-SAT reduction in reduce.py.

We implement brute-force solvers for both problems from the definitions in
problems.py and compare answers on many small instances.

Note: the reduction introduces one fresh variable per source clause, so the
reduced instance has num_vars = m + 1 + k.  Tests are kept small enough that
brute force over the reduced instance is feasible (num_vars <= ~16).
"""

from __future__ import annotations

import itertools
import json
import random

from problems import ThreeSat, NaeThreeSat
from reduce import reduce


def lit_value(literal: int, assignment: dict[int, bool]) -> bool:
    v = assignment[abs(literal)]
    return v if literal > 0 else (not v)


def solve_three_sat(instance: dict) -> bool:
    """Brute force 3-SAT."""
    m = instance["num_vars"]
    clauses = instance["clauses"]
    for bits in itertools.product([False, True], repeat=m):
        assignment = {i + 1: bits[i] for i in range(m)}
        if all(any(lit_value(l, assignment) for l in clause) for clause in clauses):
            return True
    return False


def solve_nae_three_sat(instance: dict) -> bool:
    """Brute force NAE-3-SAT."""
    m = instance["num_vars"]
    clauses = instance["clauses"]
    for bits in itertools.product([False, True], repeat=m):
        assignment = {i + 1: bits[i] for i in range(m)}
        ok = True
        for clause in clauses:
            vals = [lit_value(l, assignment) for l in clause]
            if all(vals) or not any(vals):
                ok = False
                break
        if ok:
            return True
    return False


def random_three_sat(num_vars: int, num_clauses: int, rng: random.Random) -> dict:
    clauses = []
    for _ in range(num_clauses):
        vs = rng.sample(range(1, num_vars + 1), 3)
        clause = [v if rng.random() < 0.5 else -v for v in vs]
        clauses.append(clause)
    return {"num_vars": num_vars, "clauses": clauses}


def main() -> None:
    rng = random.Random(12345)
    tests_run = 0
    tests_passed = 0
    failures = []

    def check(instance: dict, label: str) -> None:
        nonlocal tests_run, tests_passed
        tests_run += 1
        # Both instances must be valid according to problems.py.
        ThreeSat.validate(instance)
        target = reduce(instance)
        NaeThreeSat.validate(target)
        # Keep brute force feasible.
        assert target["num_vars"] <= 17, (label, target["num_vars"])

        src = solve_three_sat(instance)
        tgt = solve_nae_three_sat(target)
        if src == tgt:
            tests_passed += 1
        else:
            failures.append((label, instance, target, src, tgt))

    # Explicit edge cases.
    check({"num_vars": 0, "clauses": []}, "empty m=0")
    check({"num_vars": 5, "clauses": []}, "empty m=5")
    check({"num_vars": 3, "clauses": [[1, 2, 3]]}, "single clause")
    check({"num_vars": 3, "clauses": [[-1, -2, -3]]}, "single all-neg clause")
    check({"num_vars": 3, "clauses": [[1, 2, 3], [-1, -2, -3]]}, "two clauses")
    check({"num_vars": 4, "clauses": [[1, 2, 3], [-1, -2, -3], [1, -2, 4]]}, "three clauses")
    # Duplicate clauses.
    check({"num_vars": 3, "clauses": [[1, 2, 3], [1, 2, 3]]}, "duplicate clauses")
    # Unused variables.
    check({"num_vars": 6, "clauses": [[1, 2, 3]]}, "unused vars")
    # Literal order should not matter.
    check({"num_vars": 3, "clauses": [[3, 1, 2]]}, "shuffled literals")

    # Random tests, keeping m + 1 + k small.
    for m in range(3, 6):
        for _ in range(60):
            k = rng.randint(1, 6)
            inst = random_three_sat(m, k, rng)
            check(inst, f"random m={m} k={k}")

    # Slightly larger random tests (reduced num_vars <= 17).
    for _ in range(30):
        m = rng.randint(3, 6)
        k = rng.randint(1, 8)
        inst = random_three_sat(m, k, rng)
        check(inst, f"random-big m={m} k={k}")

    # All 8 sign patterns on 3 variables (8 clauses -> reduced 12 vars).
    all_clauses = [
        [1, 2, 3], [1, 2, -3], [1, -2, 3], [1, -2, -3],
        [-1, 2, 3], [-1, 2, -3], [-1, -2, 3], [-1, -2, -3],
    ]
    check({"num_vars": 3, "clauses": all_clauses}, "unsat all 8 clauses m=3")

    # A satisfiable dense instance.
    check({"num_vars": 3, "clauses": [[1, 2, 3], [-1, -2, 3], [1, -2, -3]]}, "dense sat")

    # Exhaustive over all 3-variable formulas with 1 or 2 clauses (up to signs).
    lits = [1, 2, 3, -1, -2, -3]
    seen = set()
    for c1 in itertools.combinations(lits, 3):
        if len({abs(x) for x in c1}) != 3:
            continue
        for c2 in itertools.combinations(lits, 3):
            if len({abs(x) for x in c2}) != 3:
                continue
            key = (tuple(sorted(c1)), tuple(sorted(c2)))
            if key in seen:
                continue
            seen.add(key)
            check({"num_vars": 3, "clauses": [list(c1), list(c2)]}, "exhaustive-2clause")

    print(f"tests_run={tests_run} tests_passed={tests_passed}")
    if failures:
        print("FAILURES:")
        for label, inst, tgt, src, t in failures[:10]:
            print(label, inst, "->", tgt, "src=", src, "tgt=", t)
        raise SystemExit(1)

    verdict = {
        "verified": tests_passed == tests_run,
        "tests_run": tests_run,
        "tests_passed": tests_passed,
    }
    with open("verdict.json", "w") as fh:
        json.dump(verdict, fh)
    print("verdict:", verdict)


if __name__ == "__main__":
    main()
