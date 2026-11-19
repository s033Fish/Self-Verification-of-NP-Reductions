"""Test the reduction from Clique to VertexCover.

The repository provides a ``reduce`` function that should transform any
Clique instance into an equivalent VertexCover instance.  This script
implements brute‑force solvers for both problems (suitable for tiny
instances) and checks that the answer of the reduced instance matches the
answer of the original instance on a wide range of randomly generated
graphs.

The script prints the number of tests run and the number passed.  It also
creates ``verdict.json`` in the repository root with the required fields:

    {"verified": <bool>, "tests_run": <int>, "tests_passed": <int>}

The ``verified`` flag is true only if **all** generated tests succeed.
"""

from __future__ import annotations

import json
import random
import itertools
import sys
from typing import List, Dict

from problems import Clique, VertexCover
from reduce import reduce as reduce_instance


def brute_clique(instance: Dict) -> bool:
    """Return True iff the Clique instance is a yes‑instance.

    Implements the definition directly by enumerating subsets.  Suitable for
    tiny graphs (n ≤ 8) used in the tests.
    """
    n = instance["n"]
    edges = set(frozenset(e) for e in instance["edges"])
    k = instance["k"]

    # Edge cases from the problem statement
    if k <= 0:
        return True
    if k == 1:
        return n >= 1
    if k > n:
        return False

    # Search for any subset of size >= k that forms a clique.
    vertices = list(range(n))
    for size in range(k, n + 1):
        for subset in itertools.combinations(vertices, size):
            # Check all unordered pairs are edges.
            if all(frozenset((u, v)) in edges for u, v in itertools.combinations(subset, 2)):
                return True
    return False


def brute_vertex_cover(instance: Dict) -> bool:
    """Return True iff the VertexCover instance is a yes‑instance.

    Enumerates subsets of vertices up to size k and checks if they cover all
    edges.
    """
    n = instance["n"]
    edges = [tuple(e) for e in instance["edges"]]
    k = instance["k"]

    # Edge cases from the problem statement
    if k < 0:
        return False
    if not edges:
        return True  # empty edge set is always covered
    if k >= n:
        return True

    vertices = list(range(n))
    # Try all subset sizes up to k.
    for size in range(0, k + 1):
        for subset in itertools.combinations(vertices, size):
            covered = True
            subset_set = set(subset)
            for u, v in edges:
                if u not in subset_set and v not in subset_set:
                    covered = False
                    break
            if covered:
                return True
    return False


def random_instance(max_n: int = 6) -> Dict:
    """Generate a random Clique instance.

    The graph is simple and undirected.  ``k`` is chosen in a range that
    includes values below 0 and above ``n`` to test edge cases.
    """
    n = random.randint(0, max_n)
    possible_edges = [(u, v) for u in range(n) for v in range(u + 1, n)]
    edges: List[List[int]] = []
    for u, v in possible_edges:
        if random.choice([True, False]):
            edges.append([u, v])
    # Choose k in a range that may be negative or larger than n.
    k = random.randint(-2, n + 2)
    return {"n": n, "edges": edges, "k": k}


def main() -> None:
    random.seed(0)
    total = 0
    passed = 0
    for _ in range(200):  # enough random tests for confidence
        src = random_instance()
        # Validate source (will raise if malformed – should not happen).
        Clique.validate(src)
        # Compute answers directly.
        ans_src = brute_clique(src)
        # Reduce and compute answer of target.
        tgt = reduce_instance(src)
        VertexCover.validate(tgt)
        ans_tgt = brute_vertex_cover(tgt)
        total += 1
        if ans_src == ans_tgt:
            passed += 1
        else:
            # Print a failing case for debugging.
            print("FAILURE", file=sys.stderr)
            print("source:", src, file=sys.stderr)
            print("target:", tgt, file=sys.stderr)
            print("source answer", ans_src, "target answer", ans_tgt, file=sys.stderr)
    # Write verdict.json
    verdict = {
        "verified": passed == total,
        "tests_run": total,
        "tests_passed": passed,
    }
    with open("verdict.json", "w", encoding="utf-8") as f:
        json.dump(verdict, f)
    print(json.dumps(verdict))

if __name__ == "__main__":
    main()

