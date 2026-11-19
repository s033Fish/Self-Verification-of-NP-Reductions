"""Tests for the reduction from Hamiltonian Cycle to Hamiltonian Path.

The repository provides only validation for instances and a reduction
function.  To verify the reduction we implement brute‑force solvers for
both problems (suitable for tiny graphs) and compare the answer on the
original instance with the answer on the reduced instance for all
graphs up to 5 vertices.

The test script records the number of instances checked and how many
passed.  It writes a ``verdict.json`` file in the current directory with
the required fields.
"""

from __future__ import annotations

import itertools
import json
import sys
from typing import List

import problems
import reduce


def hamiltonian_cycle_bruteforce(instance: dict) -> bool:
    """Return True iff the graph has a Hamiltonian cycle.

    The implementation follows the definition in ``HamiltonianCycle``.
    It is exponential but only used for n ≤ 5.
    """
    n = instance["n"]
    edges = set(frozenset(e) for e in instance["edges"])

    # Edge cases from the problem statement
    if n <= 2:
        return False
    if n == 3:
        # Only a triangle qualifies
        return len(edges) == 3 and all(len(e) == 2 for e in edges)

    # Try all permutations of vertices as a cycle (starting point fixed to reduce duplicates)
    verts = list(range(n))
    for perm in itertools.permutations(verts[1:]):
        cycle = (0,) + perm
        ok = True
        for a, b in zip(cycle, cycle[1:] + (cycle[0],)):
            if frozenset((a, b)) not in edges:
                ok = False
                break
        if ok:
            return True
    return False


def hamiltonian_path_bruteforce(instance: dict) -> bool:
    """Return True iff the graph has a Hamiltonian path.

    Mirrors the definition in ``HamiltonianPath``.
    """
    n = instance["n"]
    edges = set(frozenset(e) for e in instance["edges"])

    if n == 0:
        return False
    if n == 1:
        return True
    if n == 2:
        return frozenset((0, 1)) in edges

    verts = list(range(n))
    for perm in itertools.permutations(verts):
        ok = True
        for a, b in zip(perm, perm[1:]):
            if frozenset((a, b)) not in edges:
                ok = False
                break
        if ok:
            return True
    return False


def all_graphs_up_to(max_n: int) -> List[dict]:
    """Generate every simple undirected graph with vertices 0..n-1 for n ≤ max_n.

    Each graph is represented as the instance dictionary expected by the
    problem validators.
    """
    instances: List[dict] = []
    for n in range(max_n + 1):
        possible_edges = [(u, v) for u in range(n) for v in range(u + 1, n)]
        for mask in range(1 << len(possible_edges)):
            edges = [list(possible_edges[i]) for i in range(len(possible_edges)) if (mask >> i) & 1]
            instances.append({"n": n, "edges": edges})
    return instances


def main() -> None:
    max_n = 5
    instances = all_graphs_up_to(max_n)
    total = len(instances)
    passed = 0

    for inst in instances:
        # Validate source instance (should always succeed)
        problems.HamiltonianCycle.validate(inst)
        source_ans = hamiltonian_cycle_bruteforce(inst)
        reduced = reduce.reduce(inst)
        # Validate target instance produced by reduction
        problems.HamiltonianPath.validate(reduced)
        target_ans = hamiltonian_path_bruteforce(reduced)
        if source_ans == target_ans:
            passed += 1
        else:
            print("Mismatch!", file=sys.stderr)
            print("source", inst, "=>", source_ans, file=sys.stderr)
            print("reduced", reduced, "=>", target_ans, file=sys.stderr)
            break

    verdict = {
        "verified": passed == total,
        "tests_run": total,
        "tests_passed": passed,
    }
    with open("verdict.json", "w", encoding="utf-8") as f:
        json.dump(verdict, f, indent=2)
    print(json.dumps(verdict, indent=2))

if __name__ == "__main__":
    main()
