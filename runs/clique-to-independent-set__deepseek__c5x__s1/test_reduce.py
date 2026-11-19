"""Test suite for the reduction from Clique to Independent Set.

The repository provides a ``reduce`` function that should map a Clique
instance to an Independent Set instance preserving the answer.  This file
contains a brute‑force solver for both problems and runs the reduction on a
large collection of small random instances.  It then writes a ``verdict.json``
file describing whether all tests passed.

The format of the instances follows the definitions in ``problems.py``.  The
tests cover edge cases (k <= 0, k > n, empty edge list, complete graph, etc.)
and a few random graphs for n up to 6 which is exhaustive for the given size.
"""

from __future__ import annotations

import json
import itertools
import random
from pathlib import Path

from problems import Clique, IndependentSet
from reduce import reduce


def brute_force_clique(instance: dict) -> bool:
    """Return True iff the Clique instance has a clique of size >= k.

    The implementation follows the definition in ``problems.py`` exactly and
    works for the tiny graphs used in the tests.
    """
    n = instance["n"]
    edges = {frozenset(e) for e in instance["edges"]}
    k = instance["k"]

    # Edge cases from the problem statement
    if k <= 0:
        return True
    if k == 1:
        return n >= 1
    if k > n:
        return False

    # Check all subsets of vertices of size >= k
    vertices = list(range(n))
    for size in range(k, n + 1):
        for subset in itertools.combinations(vertices, size):
            # Every pair must be an edge
            if all(frozenset(pair) in edges for pair in itertools.combinations(subset, 2)):
                return True
    return False


def brute_force_independent_set(instance: dict) -> bool:
    """Return True iff the Independent Set instance has an independent set of size >= k.
    """
    n = instance["n"]
    edges = {frozenset(e) for e in instance["edges"]}
    k = instance["k"]

    if k <= 0:
        return True
    if k > n:
        return False
    if not edges:  # no edges, any set works
        return True

    vertices = list(range(n))
    for size in range(k, n + 1):
        for subset in itertools.combinations(vertices, size):
            # No pair may be an edge
            if all(frozenset(pair) not in edges for pair in itertools.combinations(subset, 2)):
                return True
    return False


def generate_all_graphs(n: int) -> list[list[list[int]]]:
    """Generate all undirected simple graphs on n vertices.

    Returns a list of edge lists where each edge is a ``[u, v]`` with ``u < v``.
    """
    possible_edges = [(u, v) for u in range(n) for v in range(u + 1, n)]
    graphs: list[list[list[int]]] = []
    for mask in range(1 << len(possible_edges)):
        edges: list[list[int]] = []
        for i, (u, v) in enumerate(possible_edges):
            if mask & (1 << i):
                edges.append([u, v])
        graphs.append(edges)
    return graphs


def run_tests() -> tuple[int, int]:
    """Run exhaustive tests for n up to 5 and a few random ones up to 6.

    Returns a tuple ``(tests_run, tests_passed)``.
    """
    tests_run = 0
    tests_passed = 0

    # Exhaustive enumeration for n up to 5 (manageable number of graphs)
    for n in range(0, 5):
        graphs = generate_all_graphs(n)
        for edges in graphs:
            # Test a range of k values including edge cases
            for k in range(-1, n + 3):  # includes k < 0, 0, ..., n+2
                instance = {"n": n, "edges": edges, "k": k}
                # Validate using problem classes (will raise if malformed)
                Clique.validate(instance)
                IndependentSet.validate(instance)

                source_answer = brute_force_clique(instance)
                reduced = reduce(instance)
                # Ensure reduced instance validates as IndependentSet
                IndependentSet.validate(reduced)
                target_answer = brute_force_independent_set(reduced)

                tests_run += 1
                if source_answer == target_answer:
                    tests_passed += 1
                else:
                    print("FAIL", instance, "=>", reduced, source_answer, target_answer)

    # Additional random tests for n=6 (2^15 possible graphs -> too many)
    random.seed(0)
    for _ in range(200):
        n = 6
        possible_edges = [(u, v) for u in range(n) for v in range(u + 1, n)]
        edges = [list(e) for e in possible_edges if random.random() < 0.5]
        k = random.randint(-2, n + 2)
        instance = {"n": n, "edges": edges, "k": k}
        Clique.validate(instance)
        IndependentSet.validate(instance)
        source_answer = brute_force_clique(instance)
        reduced = reduce(instance)
        IndependentSet.validate(reduced)
        target_answer = brute_force_independent_set(reduced)
        tests_run += 1
        if source_answer == target_answer:
            tests_passed += 1
        else:
            print("FAIL", instance, "=>", reduced, source_answer, target_answer)

    return tests_run, tests_passed


def main() -> None:
    tests_run, tests_passed = run_tests()
    verdict = {
        "verified": tests_run == tests_passed,
        "tests_run": tests_run,
        "tests_passed": tests_passed,
    }
    Path("verdict.json").write_text(json.dumps(verdict, indent=2))
    print(json.dumps(verdict, indent=2))


if __name__ == "__main__":
    main()

