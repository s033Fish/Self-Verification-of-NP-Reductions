"""Brute-force solvers + tests comparing 3-SAT answers to reduced IS answers."""

from __future__ import annotations

import itertools
import json
import random

from problems import ThreeSat, IndependentSet
from reduce import reduce


# --------------------------- brute force solvers ---------------------------

def solve_three_sat(instance: dict) -> bool:
    m = instance["num_vars"]
    clauses = instance["clauses"]
    for bits in itertools.product([False, True], repeat=m):
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


def solve_independent_set(instance: dict) -> bool:
    """Exact independent-set decision via backtracking with pruning."""
    n = instance["n"]
    k = instance["k"]
    if k <= 0:
        return True
    if k > n:
        return False
    adj = [set() for _ in range(n)]
    for u, v in instance["edges"]:
        adj[u].add(v)
        adj[v].add(u)

    # vertices sorted by degree ascending (branch on high-degree first)
    order = sorted(range(n), key=lambda v: -len(adj[v]))
    pos = {v: i for i, v in enumerate(order)}

    def rec(idx: int, chosen: int, forbidden: set) -> bool:
        if chosen >= k:
            return True
        if chosen + (n - idx) < k:
            return False
        if idx == n:
            return chosen >= k
        v = order[idx]
        # branch: include v if not forbidden
        if v not in forbidden:
            new_forbidden = forbidden | adj[v]
            if rec(idx + 1, chosen + 1, new_forbidden):
                return True
        # branch: exclude v
        return rec(idx + 1, chosen, forbidden)

    return rec(0, 0, set())


# ------------------------------- generators --------------------------------

def random_three_sat(rng: random.Random, max_vars: int, max_clauses: int) -> dict:
    m = rng.randint(0, max_vars)
    if m < 3:
        return {"num_vars": m, "clauses": []}
    nclauses = rng.randint(0, max_clauses)
    clauses = []
    for _ in range(nclauses):
        vs = rng.sample(range(1, m + 1), 3)
        clause = [v if rng.random() < 0.5 else -v for v in vs]
        clauses.append(clause)
    return {"num_vars": m, "clauses": clauses}


def all_small_three_sat():
    """Exhaustive small formulas: m in 0..3, all clause sets of size <= 2."""
    for m in range(0, 3):
        yield {"num_vars": m, "clauses": []}
    m = 3
    possible = []
    for vs in itertools.permutations(range(1, 4), 3):
        for signs in itertools.product([1, -1], repeat=3):
            possible.append([s * v for s, v in zip(signs, vs)])
    uniq = []
    seen = set()
    for c in possible:
        key = frozenset(c)
        if key not in seen:
            seen.add(key)
            uniq.append(c)
    yield {"num_vars": m, "clauses": []}
    for c in uniq:
        yield {"num_vars": m, "clauses": [c]}
    for c1, c2 in itertools.combinations(uniq, 2):
        yield {"num_vars": m, "clauses": [c1, c2]}


# ---------------------------------- tests ----------------------------------

def main() -> None:
    tests_run = 0
    tests_passed = 0

    def check(src: dict) -> None:
        nonlocal tests_run, tests_passed
        tests_run += 1
        ThreeSat.validate(src)
        tgt = reduce(src)
        IndependentSet.validate(tgt)
        expected = solve_three_sat(src)
        got = solve_independent_set(tgt)
        if expected == got:
            tests_passed += 1
        else:
            print("MISMATCH")
            print("  src     :", src)
            print("  expected:", expected)
            print("  tgt     :", tgt)
            print("  got     :", got)

    for src in all_small_three_sat():
        check(src)

    rng = random.Random(12345)
    for _ in range(400):
        check(random_three_sat(rng, max_vars=5, max_clauses=4))

    # explicit edge cases
    check({"num_vars": 0, "clauses": []})
    check({"num_vars": 7, "clauses": []})
    check({"num_vars": 3, "clauses": [[1, 2, 3]]})
    check({"num_vars": 3, "clauses": [[1, 2, 3], [1, 2, 3]]})
    check({"num_vars": 4, "clauses": [[1, 2, 3], [-1, -2, -3], [1, -2, 4]]})

    # unsatisfiable: all 8 clauses over 3 vars (each unordered clause once)
    unsat = []
    for vs in itertools.combinations(range(1, 4), 3):
        for signs in itertools.product([1, -1], repeat=3):
            unsat.append([s * v for s, v in zip(signs, vs)])
    check({"num_vars": 3, "clauses": unsat})

    # a larger satisfiable instance
    big = {"num_vars": 6, "clauses": []}
    for _ in range(8):
        vs = rng.sample(range(1, 7), 3)
        big["clauses"].append([v if rng.random() < 0.5 else -v for v in vs])
    check(big)

    print(f"tests_run={tests_run} tests_passed={tests_passed}")
    assert tests_run == tests_passed, "some tests failed"

    with open("verdict.json", "w") as f:
        json.dump(
            {"verified": True, "tests_run": tests_run, "tests_passed": tests_passed}, f
        )
    print("verdict.json written")


if __name__ == "__main__":
    main()
