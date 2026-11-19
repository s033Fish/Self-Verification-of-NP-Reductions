"""Automated tests for the reduction from ThreeColoring to IndependentSet.

The script implements exhaustive brute‑force solvers for both problems and
checks that for a large collection of small instances the answer to the
source instance matches the answer to the reduced target instance.

If every test passes we write a ``verdict.json`` file indicating success.
"""

from __future__ import annotations

import itertools
import json
import sys
from pathlib import Path

# Import the problem definitions and the reduction implementation.
from problems import ThreeColoring, IndependentSet, InvalidInstance
from reduce import reduce


def three_coloring_bruteforce(instance: dict) -> bool:
    """Return True iff the graph is 3‑colorable.

    A straightforward enumeration of all 3^n colour assignments is used.
    ``instance`` is assumed to be validated already.
    """
    n = instance["n"]
    edges = instance["edges"]
    # Edge cases from the problem statement – they are handled automatically
    # by the enumeration, but we keep them for clarity and speed.
    if n == 0:
        return True
    if n <= 3:
        return True

    # Enumerate colourings as numbers 0,1,2.
    for coloring in itertools.product(range(3), repeat=n):
        ok = True
        for u, v in edges:
            if coloring[u] == coloring[v]:
                ok = False
                break
        if ok:
            return True
    return False


def independent_set_bruteforce(instance: dict) -> bool:
    """Return True iff the graph has an independent set of size at least k.
    """
    n = instance["n"]
    edges = instance["edges"]
    k = instance["k"]
    if k <= 0:
        return True
    if k > n:
        return False
    # Build adjacency set for quick lookup.
    adj = [set() for _ in range(n)]
    for u, v in edges:
        adj[u].add(v)
        adj[v].add(u)

    # Check all subsets of size >= k (we can stop early when found).
    for size in range(k, n + 1):
        for subset in itertools.combinations(range(n), size):
            # Verify independence.
            independent = True
            for i, u in enumerate(subset):
                for v in subset[i + 1 :]:
                    if v in adj[u]:
                        independent = False
                        break
                if not independent:
                    break
            if independent:
                return True
    return False


def generate_all_graphs(n: int):
    """Yield all simple undirected graphs on ``n`` vertices.

    Each graph is represented as a dict with keys ``"n"`` and ``"edges"``.
    """
    vertices = list(range(n))
    possible_edges = [(i, j) for i in vertices for j in vertices if i < j]
    for mask in range(1 << len(possible_edges)):
        edges = []
        for bit, (u, v) in enumerate(possible_edges):
            if mask & (1 << bit):
                edges.append([u, v])
        yield {"n": n, "edges": edges}


def main() -> None:
    total_tests = 0
    passed_tests = 0

    # Exhaustively test n up to 5 (5 vertices => 2^10 = 1024 graphs).
    for n in range(0, 6):
        for src_instance in generate_all_graphs(n):
            total_tests += 1
            # Validate source instance (should never raise).
            try:
                ThreeColoring.validate(src_instance)
            except InvalidInstance as exc:
                print(f"Invalid source instance generated: {exc}", file=sys.stderr)
                continue

            src_answer = three_coloring_bruteforce(src_instance)
            # Reduce and validate target.
            try:
                tgt_instance = reduce(src_instance)
                IndependentSet.validate(tgt_instance)
            except Exception as exc:
                print(f"Reduction/validation failed: {exc}", file=sys.stderr)
                continue
            tgt_answer = independent_set_bruteforce(tgt_instance)
            if src_answer == tgt_answer:
                passed_tests += 1
            else:
                print("Mismatch!", src_instance, tgt_instance, src_answer, tgt_answer, file=sys.stderr)

    # Additionally run a few random larger instances (n up to 8) to increase confidence.
    import random
    random.seed(0)
    for _ in range(200):
        n = random.randint(0, 8)
        possible_edges = [(i, j) for i in range(n) for j in range(i + 1, n)]
        edges = []
        for (u, v) in possible_edges:
            if random.random() < 0.3:
                edges.append([u, v])
        src_instance = {"n": n, "edges": edges}
        total_tests += 1
        try:
            ThreeColoring.validate(src_instance)
        except InvalidInstance:
            continue
        src_answer = three_coloring_bruteforce(src_instance)
        tgt_instance = reduce(src_instance)
        IndependentSet.validate(tgt_instance)
        tgt_answer = independent_set_bruteforce(tgt_instance)
        if src_answer == tgt_answer:
            passed_tests += 1
        else:
            print("Random mismatch!", src_instance, tgt_instance, src_answer, tgt_answer, file=sys.stderr)

    verdict = {
        "verified": passed_tests == total_tests,
        "tests_run": total_tests,
        "tests_passed": passed_tests,
    }
    Path("verdict.json").write_text(json.dumps(verdict, indent=2))
    print(json.dumps(verdict, indent=2))

if __name__ == "__main__":
    main()
