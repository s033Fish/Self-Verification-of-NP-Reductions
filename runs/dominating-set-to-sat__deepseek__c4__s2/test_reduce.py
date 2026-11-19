"""Brute-force solvers for both problems plus randomized/exhaustive tests."""

from __future__ import annotations

import itertools
import random

import problems
from reduce import reduce


# ----------------------------------------------------------------------
# Brute-force solvers written directly from the problem definitions.

def solve_dominating_set(instance):
    n = instance["n"]
    edges = instance["edges"]
    k = instance["k"]
    if k < 0:
        return False
    if n == 0:
        return True
    adj = [set() for _ in range(n)]
    for u, v in edges:
        adj[u].add(v)
        adj[v].add(u)
    for size in range(0, min(k, n) + 1):
        for subset in itertools.combinations(range(n), size):
            chosen = set(subset)
            if all(v in chosen or (adj[v] & chosen) for v in range(n)):
                return True
    return False


def solve_sat_bruteforce(instance):
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


def solve_sat_dpll(instance):
    """Simple DPLL with unit propagation; used when brute force is too slow."""
    clauses = [frozenset(c) for c in instance["clauses"]]

    def dpll(clauses):
        # Unit propagation.
        while True:
            units = [next(iter(c)) for c in clauses if len(c) == 1]
            if not units:
                break
            lit = units[0]
            new = []
            for c in clauses:
                if lit in c:
                    continue
                if -lit in c:
                    new.append(c - {-lit})
                else:
                    new.append(c)
            clauses = new
        if any(len(c) == 0 for c in clauses):
            return False
        if not clauses:
            return True
        # Choose a literal.
        lit = next(iter(next(iter(clauses))))
        for choice in (lit, -lit):
            new = []
            for c in clauses:
                if choice in c:
                    continue
                if -choice in c:
                    new.append(c - {-choice})
                else:
                    new.append(c)
            if dpll(new):
                return True
        return False

    return dpll(clauses)


def solve_sat(instance):
    if instance["num_vars"] <= 14:
        return solve_sat_bruteforce(instance)
    return solve_sat_dpll(instance)


# ----------------------------------------------------------------------
# Instance generators.

def random_graph_instance(rng, max_n=6, max_k=5):
    n = rng.randint(0, max_n)
    all_edges = [(u, v) for u in range(n) for v in range(u + 1, n)]
    rng.shuffle(all_edges)
    edges = [list(e) for e in all_edges if rng.random() < 0.5]
    k = rng.randint(-1, max_k)
    return {"n": n, "edges": edges, "k": k}


def all_graph_instances(max_n=4):
    """Every graph on 0..max_n vertices plus a range of k values."""
    for n in range(0, max_n + 1):
        all_edges = [(u, v) for u in range(n) for v in range(u + 1, n)]
        for mask in range(1 << len(all_edges)):
            edges = [list(e) for i, e in enumerate(all_edges) if mask >> i & 1]
            for k in range(-1, n + 2):
                yield {"n": n, "edges": edges, "k": k}


def main():
    tests_run = 0
    tests_passed = 0

    def check(instance):
        nonlocal tests_run, tests_passed
        tests_run += 1
        problems.DominatingSet.validate(instance)
        target = reduce(instance)
        problems.Sat.validate(target)
        expected = solve_dominating_set(instance)
        got = solve_sat(target)
        if expected == got:
            tests_passed += 1
        else:
            raise AssertionError(
                f"MISMATCH src={instance} -> tgt={target} "
                f"expected={expected} got={got}"
            )

    # Exhaustive small graphs.
    for instance in all_graph_instances(max_n=4):
        check(instance)

    # Random instances, including larger ones handled by DPLL.
    rng = random.Random(12345)
    for _ in range(4000):
        check(random_graph_instance(rng, max_n=8, max_k=6))

    # Explicit edge cases.
    check({"n": 0, "edges": [], "k": 0})
    check({"n": 0, "edges": [], "k": 5})
    check({"n": 0, "edges": [], "k": -1})
    check({"n": 3, "edges": [], "k": 0})
    check({"n": 3, "edges": [], "k": 3})
    check({"n": 3, "edges": [], "k": 100})
    check({"n": 4, "edges": [[0, 1], [1, 2], [2, 3]], "k": 1})
    check({"n": 4, "edges": [[0, 1], [1, 2], [2, 3]], "k": 2})
    check({"n": 5, "edges": [[0, 1], [1, 2], [2, 3], [3, 4], [4, 0]], "k": 2})

    print(f"tests_run={tests_run} tests_passed={tests_passed}")
    assert tests_run == tests_passed
    return tests_run, tests_passed


if __name__ == "__main__":
    main()
