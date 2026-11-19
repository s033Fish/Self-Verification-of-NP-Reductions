"""Independent tests for reduce.py: Exact Cover -> SAT.

We implement our own brute-force solvers directly from the problem
definitions in problems.py, then compare the source answer with the
answer to the reduced SAT instance over many small instances.

Two independent solver implementations are used for each problem so that
a bug in one solver cannot silently mask a bug in the reduction.
"""

from __future__ import annotations

import itertools
import random

from problems import ExactCover, Sat
from reduce import reduce


# ----------------------------------------------------------------------
# Exact Cover solvers.

def solve_exact_cover_masks(instance: dict) -> bool:
    """Enumerate all sub-collections; require disjoint union == universe."""
    u = instance["universe_size"]
    sets = instance["sets"]
    n = len(sets)
    target = (1 << u) - 1
    for mask in range(1 << n):
        union = 0
        ok = True
        for i in range(n):
            if mask >> i & 1:
                s = 0
                for e in sets[i]:
                    s |= 1 << e
                if union & s:
                    ok = False
                    break
                union |= s
        if ok and union == target:
            return True
    return False


def solve_exact_cover_recursive(instance: dict) -> bool:
    """Recursively pick a set covering the lowest uncovered element."""
    u = instance["universe_size"]
    sets = [frozenset(s) for s in instance["sets"]]
    full = (1 << u) - 1

    def rec(covered: int) -> bool:
        if covered == full:
            return True
        # lowest uncovered element
        e = 0
        while covered >> e & 1:
            e += 1
        for s in sets:
            if e in s and not (covered & sum(1 << x for x in s)):
                new = covered | sum(1 << x for x in s)
                if rec(new):
                    return True
        return False

    return rec(0)


# ----------------------------------------------------------------------
# SAT solvers.

def solve_sat_masks(instance: dict) -> bool:
    m = instance["num_vars"]
    clauses = instance["clauses"]
    for bits in range(1 << m):
        if all(
            any(((bits >> (abs(lit) - 1)) & 1) == (1 if lit > 0 else 0)
                for lit in clause)
            for clause in clauses
        ):
            return True
    return False


def solve_sat_dpll(instance: dict) -> bool:
    """Simple recursive DPLL with unit propagation over clauses as sets."""
    clauses = [set(c) for c in instance["clauses"]]

    def rec(clauses):
        # drop satisfied clauses, simplify false literals
        simplified = []
        for c in clauses:
            if not c:
                return False
            # tautology -> satisfied
            if any(-lit in c for lit in c):
                continue
            simplified.append(c)
        if not simplified:
            return True
        # unit propagation
        units = [next(iter(c)) for c in simplified if len(c) == 1]
        if units:
            lit = units[0]
            new = []
            for c in simplified:
                if lit in c:
                    continue
                new.append(c - {-lit})
            return rec(new)
        # branch on a literal
        lit = next(iter(simplified[0]))
        for choice in (lit, -lit):
            new = []
            for c in simplified:
                if choice in c:
                    continue
                new.append(c - {-choice})
            if rec(new):
                return True
        return False

    return rec(clauses)


# ----------------------------------------------------------------------
# Instance enumeration helpers.

def all_subsets(u: int):
    elems = list(range(u))
    for r in range(u + 1):
        for combo in itertools.combinations(elems, r):
            yield list(combo)


def exhaustive_instances():
    for u in range(0, 4):
        subsets = list(all_subsets(u))
        for num_sets in range(0, 4):
            for combo in itertools.product(subsets, repeat=num_sets):
                yield {"universe_size": u, "sets": [list(s) for s in combo]}


def random_instances(count: int, seed: int = 12345):
    rng = random.Random(seed)
    for _ in range(count):
        u = rng.randint(0, 6)
        num_sets = rng.randint(0, 12)
        sets = []
        for _ in range(num_sets):
            k = rng.randint(0, u)
            sets.append(sorted(rng.sample(range(u), k)))
        yield {"universe_size": u, "sets": sets}


def run_tests() -> tuple[int, int, int, int]:
    tests_run = 0
    tests_passed = 0
    src_yes = 0
    tgt_yes = 0
    failures = []

    def check(inst: dict, tag: str):
        nonlocal tests_run, tests_passed, src_yes, tgt_yes
        tests_run += 1
        ExactCover.validate(inst)

        src_a = solve_exact_cover_masks(inst)
        src_b = solve_exact_cover_recursive(inst)
        assert src_a == src_b, f"source solvers disagree on {inst}"

        red = reduce(inst)
        Sat.validate(red)
        tgt_a = solve_sat_masks(red)
        tgt_b = solve_sat_dpll(red)
        assert tgt_a == tgt_b, f"target solvers disagree on {red}"

        if src_a:
            src_yes += 1
        if tgt_a:
            tgt_yes += 1

        if src_a == tgt_a:
            tests_passed += 1
        else:
            failures.append((tag, inst, src_a, red, tgt_a))

    for i, inst in enumerate(exhaustive_instances()):
        check(inst, f"exhaustive-{i}")

    for i, inst in enumerate(random_instances(3000)):
        check(inst, f"random-{i}")

    edge_cases = [
        {"universe_size": 0, "sets": []},
        {"universe_size": 0, "sets": [[], []]},
        {"universe_size": 1, "sets": []},
        {"universe_size": 1, "sets": [[]]},
        {"universe_size": 1, "sets": [[0]]},
        {"universe_size": 1, "sets": [[0], [0]]},
        {"universe_size": 2, "sets": [[0], [1]]},
        {"universe_size": 2, "sets": [[0, 1]]},
        {"universe_size": 2, "sets": [[0], [0, 1]]},
        {"universe_size": 3, "sets": [[0, 1], [1, 2], [0, 2]]},
        {"universe_size": 3, "sets": [[0, 1], [2]]},
        {"universe_size": 3, "sets": [[0], [1], [2], [0, 1, 2]]},
        {"universe_size": 4, "sets": [[0, 1], [2, 3], [0, 2], [1, 3]]},
        {"universe_size": 4, "sets": [[0, 1], [2, 3], [0, 2], [1, 3], [0, 1, 2, 3]]},
        {"universe_size": 5, "sets": [[0], [1], [2], [3], [4]]},
        {"universe_size": 5, "sets": [[0, 1, 2, 3, 4]]},
        {"universe_size": 5, "sets": [[0, 1, 2, 3, 4], [0]]},
    ]
    for i, inst in enumerate(edge_cases):
        check(inst, f"edge-{i}")

    if failures:
        print("FAILURES:")
        for tag, inst, src, red, tgt in failures[:10]:
            print(f"  {tag}: src={src} tgt={tgt} inst={inst} red={red}")
    print(f"source yes: {src_yes}, target yes: {tgt_yes}")
    return tests_run, tests_passed, src_yes, tgt_yes


if __name__ == "__main__":
    run, passed, sy, ty = run_tests()
    print(f"tests_run={run} tests_passed={passed}")
    assert run == passed, f"{run - passed} tests failed"
    print("ALL TESTS PASSED")
