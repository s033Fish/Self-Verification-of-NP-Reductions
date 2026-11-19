"""Independent tests for reduce.py (Exact Cover -> SAT).

We implement our own solvers for both problems straight from the definitions
in problems.py, then compare the source answer with the answer to the reduced
SAT instance on many small instances (exhaustive for tiny sizes, plus
randomized larger ones checked with independent backtracking solvers).

Run:  python3 test_reduce.py
"""

from __future__ import annotations

import itertools
import random
import sys

from problems import ExactCover, Sat, InvalidInstance
from reduce import reduce


# ----------------------------------------------------------------------
# Brute-force solvers (written from the docstrings; problems.py has none)

def solve_exact_cover_bruteforce(instance) -> bool:
    u = instance["universe_size"]
    sets = instance["sets"]
    n = len(sets)
    target = set(range(u))
    for mask in range(1 << n):
        union = set()
        total = 0
        for i in range(n):
            if mask & (1 << i):
                s = sets[i]
                total += len(s)
                union.update(s)
        if total == len(union) and union == target:
            return True
    return False


def solve_sat_bruteforce(instance) -> bool:
    m = instance["num_vars"]
    clauses = instance["clauses"]
    for bits in range(1 << m):
        sat = True
        for clause in clauses:
            if not any(
                ((bits >> (abs(lit) - 1)) & 1) if lit > 0
                else not ((bits >> (abs(lit) - 1)) & 1)
                for lit in clause
            ):
                sat = False
                break
        if sat:
            return True
    return False


# ----------------------------------------------------------------------
# Independent backtracking solvers for larger instances

def solve_exact_cover_bt(instance) -> bool:
    """Backtracking exact cover (choose an uncovered element, try its sets)."""
    u = instance["universe_size"]
    sets = [frozenset(s) for s in instance["sets"]]
    by_elem = [[] for _ in range(u)]
    for i, s in enumerate(sets):
        for e in s:
            by_elem[e].append(i)
    covered = [False] * u

    def rec(remaining):
        if remaining == 0:
            return True
        # pick uncovered element with fewest candidate sets
        best_e, best_cands = None, None
        for e in range(u):
            if not covered[e]:
                cands = [i for i in by_elem[e] if not (sets[i] & covered_set)]
                if best_cands is None or len(cands) < len(best_cands):
                    best_e, best_cands = e, cands
        if not best_cands:
            return False
        for i in best_cands:
            for e in sets[i]:
                covered[e] = True
            if rec(remaining - len(sets[i])):
                return True
            for e in sets[i]:
                covered[e] = False
        return False

    # maintain a set of covered elements for disjointness checks
    covered_set = set()

    def rec2(remaining):
        if remaining == 0:
            return True
        best_e, best_cands = None, None
        for e in range(u):
            if e not in covered_set:
                cands = [i for i in by_elem[e] if not (sets[i] & covered_set)]
                if best_cands is None or len(cands) < len(best_cands):
                    best_e, best_cands = e, cands
        if not best_cands:
            return False
        for i in best_cands:
            covered_set.update(sets[i])
            if rec2(remaining - len(sets[i])):
                return True
            covered_set.difference_update(sets[i])
        return False

    return rec2(u)


def solve_sat_dpll(instance) -> bool:
    """Simple DPLL satisfiability checker."""
    m = instance["num_vars"]
    clauses = [list(c) for c in instance["clauses"]]

    def simplify(clauses, lit):
        out = []
        for c in clauses:
            if lit in c:
                continue  # clause satisfied
            nc = [x for x in c if x != -lit]
            if not nc:
                return None  # empty clause -> conflict
            out.append(nc)
        return out

    def dpll(clauses):
        if any(len(c) == 0 for c in clauses):
            return False
        # unit propagation
        while True:
            units = [c[0] for c in clauses if len(c) == 1]
            if not units:
                break
            lit = units[0]
            clauses = simplify(clauses, lit)
            if clauses is None:
                return False
        if not clauses:
            return True
        # pure literal elimination
        lits = {l for c in clauses for l in c}
        for l in list(lits):
            if -l not in lits:
                clauses = simplify(clauses, l)
                if clauses is None:
                    return False
                if not clauses:
                    return True
        # branch on first literal
        lit = clauses[0][0]
        for choice in (lit, -lit):
            nc = simplify(clauses, choice)
            if nc is not None and dpll(nc):
                return True
        return False

    return dpll(clauses)


# ----------------------------------------------------------------------
# Instance generation

