"""Independent tests for reduce.py: Exact Cover -> SAT.

We implement brute-force solvers for both problems from the definitions in
problems.py, generate many small source instances (including edge cases),
reduce them, and compare answers.  A verdict.json is written at the end.
"""
from __future__ import annotations

import itertools
import json
import random
from typing import Any, Dict, List

from problems import ExactCover, Sat
from reduce import reduce


# ----------------------------------------------------------------------
# Brute-force solvers (written from the problem definitions)

def solve_exact_cover(instance: Dict[str, Any]) -> bool:
    """Yes iff some sub-collection of sets partitions the universe."""
    u = instance["universe_size"]
    sets = instance["sets"]
    m = len(sets)
    for mask in range(1 << m):
        covered = set()
        ok = True
        for i in range(m):
            if (mask >> i) & 1:
                s = set(sets[i])
                if covered & s:          # not pairwise disjoint
                    ok = False
                    break
                covered |= s
        if ok and len(covered) == u:     # union is whole universe
            return True
    return False


def solve_sat(instance: Dict[str, Any]) -> bool:
    """Yes iff some assignment satisfies every clause."""
    m = instance["num_vars"]
    clauses = instance["clauses"]
    for mask in range(1 << m):
        assign = [bool((mask >> (v - 1)) & 1) for v in range(1, m + 1)]
        good = True
        for clause in clauses:
            if not any(
                (lit > 0 and assign[lit - 1]) or (lit < 0 and not assign[-lit - 1])
                for lit in clause
            ):
                good = False
                break
        if good:
            return True
    return False


# ----------------------------------------------------------------------
# Instance generation

def all_subsets(u: int) -> List[List[int]]:
    subs = []
    for r in range(u + 1):
        for combo in itertools.combinations(range(u), r):
            subs.append(list(combo))
    return subs


def gen_instances():
    """Many small Exact Cover instances, including edge cases."""
    instances = []
    for u in range(0, 4):
        subs = all_subsets(u)
        for k in range(0, 4):
            for combo in itertools.product(subs, repeat=k):
                instances.append({"universe_size": u, "sets": [list(s) for s in combo]})
    return instances


# ----------------------------------------------------------------------
# Tests

def main() -> None:
    tests_run = 0
    tests_passed = 0
    failures = []

    instances = gen_instances()
    print(f"Generated {len(instances)} source instances")

    for inst in instances:
        ExactCover.validate(inst)
        expected = solve_exact_cover(inst)
        out = reduce(inst)
        Sat.validate(out)
        got = solve_sat(out)
        tests_run += 1
        if expected == got:
            tests_passed += 1
        else:
            failures.append((inst, expected, got, out))

    # Explicit edge cases
    edge_cases = [
        {"universe_size": 0, "sets": []},
        {"universe_size": 0, "sets": [[], []]},
        {"universe_size": 1, "sets": []},
        {"universe_size": 1, "sets": [[]]},
        {"universe_size": 1, "sets": [[0], [0]]},
        {"universe_size": 2, "sets": [[0], [1], [0, 1]]},
        {"universe_size": 2, "sets": [[0, 1], [0, 1]]},
        {"universe_size": 3, "sets": [[0, 1], [1, 2], [0, 2]]},
    ]
    for inst in edge_cases:
        ExactCover.validate(inst)
        expected = solve_exact_cover(inst)
        out = reduce(inst)
        Sat.validate(out)
        got = solve_sat(out)
        tests_run += 1
        if expected == got:
            tests_passed += 1
        else:
            failures.append((inst, expected, got, out))

    # Randomized tests
    rng = random.Random(12345)
    for _ in range(300):
        u = rng.randint(0, 5)
        k = rng.randint(0, 6)
        sets = []
        for _ in range(k):
            r = rng.randint(0, u)
            sets.append(sorted(rng.sample(range(u), r)))
        inst = {"universe_size": u, "sets": sets}
        ExactCover.validate(inst)
        expected = solve_exact_cover(inst)
        out = reduce(inst)
        Sat.validate(out)
        got = solve_sat(out)
        tests_run += 1
        if expected == got:
            tests_passed += 1
        else:
            failures.append((inst, expected, got, out))

    print(f"tests_run={tests_run} tests_passed={tests_passed}")
    if failures:
        print("FAILURES:")
        for inst, exp, got, out in failures[:20]:
            print(f"  inst={inst} expected={exp} got={got} out={out}")
    else:
        print("All tests passed.")

    verdict = {
        "verified": len(failures) == 0,
        "tests_run": tests_run,
        "tests_passed": tests_passed,
    }
    with open("verdict.json", "w") as f:
        json.dump(verdict, f)
    print("verdict.json:", verdict)


if __name__ == "__main__":
    main()
