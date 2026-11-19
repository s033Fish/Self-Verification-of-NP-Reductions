"""Brute-force solvers and tests for the Hamiltonian Path -> SAT reduction."""

from __future__ import annotations

import itertools
import random

from reduce import reduce


# ----------------------------------------------------------------------
# Brute-force solvers (written from the problem definitions).

def solve_hamiltonian_path(instance):
    n = instance["n"]
    edges = instance["edges"]
    if n == 0:
        return False
    if n == 1:
        return True
    edge_set = set()
    for u, v in edges:
        edge_set.add((u, v))
        edge_set.add((v, u))
    for perm in itertools.permutations(range(n)):
        if all((perm[i], perm[i + 1]) in edge_set for i in range(n - 1)):
            return True
    return False


def solve_sat(instance):
    """DPLL with unit propagation (correct, fast enough for small tests)."""
    clauses = [list(c) for c in instance["clauses"]]

    def rec(clauses, assign):
        while True:
            if any(len(c) == 0 for c in clauses):
                return False
            units = [c[0] for c in clauses if len(c) == 1]
            if not units:
                break
            lit = units[0]
            v = abs(lit)
            val = lit > 0
            if v in assign and assign[v] != val:
                return False
            assign = dict(assign)
            assign[v] = val
            new = []
            for c in clauses:
                if any(abs(l) == v and (l > 0) == val for l in c):
                    continue  # clause satisfied
                nc = [l for l in c if abs(l) != v]
                if not nc:
                    return False
                new.append(nc)
            clauses = new
        if not clauses:
            return True
        lit = clauses[0][0]
        v = abs(lit)
        for val in (True, False):
            assign2 = dict(assign)
            assign2[v] = val
            new = []
            ok = True
            for c in clauses:
                if any(abs(l) == v and (l > 0) == val for l in c):
                    continue
                nc = [l for l in c if abs(l) != v]
                if not nc:
                    ok = False
                    break
                new.append(nc)
            if ok and rec(new, assign2):
                return True
        return False

    return rec(clauses, {})


# ----------------------------------------------------------------------
# Helpers.

def all_graphs(n):
    pairs = list(itertools.combinations(range(n), 2))
    for mask in range(1 << len(pairs)):
        edges = [list(pairs[i]) for i in range(len(pairs)) if (mask >> i) & 1]
        yield {"n": n, "edges": edges}


def check(instance):
    expected = solve_hamiltonian_path(instance)
    target = reduce(instance)
    got = solve_sat(target)
    assert expected == got, (instance, expected, target, got)
    return expected


def main():
    tests_run = 0
    tests_passed = 0

    # Exhaustive over all graphs on 0..4 vertices.
    for n in range(0, 5):
        for instance in all_graphs(n):
            tests_run += 1
            check(instance)
            tests_passed += 1

    # Random larger graphs (n = 5..7), using brute force over permutations.
    rng = random.Random(12345)
    for n in range(5, 8):
        pairs = list(itertools.combinations(range(n), 2))
        for _ in range(30):
            edges = [list(p) for p in pairs if rng.random() < 0.4]
            instance = {"n": n, "edges": edges}
            tests_run += 1
            check(instance)
            tests_passed += 1

    # Explicit edge cases.
    edge_cases = [
        {"n": 0, "edges": []},
        {"n": 1, "edges": []},
        {"n": 2, "edges": []},
        {"n": 2, "edges": [[0, 1]]},
        {"n": 3, "edges": [[0, 1], [1, 2]]},
        {"n": 3, "edges": [[0, 1]]},
        {"n": 4, "edges": [[0, 1], [1, 2], [2, 3]]},
        {"n": 4, "edges": [[0, 1], [1, 2], [2, 3], [3, 0]]},
    ]
    for instance in edge_cases:
        tests_run += 1
        check(instance)
        tests_passed += 1

    # Validate the produced instances against the target's validator.
    from problems import Sat
    for n in range(0, 6):
        for instance in all_graphs(n):
            Sat.validate(reduce(instance))

    print(f"tests_run={tests_run} tests_passed={tests_passed}")
    assert tests_run == tests_passed
    return tests_run, tests_passed


if __name__ == "__main__":
    main()
