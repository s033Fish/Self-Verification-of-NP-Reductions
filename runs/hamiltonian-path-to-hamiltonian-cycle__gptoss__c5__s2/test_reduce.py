"""Tests for the Hamiltonian Path → Hamiltonian Cycle reduction.

The repository provides only validation code and a reduction implementation.
This test suite implements brute‑force solvers for both source and target
problems and checks that for a wide range of small instances the reduction
preserves the answer.

The test enumerates all simple undirected graphs with up to ``MAX_N``
vertices (inclusive). For each graph we construct the instance dicts as
required by the problem definitions, run the solvers, apply the reduction,
and verify that the target answer matches the source answer.

The script prints a JSON object ``verdict.json`` containing the verification
result required by the task description.
"""

from __future__ import annotations

import itertools
import json
import sys
from typing import List, Dict

from problems import HamiltonianPath, HamiltonianCycle
from reduce import reduce


def brute_hamiltonian_path(instance: Dict) -> bool:
    """Return True iff the graph has a Hamiltonian path.

    Implements the definition directly by enumerating all permutations of
    vertices. Suitable for the tiny graphs used in the tests.
    """
    n = instance["n"]
    edges = {frozenset(e) for e in instance["edges"]}
    if n == 0:
        return False
    if n == 1:
        return True
    # For each permutation, check consecutive adjacency.
    for perm in itertools.permutations(range(n)):
        ok = True
        for a, b in zip(perm, perm[1:]):
            if frozenset((a, b)) not in edges:
                ok = False
                break
        if ok:
            return True
    return False


def brute_hamiltonian_cycle(instance: Dict) -> bool:
    """Return True iff the graph has a Hamiltonian cycle.

    Enumerates permutations of vertices and checks that the edges exist
    between consecutive vertices and also between the last and first.
    """
    n = instance["n"]
    edges = {frozenset(e) for e in instance["edges"]}
    if n <= 2:
        return False
    for perm in itertools.permutations(range(n)):
        ok = True
        for a, b in zip(perm, perm[1:]):
            if frozenset((a, b)) not in edges:
                ok = False
                break
        # close the cycle
        if ok and frozenset((perm[-1], perm[0])) in edges:
            return True
    return False


def generate_all_graphs(n: int) -> List[Dict]:
    """Generate all simple undirected graphs on ``n`` vertices.

    Each graph is represented as the instance dict expected by the problem
    validators.
    """
    vertices = list(range(n))
    possible_edges = [(u, v) for u in vertices for v in vertices if u < v]
    instances: List[Dict] = []
    for mask in range(1 << len(possible_edges)):
        edges: List[List[int]] = []
        for i, (u, v) in enumerate(possible_edges):
            if mask & (1 << i):
                edges.append([u, v])
        instances.append({"n": n, "edges": edges})
    return instances


def main() -> None:
    MAX_N = 5  # keep runtime reasonable while covering many cases
    total_tests = 0
    passed_tests = 0

    for n in range(0, MAX_N + 1):
        for src_instance in generate_all_graphs(n):
            # Validate source instance (should never raise)
            HamiltonianPath.validate(src_instance)
            src_ans = brute_hamiltonian_path(src_instance)
            tgt_instance = reduce(src_instance)
            # Validate target instance produced by reduction
            HamiltonianCycle.validate(tgt_instance)
            tgt_ans = brute_hamiltonian_cycle(tgt_instance)
            total_tests += 1
            if src_ans == tgt_ans:
                passed_tests += 1
            else:
                # Print a diagnostic for debugging purposes
                print("Mismatch!", file=sys.stderr)
                print("source", src_instance, file=sys.stderr)
                print("source_ans", src_ans, file=sys.stderr)
                print("target", tgt_instance, file=sys.stderr)
                print("target_ans", tgt_ans, file=sys.stderr)
    verdict = {
        "verified": passed_tests == total_tests,
        "tests_run": total_tests,
        "tests_passed": passed_tests,
    }
    with open("verdict.json", "w") as f:
        json.dump(verdict, f)
    # Also output to stdout for visibility
    print(json.dumps(verdict))

if __name__ == "__main__":
    main()
