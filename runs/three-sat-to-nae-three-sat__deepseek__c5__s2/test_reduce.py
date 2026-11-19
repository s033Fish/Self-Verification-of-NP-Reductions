"""Independent tests for reduce.py: 3-SAT -> NAE-3-SAT.

We write brute-force solvers for both problems directly from the
definitions in problems.py, then compare the answer of many small source
instances with the answer of their reductions.
"""

from __future__ import annotations

import itertools
import json
import random

import problems
from reduce import reduce


# ----------------------------------------------------------------------
# Brute-force solvers written from the definitions.


def solve_three_sat(instance: dict) -> bool:
    """Yes iff some assignment makes every clause contain a true literal."""
    m = instance["num_vars"]
    clauses = instance["clauses"]
    for bits in itertools.product((False, True), repeat=m):
        def lit_value(lit):
            val = bits[abs(lit) - 1]
            return val if lit > 0 else not val

        if all(any(lit_value(l) for l in clause) for clause in clauses):
            return True
    return False


def solve_nae_three_sat(instance: dict) -> bool:
    """Yes iff some assignment makes every clause not all-equal."""
    m = instance["num_vars"]
    clauses = instance["clauses"]
    for bits in itertools.product((False, True), repeat=m):
        def lit_value(lit):
            val = bits[abs(lit) - 1]
            return val if lit > 0 else not val

        ok = True
        for clause in clauses:
            vals = [lit_value(l) for l in clause]
            if all(vals) or not any(vals):
                ok = False
                break
        if ok:
            return True
    return False


# ----------------------------------------------------------------------
# Instance generators (small, valid source instances).


def all_clauses_for(m):
    out = []
    for triple in itertools.combinations(range(1, m + 1), 3):
        for signs in itertools.product((1, -1), repeat=3):
            out.append([s * v for s, v in zip(signs, triple)])
    return out


def random_source_instance(rng, max_vars=6, max_clauses=6):
    m = rng.randint(0, max_vars)
    if m < 3:
        return {"num_vars": m, "clauses": []}
    n_clauses = rng.randint(0, max_clauses)
    clauses = []
    for _ in range(n_clauses):
        vs = rng.sample(range(1, m + 1), 3)
        clauses.append([v if rng.random() < 0.5 else -v for v in vs])
    return {"num_vars": m, "clauses": clauses}


def all_small_source_instances():
    """Exhaustively enumerate a family of small valid source instances."""
    for m in range(0, 5):
        if m < 3:
            yield {"num_vars": m, "clauses": []}
            continue
        all_clauses = all_clauses_for(m)
        yield {"num_vars": m, "clauses": []}
        for c in all_clauses:
            yield {"num_vars": m, "clauses": [c]}
        if m <= 4:
            for c1 in all_clauses:
                for c2 in all_clauses:
                    yield {"num_vars": m, "clauses": [c1, c2]}
        if m == 3:
            for c1 in all_clauses:
                for c2 in all_clauses:
                    for c3 in all_clauses:
                        yield {"num_vars": m, "clauses": [c1, c2, c3]}


def main():
    tests_run = 0
    tests_passed = 0
    failures = []

    def check(inst):
        nonlocal tests_run, tests_passed
        tests_run += 1
        problems.ThreeSat.validate(inst)
        expected = solve_three_sat(inst)
        red = reduce(inst)
        problems.NaeThreeSat.validate(red)
        got = solve_nae_three_sat(red)
        if got == expected:
            tests_passed += 1
        else:
            failures.append((inst, red, expected, got))

    # Exhaustive small instances (incl. all triples of clauses for m=3)
    for inst in all_small_source_instances():
        check(inst)

    # Random instances
    rng = random.Random(12345)
    for _ in range(5000):
        check(random_source_instance(rng))

    # Some larger random instances
    rng2 = random.Random(999)
    for _ in range(500):
        m = rng2.randint(3, 8)
        n = rng2.randint(0, 12)
        clauses = []
        for _ in range(n):
            vs = rng2.sample(range(1, m + 1), 3)
            clauses.append([v if rng2.random() < 0.5 else -v for v in vs])
        check({"num_vars": m, "clauses": clauses})

    # Duplicate clauses
    rng3 = random.Random(7)
    for _ in range(500):
        m = rng3.randint(3, 6)
        base = []
        for _ in range(rng3.randint(1, 3)):
            vs = rng3.sample(range(1, m + 1), 3)
            base.append([v if rng3.random() < 0.5 else -v for v in vs])
        clauses = [list(c) for c in base for _ in range(rng3.randint(1, 3))]
        check({"num_vars": m, "clauses": clauses})

    # Known unsatisfiable 3-SAT formulas must reduce to unsatisfiable NAE
    unsat_cases = [
        {"num_vars": 3, "clauses": [[1, 2, 3], [1, 2, -3], [1, -2, 3],
                                    [1, -2, -3], [-1, 2, 3], [-1, 2, -3],
                                    [-1, -2, 3], [-1, -2, -3]]},
    ]
    for inst in unsat_cases:
        check(inst)

    print(f"tests_run={tests_run} tests_passed={tests_passed}")
    if failures:
        print("FAILURES (showing up to 5):")
        for inst, red, expected, got in failures[:5]:
            print("  source:", inst, "expected", expected)
            print("  target:", red, "got", got)
    else:
        print("all tests passed")

    verdict = {
        "verified": len(failures) == 0,
        "tests_run": tests_run,
        "tests_passed": tests_passed,
    }
    with open("verdict.json", "w") as f:
        json.dump(verdict, f)
    print("verdict:", verdict)


if __name__ == "__main__":
    main()
