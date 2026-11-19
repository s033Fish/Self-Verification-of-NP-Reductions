"""Test harness for the Hamiltonian Path → Hamiltonian Cycle reduction.

The file implements brute‑force solvers for both problems based directly on
the definitions in ``problems.py`` and then exhaustively checks all small
graphs (up to 5 vertices).  For each source instance we:

1. Validate the source instance using ``HamiltonianPath.validate``.
2. Reduce it via ``reduce``.
3. Validate the returned target instance using ``HamiltonianCycle.validate``.
4. Compare the answer of the source problem with the answer of the target
   problem; they must coincide.

The script writes a ``verdict.json`` file containing three fields:

* ``verified`` – ``true`` iff *all* tests passed.
* ``tests_run`` – total number of source instances examined.
* ``tests_passed`` – number of instances where the reduction preserved the
  answer.

The verification logic is deliberately simple and runs in well under a
second for the chosen bounds.
"""

from __future__ import annotations

import itertools
import json
from typing import List, Tuple

from problems import HamiltonianPath, HamiltonianCycle
from reduce import reduce as reduce_instance


def has_edge(edges_set: set[Tuple[int, int]], u: int, v: int) -> bool:
    """Return True if {u, v} is in the undirected edge set."""
    return (u, v) in edges_set or (v, u) in edges_set


def solve_hamiltonian_path(instance: dict) -> bool:
    n = instance["n"]
    edges = instance["edges"]
    if n == 0:
        return False
    if n == 1:
        return True
    edge_set = {tuple(e) for e in edges}
    vertices = list(range(n))
    for perm in itertools.permutations(vertices):
        good = True
        for a, b in zip(perm, perm[1:]):
            if not has_edge(edge_set, a, b):
                good = False
                break
        if good:
            return True
    return False


def solve_hamiltonian_cycle(instance: dict) -> bool:
    n = instance["n"]
    edges = instance["edges"]
    if n < 3:
        return False
    edge_set = {tuple(e) for e in edges}
    vertices = list(range(n))
    for perm in itertools.permutations(vertices):
        good = True
        for a, b in zip(perm, perm[1:]):
            if not has_edge(edge_set, a, b):
                good = False
                break
        if good and has_edge(edge_set, perm[-1], perm[0]):
            return True
    return False


def all_graphs(n: int) -> List[dict]:
    """Generate every simple undirected graph on ``n`` vertices.

    The representation matches the problem definition: a dict with keys
    ``"n"`` and ``"edges"`` where each edge is a two‑element list.
    """
    vertices = list(range(n))
    possible_edges = list(itertools.combinations(vertices, 2))
    graphs: List[dict] = []
    for mask in range(1 << len(possible_edges)):
        edges: List[List[int]] = []
        for i, (u, v) in enumerate(possible_edges):
            if mask & (1 << i):
                edges.append([u, v])
        graphs.append({"n": n, "edges": edges})
    return graphs


def main() -> None:
    tests_run = 0
    tests_passed = 0
    for n in range(0, 6):  # up to 5 vertices inclusive
        for src_instance in all_graphs(n):
            HamiltonianPath.validate(src_instance)
            src_answer = solve_hamiltonian_path(src_instance)
            tgt_instance = reduce_instance(src_instance)
            HamiltonianCycle.validate(tgt_instance)
            tgt_answer = solve_hamiltonian_cycle(tgt_instance)
            tests_run += 1
            if src_answer == tgt_answer:
                tests_passed += 1
            else:
                print("Mismatch!", src_instance, "=>", tgt_instance, src_answer, tgt_answer)
    verified = tests_run == tests_passed
    verdict = {"verified": verified, "tests_run": tests_run, "tests_passed": tests_passed}
    with open("verdict.json", "w", encoding="utf-8") as f:
        json.dump(verdict, f, indent=2)
    print(json.dumps(verdict, indent=2))

if __name__ == "__main__":
    main()

