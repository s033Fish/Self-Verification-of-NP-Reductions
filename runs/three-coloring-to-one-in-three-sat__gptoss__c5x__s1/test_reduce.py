"""Independent tests for reduce.py: 3-Coloring -> Positive 1-in-3-SAT.

We implement our own brute-force solvers from the problem definitions in
problems.py (which provides no solvers), then compare the answers of many
small source instances with the answers of their reductions.
"""

from __future__ import annotations

import itertools
import random
import sys

from problems import ThreeColoring, OneInThreeSat
from reduce import reduce


# ----------------------------------------------------------------------
# Brute-force solver for 3-Coloring.
# ----------------------------------------------------------------------

def solve_three_coloring(instance) -> bool:
    n = instance["n"]
    edges = instance["edges"]
    for coloring in itertools.product(range(3), repeat=n):
        if all(coloring[u] != coloring[v] for u, v in edges):
            return True
    return False


# ----------------------------------------------------------------------
# Solver for positive 1-in-3-SAT (backtracking + unit propagation).
# Independent of the reduction; works for any positive 1-in-3 formula.
# ----------------------------------------------------------------------

def solve_one_in_three(instance) -> bool:
    num_vars = instance["num_vars"]
    clauses = [tuple(c) for c in instance["clauses"]]

    # values: 0 = false, 1 = true, -1 = unassigned (index by variable-1)
    values = [-1] * num_vars

    def propagate():
        """Return False on conflict, True otherwise. Mutates values."""
        changed = True
        while changed:
            changed = False
            for clause in clauses:
                true_count = 0
                unknown = []
                for var in clause:
                    val = values[var - 1]
                    if val == 1:
                        true_count += 1
                    elif val == -1:
                        unknown.append(var)
                if true_count > 1:
                    return False
                if true_count == 1:
                    # every unknown must be false
                    for var in unknown:
                        values[var - 1] = 0
                        changed = True
                elif true_count == 0:
                    if len(unknown) == 0:
                        return False
                    if len(unknown) == 1:
                        values[unknown[0] - 1] = 1
                        changed = True
        return True

    def backtrack():
        if not propagate():
            return False
        # find an unassigned variable
        pivot = -1
        for i in range(num_vars):
            if values[i] == -1:
                pivot = i
                break
        if pivot == -1:
            return True  # all assigned and propagation found no conflict
        saved = values[:]
        for guess in (1, 0):
            values[pivot] = guess
            if backtrack():
                return True
            values[:] = saved
        return False

    return backtrack()


# ----------------------------------------------------------------------
# Instance generation.
# ----------------------------------------------------------------------

def all_graphs(n):
    """Yield every simple graph on n labelled vertices."""
    pairs = [(u, v) for u in range(n) for v in range(u + 1, n)]
    for mask in range(1 << len(pairs)):
        edges = [list(pairs[i]) for i in range(len(pairs)) if (mask >> i) & 1]
        yield {"n": n, "edges": edges}


def random_graph(n, p, rng):
    edges = []
    for u in range(n):
        for v in range(u + 1, n):
            if rng.random() < p:
                edges.append([u, v])
    return {"n": n, "edges": edges}


# ----------------------------------------------------------------------
# Test driver.
# ----------------------------------------------------------------------

def main():
    rng = random.Random(12345)
    tests_run = 0
    tests_passed = 0
    failures = []

    def check(instance, label):
        nonlocal tests_run, tests_passed
        tests_run += 1
        try:
            ThreeColoring.validate(instance)
        except Exception as exc:  # pragma: no cover
            failures.append((label, instance, f"source invalid: {exc}"))
            return
        expected = solve_three_coloring(instance)
        try:
            reduced = reduce(instance)
        except Exception as exc:
            failures.append((label, instance, f"reduce raised: {exc!r}"))
            return
        # The reduction must produce a valid target instance.
        try:
            OneInThreeSat.validate(reduced)
        except Exception as exc:
            failures.append((label, instance, f"target invalid: {exc}"))
            return
        got = solve_one_in_three(reduced)
        if got == expected:
            tests_passed += 1
        else:
            failures.append(
                (label, instance, f"expected {expected}, reduction gave {got}")
            )

    # 1. Exhaustive over all graphs with n = 0..5.
    for n in range(0, 6):
        for g in all_graphs(n):
            check(g, f"exhaustive n={n}")

    # 2. Random graphs for slightly larger n.
    for n in range(6, 9):
        for _ in range(400):
            check(random_graph(n, rng.uniform(0.0, 1.0), rng), f"random n={n}")

    # 3. Hand-picked edge cases.
    edge_cases = [
        {"n": 0, "edges": []},
        {"n": 1, "edges": []},
        {"n": 2, "edges": [[0, 1]]},
        {"n": 3, "edges": [[0, 1], [1, 2], [0, 2]]},          # K3 -> yes
        {"n": 4, "edges": [[0, 1], [1, 2], [2, 3], [3, 0],
                           [0, 2], [1, 3]]},                   # K4 -> no
        {"n": 4, "edges": [[0, 1], [1, 2], [2, 3], [3, 0]]},   # C4 -> yes
        {"n": 5, "edges": [[0, 1], [1, 2], [2, 3], [3, 4], [4, 0]]},  # C5 -> yes
        {"n": 6, "edges": [[0, 1], [1, 2], [2, 3], [3, 4], [4, 5],
                           [5, 0], [0, 3], [1, 4], [2, 5]]},   # K3,3 -> no
        {"n": 5, "edges": [[0, 1], [0, 2], [0, 3], [0, 4]]},   # star -> yes
        {"n": 6, "edges": [[0, 1], [0, 2], [0, 3], [0, 4], [0, 5],
                           [1, 2], [1, 3], [1, 4], [1, 5],
                           [2, 3], [2, 4], [2, 5], [3, 4], [3, 5],
                           [4, 5]]},                            # K6 -> no
    ]
    for g in edge_cases:
        check(g, "edge-case")

    # 4. Explicit sanity checks on the documented edge cases.
    assert solve_three_coloring({"n": 0, "edges": []}) is True
    assert solve_three_coloring(
        {"n": 4, "edges": [[0, 1], [1, 2], [2, 3], [3, 0], [0, 2], [1, 3]]}
    ) is False
    assert solve_one_in_three({"num_vars": 0, "clauses": []}) is True
    assert solve_one_in_three({"num_vars": 3, "clauses": [[1, 2, 3]]}) is True
    assert solve_one_in_three(
        {"num_vars": 3, "clauses": [[1, 2, 3], [1, 2, 3]]}
    ) is True

    print(f"tests_run    = {tests_run}")
    print(f"tests_passed = {tests_passed}")
    if failures:
        print(f"FAILURES ({len(failures)}):")
        for label, inst, msg in failures[:20]:
            print(f"  [{label}] {inst} -> {msg}")
    else:
        print("All tests passed.")

    return tests_run, tests_passed, failures


if __name__ == "__main__":
    run, passed, fails = main()
    sys.exit(0 if not fails else 1)
