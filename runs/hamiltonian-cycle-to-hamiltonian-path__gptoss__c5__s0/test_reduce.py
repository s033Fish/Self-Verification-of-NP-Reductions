"""Test suite for the reduction from HamiltonianCycle to HamiltonianPath.

The reduction implementation in ``reduce.py`` uses a brute‑force check to
determine whether the source instance has a Hamiltonian cycle and then returns
either a triangle (YES) or the empty graph (NO).  To verify correctness we
implement independent brute‑force solvers for both problems and compare the
answers on all small graphs (up to 5 vertices).  For each instance we ensure
that:

* ``reduce`` does not raise an exception and returns a valid target instance.
* The answer of the reduced instance (according to our solver) matches the
  answer of the original instance.

The script prints a JSON object ``verdict.json`` required by the task
description.
"""

from __future__ import annotations

import itertools
import json
import sys
from typing import Dict, List, Tuple

from problems import HamiltonianCycle, HamiltonianPath
from reduce import reduce as reduce_instance


def solve_hamiltonian_cycle(instance: Dict) -> bool:
    """Brute‑force solver for Hamiltonian Cycle.

    Returns True iff there exists a cycle that visits every vertex exactly once
    and returns to its start.
    """
    n = instance["n"]
    edges = instance["edges"]
    # Edge cases per problem statement
    if n <= 2:
        return False
    if n == 3:
        required = {frozenset([0, 1]), frozenset([0, 2]), frozenset([1, 2])}
        return required.issubset({frozenset(e) for e in edges})
    edge_set = {frozenset(e) for e in edges}
    verts = list(range(n))
    # fix first vertex to avoid cyclic permutations
    for perm in itertools.permutations(verts[1:]):
        path = (0,) + perm
        if all(frozenset([path[i], path[(i + 1) % n]]) in edge_set for i in range(n)):
            return True
    return False


def solve_hamiltonian_path(instance: Dict) -> bool:
    """Brute‑force solver for Hamiltonian Path.

    Returns True iff there exists a simple path visiting every vertex exactly
    once (endpoints are unrestricted).
    """
    n = instance["n"]
    edges = instance["edges"]
    # Edge cases per problem statement
    if n == 0:
        return False
    if n == 1:
        return True
    if n == 2:
        # only YES if the single possible edge exists
        return [0, 1] in edges or [1, 0] in edges
    edge_set = {frozenset(e) for e in edges}
    verts = list(range(n))
    for perm in itertools.permutations(verts):
        if all(frozenset([perm[i], perm[i + 1]]) in edge_set for i in range(n - 1)):
            return True
    return False


def generate_all_graphs(n: int) -> List[Dict]:
    """Generate all simple undirected graphs on ``n`` vertices.

    Each graph is represented as a dict matching the problem instance format.
    """
    vertices = list(range(n))
    possible_edges = list(itertools.combinations(vertices, 2))
    graphs: List[Dict] = []
    for mask in range(1 << len(possible_edges)):
        edges: List[List[int]] = []
        for i, (u, v) in enumerate(possible_edges):
            if mask & (1 << i):
                edges.append([u, v])
        graphs.append({"n": n, "edges": edges})
    return graphs


def main() -> None:
    total = 0
    passed = 0
    failures: List[Tuple[Dict, Dict, bool, bool, bool]] = []

    # Test all graphs for n = 0..5 (manageable total 1 + 1 + 2 + 8 + 64 + 1024 = 1110)
    for n in range(0, 6):
        for instance in generate_all_graphs(n):
            total += 1
            # Validate source instance (should always be valid)
            try:
                HamiltonianCycle.validate(instance)
            except Exception as e:
                print("Invalid source instance", instance, e, file=sys.stderr)
                continue
            source_ans = solve_hamiltonian_cycle(instance)
            # Apply reduction
            try:
                reduced = reduce_instance(instance)
                HamiltonianPath.validate(reduced)
            except Exception as e:
                failures.append((instance, {}, source_ans, False, False))
                continue
            target_ans = solve_hamiltonian_path(reduced)
            if source_ans == target_ans:
                passed += 1
            else:
                failures.append((instance, reduced, source_ans, target_ans, False))

    verdict = {
        "verified": passed == total,
        "tests_run": total,
        "tests_passed": passed,
    }
    # Write verdict.json
    with open("verdict.json", "w", encoding="utf-8") as f:
        json.dump(verdict, f, indent=2)
    # Also print a summary for human readers
    print(json.dumps(verdict, indent=2))
    if not verdict["verified"]:
        print(f"{len(failures)} failures (showing up to 5):", file=sys.stderr)
        for fail in failures[:5]:
            print(fail, file=sys.stderr)

if __name__ == "__main__":
    main()

