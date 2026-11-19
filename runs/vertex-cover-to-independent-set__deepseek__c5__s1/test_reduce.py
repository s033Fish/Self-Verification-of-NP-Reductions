"""Independent verification of reduce.py (Vertex Cover -> Independent Set).

We implement brute-force solvers directly from the problem definitions in
problems.py, generate many small Vertex Cover instances, reduce them, and
check that the source and target answers agree.
"""

from __future__ import annotations

import itertools
import random

from problems import VertexCover, IndependentSet
from reduce import reduce


# ----------------------------------------------------------------------
# Brute-force solvers written from the definitions (no solvers in problems.py)
# ----------------------------------------------------------------------

def _edges_as_sets(instance):
    return [frozenset(e) for e in instance["edges"]]


def solve_vertex_cover(instance) -> bool:
    """Yes iff there is a vertex cover of AT MOST k vertices."""
    n = instance["n"]
    k = instance["k"]
    edges = _edges_as_sets(instance)
    if k < 0:
        return False
    if k >= n:
        return True
    for size in range(0, k + 1):
        for combo in itertools.combinations(range(n), size):
            chosen = set(combo)
            if all((e & chosen) for e in edges):
                return True
    return False


def solve_independent_set(instance) -> bool:
    """Yes iff there is an independent set of AT LEAST k vertices."""
    n = instance["n"]
    k = instance["k"]
    edges = _edges_as_sets(instance)
    if k <= 0:
        return True
    if k > n:
        return False
    for size in range(k, n + 1):
        for combo in itertools.combinations(range(n), size):
            chosen = set(combo)
            if all(not (e <= chosen) for e in edges):
                return True
    return False


SOLVERS = {VertexCover: solve_vertex_cover, IndependentSet: solve_independent_set}


# ----------------------------------------------------------------------
# Instance generation
# ----------------------------------------------------------------------

def random_graph(rng, n, p):
    edges = []
    for u in range(n):
        for v in range(u + 1, n):
            if rng.random() < p:
                edges.append([u, v])
    rng.shuffle(edges)
    return edges


def all_graphs(n):
    """All simple graphs on n labelled vertices."""
    pairs = [(u, v) for u in range(n) for v in range(u + 1, n)]
    for mask in range(1 << len(pairs)):
        edges = [list(pairs[i]) for i in range(len(pairs)) if mask & (1 << i)]
        yield edges


def generate_instances():
    rng = random.Random(12345)
    instances = []

    # Exhaustive: all graphs for n = 0..4, all k in a wide range.
    for n in range(0, 5):
        for edges in all_graphs(n):
            for k in range(-3, n + 4):
                instances.append({"n": n, "edges": [list(e) for e in edges], "k": k})

    # Random: n = 5..7, random densities, random k.
    for _ in range(1500):
        n = rng.randint(5, 7)
        p = rng.choice([0.0, 0.1, 0.25, 0.5, 0.75, 1.0])
        edges = random_graph(rng, n, p)
        k = rng.randint(-2, n + 2)
        instances.append({"n": n, "edges": edges, "k": k})

    # Special structures: empty graph, complete graph, paths, stars, matching.
    for n in range(0, 8):
        specials = []
        specials.append([])  # empty
        specials.append([[u, v] for u in range(n) for v in range(u + 1, n)])  # complete
        specials.append([[i, i + 1] for i in range(n - 1)])  # path
        specials.append([[0, v] for v in range(1, n)])  # star
        specials.append([[2 * i, 2 * i + 1] for i in range(n // 2)])  # matching
        for edges in specials:
            for k in range(-2, n + 3):
                instances.append({"n": n, "edges": [list(e) for e in edges], "k": k})

    return instances


# ----------------------------------------------------------------------
# Tests
# ----------------------------------------------------------------------

def main():
    instances = generate_instances()
    tests_run = 0
    tests_passed = 0
    failures = []

    for inst in instances:
        # The source instance must be valid.
        VertexCover.validate(inst)

        source_answer = SOLVERS[VertexCover](inst)

        # reduce must be callable and produce a valid target instance.
        reduced = reduce(inst)
        IndependentSet.validate(reduced)

        target_answer = SOLVERS[IndependentSet](reduced)

        tests_run += 1
        if source_answer == target_answer:
            tests_passed += 1
        else:
            failures.append((inst, reduced, source_answer, target_answer))

    # Structural checks on the reduction itself.
    structural_checks = []
    for inst in instances[:200]:
        reduced = reduce(inst)
        structural_checks.append(
            reduced["n"] == inst["n"]
            and sorted(map(tuple, reduced["edges"])) == sorted(map(tuple, inst["edges"]))
            and reduced["k"] == inst["n"] - inst["k"]
        )
    structural_ok = all(structural_checks)
    tests_run += 1
    if structural_ok:
        tests_passed += 1
    else:
        failures.append(("structural check failed",))

    # reduce must not mutate the input instance.
    mutation_ok = True
    for inst in instances[:200]:
        snapshot = {"n": inst["n"], "edges": [list(e) for e in inst["edges"]], "k": inst["k"]}
        reduce(inst)
        if inst != snapshot:
            mutation_ok = False
            break
    tests_run += 1
    if mutation_ok:
        tests_passed += 1
    else:
        failures.append(("reduce mutated its input",))

    print(f"tests_run={tests_run} tests_passed={tests_passed}")
    if failures:
        print("FAILURES (showing up to 10):")
        for f in failures[:10]:
            print("  ", f)
    else:
        print("All checks passed.")

    return tests_run, tests_passed, failures


if __name__ == "__main__":
    main()
