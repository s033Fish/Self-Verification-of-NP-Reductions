"""Test the reduction from Hamiltonian Cycle to Hamiltonian Path.

The repository provides only validation helpers and the reduction itself.
We implement exhaustive brute‑force solvers for the source and target
problems on small graphs and verify that for every generated instance the
answer of the source equals the answer of the reduced target instance.

The test enumerates all simple undirected graphs with up to ``MAX_N``
vertices (``MAX_N = 5``).  For each graph we:

1. Validate the source instance using ``HamiltonianCycle.validate``.
2. Compute the expected answer with ``hamiltonian_cycle_bruteforce``.
3. Apply ``reduce`` to obtain a target instance.
4. Validate the target instance using ``HamiltonianPath.validate``.
5. Compute the expected answer for the target with
   ``hamiltonian_path_bruteforce``.
6. Compare the two answers.

If any discrepancy is found the test records a failure.  At the end we
write ``verdict.json`` containing the verification result, the number of
tests run and the number of passed tests.
"""

from __future__ import annotations

import itertools
import json
import sys
from typing import List, Tuple

from problems import HamiltonianCycle, HamiltonianPath
from reduce import reduce as reduce_instance


def all_graphs(n: int) -> List[dict]:
    """Return a list of all simple undirected graphs on ``n`` vertices.

    Each graph is represented as ``{"n": n, "edges": [[u, v], ...]}``.
    ``n`` may be zero, in which case the only graph is the empty one.
    """
    vertices = list(range(n))
    possible_edges = [(i, j) for i in vertices for j in vertices if i < j]
    graphs: List[dict] = []
    for mask in range(1 << len(possible_edges)):
        edges: List[List[int]] = []
        for bit, (u, v) in enumerate(possible_edges):
            if mask & (1 << bit):
                edges.append([u, v])
        graphs.append({"n": n, "edges": edges})
    return graphs


def hamiltonian_cycle_bruteforce(instance: dict) -> bool:
    n = instance["n"]
    edges = set(frozenset(e) for e in instance["edges"])
    if n < 3:
        return False
    # Fix start vertex to 0 to avoid duplicate cycles.
    for perm in itertools.permutations(range(1, n)):
        cycle = (0,) + perm
        ok = True
        for a, b in zip(cycle, cycle[1:]):
            if frozenset((a, b)) not in edges:
                ok = False
                break
        # edge from last back to first
        if ok and frozenset((cycle[-1], cycle[0])) not in edges:
            ok = False
        if ok:
            return True
    return False


def hamiltonian_path_bruteforce(instance: dict) -> bool:
    n = instance["n"]
    edges = set(frozenset(e) for e in instance["edges"])
    if n == 0:
        return False
    if n == 1:
        return True
    if n == 2:
        return frozenset((0, 1)) in edges
    for perm in itertools.permutations(range(n)):
        ok = True
        for a, b in zip(perm, perm[1:]):
            if frozenset((a, b)) not in edges:
                ok = False
                break
        if ok:
            return True
    return False


def main() -> None:
    MAX_N = 5
    total_tests = 0
    passed = 0
    failures: List[Tuple[dict, dict, bool, bool]] = []

    for n in range(MAX_N + 1):
        for src_instance in all_graphs(n):
            total_tests += 1
            # Validate source instance (should never raise).
            HamiltonianCycle.validate(src_instance)
            src_ans = hamiltonian_cycle_bruteforce(src_instance)

            tgt_instance = reduce_instance(src_instance)
            # Validate target instance.
            HamiltonianPath.validate(tgt_instance)
            tgt_ans = hamiltonian_path_bruteforce(tgt_instance)

            if src_ans == tgt_ans:
                passed += 1
            else:
                failures.append((src_instance, tgt_instance, src_ans, tgt_ans))

    verdict = {
        "verified": passed == total_tests,
        "tests_run": total_tests,
        "tests_passed": passed,
    }
    # Write verdict
    with open("verdict.json", "w", encoding="utf-8") as f:
        json.dump(verdict, f, indent=2)

    if failures:
        print(f"{len(failures)} failures detected (out of {total_tests} tests)", file=sys.stderr)
        for src, tgt, src_ans, tgt_ans in failures[:5]:
            print("Source instance:", src, file=sys.stderr)
            print("Reduced target instance:", tgt, file=sys.stderr)
            print("Source answer:", src_ans, "Target answer:", tgt_ans, file=sys.stderr)

if __name__ == "__main__":
    main()

