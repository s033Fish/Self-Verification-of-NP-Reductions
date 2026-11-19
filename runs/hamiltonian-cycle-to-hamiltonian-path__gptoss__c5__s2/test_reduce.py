"""Automated tests for the reduction from HamiltonianCycle to HamiltonianPath.

The repository provides only validation functions for the two problems and a
reduction implementation that solves the source instance by brute force and
outputs a constant‑size target instance.  To verify the functional correctness
of the reduction we implement straightforward exponential‑time solvers for both
problems and compare the answers on all small graphs (up to 5 vertices).

The test suite:
  * Enumerates every undirected simple graph for n = 0..5.
  * Validates each instance using the problem classes.
  * Computes the correct answer for the source (Hamiltonian Cycle) and the
    target (Hamiltonian Path).
  * Applies ``reduce`` and checks that the reduced instance is valid and that
    its answer matches the source answer.
  * Counts the total number of tests and the number passed.

At the end a ``verdict.json`` file is written with the required fields.
"""

from __future__ import annotations

import itertools
import json
from typing import Dict, List

from problems import HamiltonianCycle, HamiltonianPath
from reduce import reduce as reduce_instance


def _has_hamiltonian_cycle(instance: Dict) -> bool:
    """Brute‑force check for a Hamiltonian cycle.

    This mirrors the implementation used inside ``reduce.py`` but is kept
    separate to avoid any accidental coupling.
    """
    n = instance["n"]
    edges = {frozenset(e) for e in instance["edges"]}
    if n <= 2:
        return False
    if n == 3:
        # The only possible cycle is the triangle.
        return all(frozenset([i, (i + 1) % 3]) in edges for i in range(3))
    for perm in itertools.permutations(range(n)):
        if all(frozenset([perm[i], perm[(i + 1) % n]]) in edges for i in range(n)):
            return True
    return False


def _has_hamiltonian_path(instance: Dict) -> bool:
    """Brute‑force check for a Hamiltonian path.

    The definition follows the problem statement in ``problems.py``.
    """
    n = instance["n"]
    edges = {frozenset(e) for e in instance["edges"]}
    if n == 0:
        return False
    if n == 1:
        return True
    if n == 2:
        return frozenset([0, 1]) in edges
    for perm in itertools.permutations(range(n)):
        if all(frozenset([perm[i], perm[i + 1]]) in edges for i in range(n - 1)):
            return True
    return False


def generate_all_graphs(max_n: int = 5) -> List[Dict]:
    """Generate every simple undirected graph for n in 0..max_n.

    Each graph is represented as a dictionary matching the instance format of
    the problems.
    """
    graphs: List[Dict] = []
    for n in range(max_n + 1):
        possible_edges = [(i, j) for i in range(n) for j in range(i + 1, n)]
        for mask in range(1 << len(possible_edges)):
            edges: List[List[int]] = []
            for idx, (u, v) in enumerate(possible_edges):
                if mask & (1 << idx):
                    edges.append([u, v])
            graphs.append({"n": n, "edges": edges})
    return graphs


def main() -> None:
    tests_run = 0
    tests_passed = 0
    for instance in generate_all_graphs(5):
        HamiltonianCycle.validate(instance)
        src_answer = _has_hamiltonian_cycle(instance)
        reduced = reduce_instance(instance)
        HamiltonianPath.validate(reduced)
        reduced_answer = _has_hamiltonian_path(reduced)
        tests_run += 1
        if reduced_answer == src_answer:
            tests_passed += 1
        else:
            print("FAILURE:")
            print("Original instance:", instance)
            print("Source answer (cycle):", src_answer)
            print("Reduced instance:", reduced)
            print("Reduced answer (path):", reduced_answer)
            break
    verdict = {
        "verified": tests_passed == tests_run,
        "tests_run": tests_run,
        "tests_passed": tests_passed,
    }
    with open("verdict.json", "w", encoding="utf-8") as f:
        json.dump(verdict, f, indent=2)
    print(json.dumps(verdict, indent=2))

if __name__ == "__main__":
    main()
