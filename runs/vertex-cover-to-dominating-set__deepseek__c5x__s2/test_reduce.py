"""Test suite for the reduction from VertexCover to DominatingSet.

The tests generate a variety of small graph instances, run a brute‑force
solver for the source problem (Vertex Cover) and for the target problem
(Dominating Set), apply the provided ``reduce`` function, and verify that
the answers match the theoretical equivalence described in ``reduce.py``.

If every generated instance satisfies the equivalence, the reduction is
considered verified.
"""

from __future__ import annotations

import itertools
import json
import sys
from pathlib import Path

import problems
from reduce import reduce


def vertex_cover_bruteforce(instance: dict) -> bool:
    """Return True iff the Vertex Cover instance has a cover of size <= k.

    The instance follows the format defined in ``problems.VertexCover``.
    """
    n = instance["n"]
    edges = [(u, v) for u, v in instance["edges"]]
    k = instance["k"]

    if k < 0:
        return False
    if not edges:
        # Empty edge set is always covered by the empty set.
        return k >= 0
    if k >= n:
        return True

    # Enumerate subsets up to size k.
    vertices = list(range(n))
    for r in range(k + 1):
        for subset in itertools.combinations(vertices, r):
            covered = True
            subset_set = set(subset)
            for u, v in edges:
                if u not in subset_set and v not in subset_set:
                    covered = False
                    break
            if covered:
                return True
    return False


def dominating_set_bruteforce(instance: dict) -> bool:
    """Return True iff the Dominating Set instance has a dominating set of size <= k.
    """
    n = instance["n"]
    edges = [(u, v) for u, v in instance["edges"]]
    k = instance["k"]

    if k < 0:
        return False
    if n == 0:
        return k >= 0
    if k >= n:
        return True

    # Build adjacency list including self (a vertex dominates itself).
    adj = [set() for _ in range(n)]
    for i in range(n):
        adj[i].add(i)
    for u, v in edges:
        adj[u].add(v)
        adj[v].add(u)

    vertices = list(range(n))
    for r in range(k + 1):
        for subset in itertools.combinations(vertices, r):
            dominated = set()
            for v in subset:
                dominated.update(adj[v])
            if len(dominated) == n:
                return True
    return False


def generate_all_graphs(max_n: int):
    """Yield all simple undirected graph instances with up to ``max_n`` vertices.

    For each ``n`` in ``0..max_n`` we iterate over all subsets of the possible
    edges ``{(i, j) | 0 <= i < j < n}``. For each graph we also iterate over a
    range of ``k`` values covering edge cases.
    """
    for n in range(max_n + 1):
        possible_edges = [(i, j) for i in range(n) for j in range(i + 1, n)]
        for edge_mask in range(1 << len(possible_edges)):
            edges = [list(possible_edges[i]) for i in range(len(possible_edges)) if (edge_mask >> i) & 1]
            # Choose a variety of k values: -1, 0, len(edges), n, n+1
            ks = set([-1, 0, len(edges), n, n + 1])
            # also a few values around half of n
            ks.add(n // 2)
            for k in ks:
                instance = {"n": n, "edges": edges, "k": k}
                yield instance


def main() -> None:
    total = 0
    passed = 0
    for src in generate_all_graphs(5):
        total += 1
        # Validate source instance (should not raise)
        problems.VertexCover.validate(src)
        src_answer = vertex_cover_bruteforce(src)
        tgt = reduce(src)
        # Validate target instance
        problems.DominatingSet.validate(tgt)
        tgt_answer = dominating_set_bruteforce(tgt)
        if src_answer == tgt_answer:
            passed += 1
        else:
            # Print a diagnostic and break for debugging.
            print("Mismatch found!", file=sys.stderr)
            print("Source:", json.dumps(src), file=sys.stderr)
            print("Reduced:", json.dumps(tgt), file=sys.stderr)
            print("src_answer", src_answer, "tgt_answer", tgt_answer, file=sys.stderr)
            break
    # Write verdict.json
    verdict = {
        "verified": passed == total,
        "tests_run": total,
        "tests_passed": passed,
    }
    Path("verdict.json").write_text(json.dumps(verdict, indent=2))
    # Exit with non‑zero code if not verified to signal failure.
    sys.exit(0 if verdict["verified"] else 1)

if __name__ == "__main__":
    main()
