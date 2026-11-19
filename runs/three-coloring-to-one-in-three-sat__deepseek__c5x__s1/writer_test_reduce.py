"""Brute-force (backtracking) solvers and tests for the reduction."""

from __future__ import annotations

import itertools
import random

from problems import ThreeColoring, OneInThreeSat
from reduce import reduce


# ---------------------------------------------------------------- solvers

def solve_three_coloring(instance):
    n = instance["n"]
    edges = instance["edges"]
    for coloring in itertools.product(range(3), repeat=n):
        if all(coloring[u] != coloring[v] for u, v in edges):
            return True
    return False


def solve_one_in_three_sat(instance):
    """Exact backtracking search for positive 1-in-3-SAT."""
    m = instance["num_vars"]
    clauses = [tuple(c) for c in instance["clauses"]]

    # For each variable, the clauses it appears in (for early pruning).
    clauses_with = [[] for _ in range(m + 1)]
    for idx, (a, b, c) in enumerate(clauses):
        clauses_with[a].append(idx)
        clauses_with[b].append(idx)
        clauses_with[c].append(idx)

    value = [None] * (m + 1)
    remaining = [3] * len(clauses)   # unassigned vars left in clause
    true_count = [0] * len(clauses)

    def ok_after(var):
        for idx in clauses_with[var]:
            if remaining[idx] == 0:
                if true_count[idx] != 1:
                    return False
            elif true_count[idx] > 1:
                return False
        return True

    def rec(var):
        if var > m:
            return all(t == 1 for t in true_count)
        for val in (False, True):
            value[var] = val
            touched = []
            for idx in clauses_with[var]:
                remaining[idx] -= 1
                if val:
                    true_count[idx] += 1
                touched.append(idx)
            if ok_after(var) and rec(var + 1):
                return True
            for idx in touched:
                remaining[idx] += 1
                if val:
                    true_count[idx] -= 1
            value[var] = None
        return False

    return rec(1)


# ---------------------------------------------------------------- helpers

def all_graphs(n):
    pairs = list(itertools.combinations(range(n), 2))
    for k in range(len(pairs) + 1):
        for chosen in itertools.combinations(pairs, k):
            yield {"n": n, "edges": [list(e) for e in chosen]}


def random_graph(n, p, rng):
    edges = []
    for u, v in itertools.combinations(range(n), 2):
        if rng.random() < p:
            edges.append([u, v])
    return {"n": n, "edges": edges}


# ---------------------------------------------------------------- tests

def main():
    tests_run = 0
    tests_passed = 0

    def check(source, label):
        nonlocal tests_run, tests_passed
        tests_run += 1
        target = reduce(source)
        ThreeColoring.validate(source)
        OneInThreeSat.validate(target)
        expected = solve_three_coloring(source)
        got = solve_one_in_three_sat(target)
        if expected != got:
            print(f"FAIL {label}: source={source} -> target={target} "
                  f"expected={expected} got={got}")
            return False
        tests_passed += 1
        return True

    # Exhaustive over all graphs with n = 0..5.
    for n in range(0, 6):
        count = 0
        for g in all_graphs(n):
            count += 1
            if not check(g, f"exhaustive n={n}"):
                print("TESTS FAILED")
                return 1
        print(f"exhaustive n={n}: {count} graphs passed")

    # Random larger graphs (still small enough to brute force).
    rng = random.Random(12345)
    for _ in range(400):
        n = rng.randint(0, 8)
        g = random_graph(n, rng.choice([0.1, 0.3, 0.5, 0.8]), rng)
        if not check(g, "random"):
            print("TESTS FAILED")
            return 1
    print("random tests passed")

    # Specific edge cases mentioned in the docstrings.
    specific = [
        {"n": 0, "edges": []},                                  # yes
        {"n": 1, "edges": []},                                  # yes
        {"n": 3, "edges": [[0, 1], [1, 2], [0, 2]]},            # triangle, yes
        {"n": 4, "edges": [[0, 1], [1, 2], [2, 3], [3, 0]]},    # C4, yes
        {"n": 4, "edges": [[0, 1], [0, 2], [0, 3], [1, 2],
                           [1, 3], [2, 3]]},                    # K4, no
        {"n": 5, "edges": [[0, 1], [0, 2], [0, 3], [0, 4],
                           [1, 2], [1, 3], [1, 4], [2, 3],
                           [2, 4], [3, 4]]},                    # K5, no
    ]
    for g in specific:
        if not check(g, "specific"):
            print("TESTS FAILED")
            return 1
    print("specific cases passed")

    # Sanity: the empty target instance is valid and yes.
    assert solve_one_in_three_sat({"num_vars": 0, "clauses": []}) is True
    OneInThreeSat.validate({"num_vars": 0, "clauses": []})

    print(f"tests_run={tests_run} tests_passed={tests_passed}")
    return 0 if tests_run == tests_passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