def gen_exhaustive():
    for u in range(0, 4):
        subsets = []
        for r in range(u + 1):
            for combo in itertools.combinations(range(u), r):
                subsets.append(list(combo))
        for n in range(0, 5):
            for choice in itertools.combinations_with_replacement(range(len(subsets)), n):
                yield {"universe_size": u, "sets": [list(subsets[i]) for i in choice]}


def gen_random(rng, trials, umax, nmax):
    for _ in range(trials):
        u = rng.randint(0, umax)
        n = rng.randint(0, nmax)
        sets = []
        for _ in range(n):
            k = rng.randint(0, u)
            sets.append(sorted(rng.sample(range(u), k)))
        yield {"universe_size": u, "sets": sets}


# ----------------------------------------------------------------------
# Test driver

def main() -> int:
    rng = random.Random(12345)
    tests_run = 0
    tests_passed = 0
    failures = []

    small = list(gen_exhaustive()) + list(gen_random(rng, 4000, 6, 7))
    for inst in small:
        tests_run += 1
        try:
            ExactCover.validate(inst)
        except InvalidInstance as exc:
            failures.append((inst, f"generated invalid source: {exc}"))
            continue
        expected = solve_exact_cover_bruteforce(inst)
        try:
            reduced = reduce(inst)
        except Exception as exc:
            failures.append((inst, f"reduce raised {type(exc).__name__}: {exc}"))
            continue
        try:
            Sat.validate(reduced)
        except InvalidInstance as exc:
            failures.append((inst, f"reduced invalid: {exc} -> {reduced}"))
            continue
        got = solve_sat_bruteforce(reduced)
        if got == expected:
            tests_passed += 1
        else:
            failures.append((inst, f"expected {expected}, got {got}; reduced={reduced}"))

    # Larger instances checked with independent backtracking solvers.
    large = list(gen_random(rng, 3000, 12, 16))
    for inst in large:
        tests_run += 1
        try:
            ExactCover.validate(inst)
        except InvalidInstance as exc:
            failures.append((inst, f"generated invalid source: {exc}"))
            continue
        expected = solve_exact_cover_bt(inst)
        try:
            reduced = reduce(inst)
        except Exception as exc:
            failures.append((inst, f"reduce raised {type(exc).__name__}: {exc}"))
            continue
        try:
            Sat.validate(reduced)
        except InvalidInstance as exc:
            failures.append((inst, f"reduced invalid: {exc} -> {reduced}"))
            continue
        got = solve_sat_dpll(reduced)
        if got == expected:
            tests_passed += 1
        else:
            failures.append((inst, f"expected {expected}, got {got}; reduced={reduced}"))

    # ---- Explicit named edge cases -------------------------------------
    edge_cases = [
        # (instance, expected_yes)
        ({"universe_size": 0, "sets": []}, True),
        ({"universe_size": 0, "sets": [[], []]}, True),
        ({"universe_size": 1, "sets": []}, False),
        ({"universe_size": 1, "sets": [[]]}, False),
        ({"universe_size": 1, "sets": [[0]]}, True),
        ({"universe_size": 1, "sets": [[0], [0]]}, True),
        ({"universe_size": 2, "sets": [[0], [1]]}, True),
        ({"universe_size": 2, "sets": [[0, 1]]}, True),
        ({"universe_size": 2, "sets": [[0], [0]]}, False),
        ({"universe_size": 2, "sets": [[0, 1], [0, 1]]}, True),
        ({"universe_size": 3, "sets": [[0, 1], [1, 2]]}, False),
        ({"universe_size": 3, "sets": [[0, 1], [2]]}, True),
        ({"universe_size": 3, "sets": [[0, 1], [2], []]}, True),
        ({"universe_size": 3, "sets": [[0], [1], [2], [0, 1, 2]]}, True),
        ({"universe_size": 4, "sets": [[0, 1], [2, 3], [1, 2]]}, True),
        ({"universe_size": 4, "sets": [[0, 1], [2, 3], [1, 2], [0, 3]]}, True),
    ]
    for inst, expected in edge_cases:
        tests_run += 1
        ExactCover.validate(inst)
        reduced = reduce(inst)
        Sat.validate(reduced)
        got = solve_sat_bruteforce(reduced)
        if got == expected and solve_exact_cover_bruteforce(inst) == expected:
            tests_passed += 1
        else:
            failures.append((inst, f"edge case expected {expected}, got {got}; reduced={reduced}"))

    print(f"tests_run={tests_run} tests_passed={tests_passed} failures={len(failures)}")
    for inst, msg in failures[:20]:
        print("FAIL:", inst, "->", msg)
    return 0 if not failures else 1


if __name__ == "__main__":
    sys.exit(main())
