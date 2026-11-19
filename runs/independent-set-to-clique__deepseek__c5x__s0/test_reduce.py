"""Test the reduction from Independent Set to Clique.

This script implements brute‑force solvers for both problems and checks that
for a wide range of small instances the answer of the source instance matches
the answer of the reduced target instance returned by ``reduce``.

The script writes a ``verdict.json`` file with the following keys:

* ``verified`` – ``true`` iff all tests passed.
* ``tests_run`` – total number of instances tested.
* ``tests_passed`` – number of instances where the reduction gave the correct
  answer (should be equal to ``tests_run`` when ``verified`` is true).

The reduction is considered correct if for every instance the yes/no answer
is preserved.
"""

from __future__ import annotations

import itertools
import json
import sys
from typing import List, Tuple

# Import the problem definitions and the reduction implementation.
import problems  # noqa: F401  (ensures validation helpers are available)
from reduce import reduce as reduce_instance


def independent_set_solver(instance: dict) -> bool:
    """Brute‑force solver for Independent Set.

    Returns True iff the graph contains an independent set of size at least
    ``k``.
    """
    n: int = instance["n"]
    edges: List[Tuple[int, int]] = [tuple(e) for e in instance["edges"]]
    k: int = instance["k"]

    # Edge cases from the problem statement.
    if k <= 0:
        return True
    if k > n:
        return False
    if not edges:
        # No edges → any set is independent.
        return True

    # Build adjacency set for quick lookup.
    adj = {i: set() for i in range(n)}
    for u, v in edges:
        adj[u].add(v)
        adj[v].add(u)

    # Check all subsets of vertices.
    for size in range(k, n + 1):
        for subset in itertools.combinations(range(n), size):
            # Verify independence.
            independent = True
            for u, v in itertools.combinations(subset, 2):
                if v in adj[u]:
                    independent = False
                    break
            if independent:
                return True
    return False


def clique_solver(instance: dict) -> bool:
    """Brute‑force solver for Clique.

    Returns True iff the graph contains a clique of size at least ``k``.
    """
    n: int = instance["n"]
    edges: List[Tuple[int, int]] = [tuple(e) for e in instance["edges"]]
    k: int = instance["k"]

    # Edge cases from the problem statement.
    if k <= 0:
        return True
    if k == 1:
        return n >= 1
    if k > n:
        return False
    if not edges:
        # No edges → only cliques of size 1 exist.
        return k <= 1

    # Build adjacency set for quick lookup.
    adj = {i: set() for i in range(n)}
    for u, v in edges:
        adj[u].add(v)
        adj[v].add(u)

    for size in range(k, n + 1):
        for subset in itertools.combinations(range(n), size):
            # Verify that every pair is connected.
            is_clique = True
            for u, v in itertools.combinations(subset, 2):
                if v not in adj[u]:
                    is_clique = False
                    break
            if is_clique:
                return True
    return False


def generate_all_instances(max_n: int = 5) -> List[dict]:
    """Generate every graph with up to ``max_n`` vertices and various k values.

    For each ``n`` we enumerate all possible edge subsets (undirected, without
    self‑loops) and for each graph we test ``k`` ranging from -1 to ``n+2`` to
    cover edge cases.
    """
    instances: List[dict] = []
    for n in range(max_n + 1):
        vertices = list(range(n))
        possible_edges = [(u, v) for u in vertices for v in vertices if u < v]
        for edge_subset in itertools.chain.from_iterable(
            itertools.combinations(possible_edges, r) for r in range(len(possible_edges) + 1)
        ):
            edges = [[u, v] for u, v in edge_subset]
            for k in range(-1, n + 3):  # covers k <= 0, typical, and > n
                instances.append({"n": n, "edges": edges, "k": k})
    return instances


def main() -> None:
    instances = generate_all_instances(max_n=5)
    total = len(instances)
    passed = 0

    for src in instances:
        # Validate source instance (will raise if malformed).
        problems.IndependentSet.validate(src)
        src_ans = independent_set_solver(src)
        tgt = reduce_instance(src)
        # Validate target instance.
        problems.Clique.validate(tgt)
        tgt_ans = clique_solver(tgt)
        if src_ans == tgt_ans:
            passed += 1
        else:
            print("Mismatch found:")
            print("Source instance:", src)
            print("Reduced target:", tgt)
            print("IndependentSet answer:", src_ans)
            print("Clique answer:", tgt_ans)
            break

    verdict = {
        "verified": passed == total,
        "tests_run": total,
        "tests_passed": passed,
    }
    with open("verdict.json", "w") as f:
        json.dump(verdict, f, indent=2)
    print(json.dumps(verdict, indent=2))

if __name__ == "__main__":
    main()
