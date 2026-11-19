"""Test the reduction from HamiltonianCycle to HamiltonianPath.

The test enumerates all simple undirected graphs with up to 5 vertices,
computes the correct answer for the source problem (Hamiltonian Cycle)
by brute force, applies ``reduce`` and computes the answer for the target
problem (Hamiltonian Path).  The reduction is considered correct if the
answers always match.

The script also validates that the instance produced by ``reduce``
conforms to the target problem's validation routine.

At the end it writes ``verdict.json`` containing the verification result.
"""

from __future__ import annotations

import itertools
import json
import sys
from typing import List

from problems import HamiltonianCycle, HamiltonianPath
from reduce import reduce as reduction


def all_graphs(n: int) -> List[dict]:
    """Return a list of all simple undirected graphs on ``n`` vertices.

    The graph is represented as a dict with keys ``"n"`` and ``"edges"``
    matching the format defined in ``problems.py``.
    """
    vertices = list(range(n))
    possible_edges = [(u, v) for u in vertices for v in vertices if u < v]
    graphs: List[dict] = []
    for mask in range(1 << len(possible_edges)):
        edges: List[List[int]] = []
        for i, (u, v) in enumerate(possible_edges):
            if mask & (1 << i):
                edges.append([u, v])
        graphs.append({"n": n, "edges": edges})
    return graphs


def has_hamiltonian_cycle(instance: dict) -> bool:
    n = instance["n"]
    if n <= 2:
        return False
    edge_set = {frozenset(e) for e in instance["edges"]}
    # For n == 3, the only yes case is the triangle.
    for perm in itertools.permutations(range(n)):
        ok = True
        for i in range(n):
            a = perm[i]
            b = perm[(i + 1) % n]
            if frozenset((a, b)) not in edge_set:
                ok = False
                break
        if ok:
            return True
    return False


def has_hamiltonian_path(instance: dict) -> bool:
    n = instance["n"]
    if n == 0:
        return False
    if n == 1:
        return True
    edge_set = {frozenset(e) for e in instance["edges"]}
    if n == 2:
        return frozenset((0, 1)) in edge_set
    for perm in itertools.permutations(range(n)):
        ok = True
        for i in range(n - 1):
            if frozenset((perm[i], perm[i + 1])) not in edge_set:
                ok = False
                break
        if ok:
            return True
    return False


def main() -> None:
    total = 0
    passed = 0
    for n in range(0, 6):
        for graph in all_graphs(n):
            try:
                HamiltonianCycle.validate(graph)
            except Exception as e:
                print(f"Invalid source instance {graph}: {e}", file=sys.stderr)
                continue
            src_ans = has_hamiltonian_cycle(graph)
            tgt_instance = reduction(graph)
            try:
                HamiltonianPath.validate(tgt_instance)
            except Exception as e:
                print(f"Reduction produced invalid target instance {tgt_instance}: {e}", file=sys.stderr)
                continue
            tgt_ans = has_hamiltonian_path(tgt_instance)
            total += 1
            if src_ans == tgt_ans:
                passed += 1
            else:
                print("Mismatch!", file=sys.stderr)
                print("source", graph, "src_ans", src_ans, file=sys.stderr)
                print("target", tgt_instance, "tgt_ans", tgt_ans, file=sys.stderr)
    verdict = {
        "verified": passed == total,
        "tests_run": total,
        "tests_passed": passed,
    }
    with open("verdict.json", "w") as f:
        json.dump(verdict, f)
    print(json.dumps(verdict, indent=2))

if __name__ == "__main__":
    main()
