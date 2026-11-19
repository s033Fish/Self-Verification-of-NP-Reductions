"""Tests for the Hamiltonian Path → Hamiltonian Cycle reduction.

The repository provides only validation functions for the two problems
and a ``reduce`` implementation. This test suite implements exhaustive
brute‑force solvers for both problems (suitable for tiny graphs) and
checks that the reduction preserves the answer on all instances with
``n`` up to 5.

The suite records the number of instances examined and whether all of
them passed. It also writes a ``verdict.json`` file with the required
information for the review task.
"""

from __future__ import annotations

import itertools
import json
import sys
from typing import List, Tuple

# Import the validation classes and the reduction function from the
# repository.
from problems import HamiltonianPath, HamiltonianCycle
from reduce import reduce as reduce_instance


def brute_force_hamiltonian_path(n: int, edges: List[Tuple[int, int]]) -> bool:
    """Return True iff the undirected graph has a Hamiltonian path.

    The implementation checks all permutations of the vertices. It is
    deliberately exponential but sufficient for the tiny graphs used in
    the test suite (n ≤ 5).
    """
    if n == 0:
        return False
    if n == 1:
        return True
    # Build adjacency set for O(1) edge lookup.
    adj = {i: set() for i in range(n)}
    for u, v in edges:
        adj[u].add(v)
        adj[v].add(u)
    for perm in itertools.permutations(range(n)):
        ok = True
        for a, b in zip(perm, perm[1:]):
            if b not in adj[a]:
                ok = False
                break
        if ok:
            return True
    return False


def brute_force_hamiltonian_cycle(n: int, edges: List[Tuple[int, int]]) -> bool:
    """Return True iff the undirected graph has a Hamiltonian cycle.

    For n ≤ 5 we again enumerate all permutations and require the wrap‑
    around edge between the last and first vertex.
    """
    if n < 3:
        return False
    adj = {i: set() for i in range(n)}
    for u, v in edges:
        adj[u].add(v)
        adj[v].add(u)
    for perm in itertools.permutations(range(n)):
        ok = True
        for a, b in zip(perm, perm[1:]):
            if b not in adj[a]:
                ok = False
                break
        # also need edge between last and first
        if ok and perm[0] in adj[perm[-1]]:
            return True
    return False


def all_graphs(n: int) -> List[List[Tuple[int, int]]]:
    """Generate every simple undirected graph on ``n`` vertices.

    The edges are represented as a list of ``(u, v)`` with ``u < v``.
    """
    vertices = list(range(n))
    possible_edges = [(u, v) for u in vertices for v in vertices if u < v]
    graphs: List[List[Tuple[int, int]]] = []
    for mask in range(1 << len(possible_edges)):
        edges = [possible_edges[i] for i in range(len(possible_edges)) if (mask >> i) & 1]
        graphs.append(edges)
    return graphs


def main() -> None:
    max_n = 5  # small enough for exhaustive enumeration
    total_tests = 0
    passed = 0

    for n in range(max_n + 1):
        for edges in all_graphs(n):
            total_tests += 1
            # Build source instance dict in the required format.
            src_instance = {"n": n, "edges": [[u, v] for u, v in edges]}
            # Validate source instance – should never raise.
            try:
                HamiltonianPath.validate(src_instance)
            except Exception as exc:
                print(f"Source validation failed for n={n}, edges={edges}: {exc}", file=sys.stderr)
                continue

            # Compute expected answers.
            path_yes = brute_force_hamiltonian_path(n, edges)
            # Reduce and validate target.
            tgt_instance = reduce_instance(src_instance)
            try:
                HamiltonianCycle.validate(tgt_instance)
            except Exception as exc:
                print(f"Target validation failed for reduced instance {tgt_instance}: {exc}", file=sys.stderr)
                continue
            # Compute target answer.
            n_t = tgt_instance["n"]
            edges_t = [(u, v) for u, v in tgt_instance["edges"]]
            cycle_yes = brute_force_hamiltonian_cycle(n_t, edges_t)
            if path_yes == cycle_yes:
                passed += 1
            else:
                print(
                    f"Mismatch for source n={n}, edges={edges}: path={path_yes}, reduced cycle={cycle_yes}",
                    file=sys.stderr,
                )

    verdict = {
        "verified": passed == total_tests,
        "tests_run": total_tests,
        "tests_passed": passed,
    }
    with open("verdict.json", "w", encoding="utf-8") as f:
        json.dump(verdict, f, indent=2)
    print(json.dumps(verdict, indent=2))


if __name__ == "__main__":
    main()

