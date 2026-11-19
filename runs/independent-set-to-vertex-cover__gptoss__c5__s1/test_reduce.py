"""Test suite for the reduction from IndependentSet to VertexCover.

The repository provides a ``reduce`` function that should transform an
instance of the source problem (Independent Set) into an equivalent instance
of the target problem (Vertex Cover).  This file implements brute‑force
solvers for both problems, exhaustively enumerates a large number of small
random instances, checks that the answers agree, and finally writes a
``verdict.json`` file summarising the result.

The verification criteria are:

* ``reduce`` must run in polynomial time (the implementation is O(|E|) and
  therefore trivially satisfies this – we simply call it).
* The answer to the reduced instance must be *yes* exactly when the answer
  to the original instance is *yes*.

The script reports the total number of tests performed and how many passed.
If every test passes, ``verified`` is set to ``true``; otherwise ``false``.
"""

from __future__ import annotations

import json
import random
import itertools
from pathlib import Path
from typing import List, Dict, Any

from reduce import reduce as reduce_instance
from problems import IndependentSet, VertexCover


def independent_set_bruteforce(instance: Dict[str, Any]) -> bool:
    """Return True iff the graph has an independent set of size >= k.

    The implementation enumerates all subsets of vertices and checks the
    independence condition directly.  This is exponential but the test
    harness only uses very small graphs (n <= 6), so it is fine.
    """
    n = instance["n"]
    edges = instance["edges"]
    k = instance["k"]

    # Edge cases from the problem statement
    if k <= 0:
        return True
    if k > n:
        return False
    if not edges:
        return True  # any set of size k works

    # Pre‑compute adjacency set for quick lookup
    adj = [set() for _ in range(n)]
    for u, v in edges:
        adj[u].add(v)
        adj[v].add(u)

    # Check all subsets of size >= k (early exit on first success)
    for size in range(k, n + 1):
        for subset in itertools.combinations(range(n), size):
            # Verify independence
            independent = True
            for u in subset:
                if any(v in subset for v in adj[u]):
                    independent = False
                    break
            if independent:
                return True
    return False


def vertex_cover_bruteforce(instance: Dict[str, Any]) -> bool:
    """Return True iff the graph has a vertex cover of size <= k.

    Enumerates all subsets of vertices up to size k and checks whether every
    edge is incident to at least one vertex in the subset.
    """
    n = instance["n"]
    edges = instance["edges"]
    k = instance["k"]

    # Edge cases from the problem statement
    if k < 0:
        return False
    if not edges:
        return True  # empty set covers nothing, works for any k>=0
    if k >= n:
        return True

    # Enumerate subsets up to size k
    for size in range(0, k + 1):
        for subset in itertools.combinations(range(n), size):
            covered = True
            subset_set = set(subset)
            for u, v in edges:
                if u not in subset_set and v not in subset_set:
                    covered = False
                    break
            if covered:
                return True
    return False


def generate_random_instance(max_n: int = 6) -> Dict[str, Any]:
    """Generate a random graph instance with n in [0, max_n] and random k.

    The function ensures the instance passes validation by the problem
    classes.
    """
    n = random.randint(0, max_n)
    possible_edges = [(u, v) for u in range(n) for v in range(u + 1, n)]
    edges: List[List[int]] = []
    for u, v in possible_edges:
        if random.random() < 0.5:
            edges.append([u, v])
    # Choose k in a range that includes edge cases
    k = random.randint(-2, n + 2)
    return {"n": n, "edges": edges, "k": k}


def main() -> None:
    random.seed(0)  # deterministic for reproducibility
    total_tests = 0
    passed = 0

    # Exhaustively test all graphs up to n=5 (there are 2^{n choose 2} edge sets)
    for n in range(0, 6):
        vertices = list(range(n))
        all_possible_edges = [(u, v) for u in vertices for v in vertices if u < v]
        for edge_mask in range(1 << len(all_possible_edges)):
            edges: List[List[int]] = []
            for i, (u, v) in enumerate(all_possible_edges):
                if (edge_mask >> i) & 1:
                    edges.append([u, v])
            # Test a variety of k values including edge cases
            for k in range(-2, n + 3):
                instance = {"n": n, "edges": edges, "k": k}
                # Validate instance using the provided validator (may raise)
                try:
                    IndependentSet.validate(instance)
                except Exception:
                    # If validation fails, skip – such instances are not
                    # considered by the reduction.
                    continue
                total_tests += 1
                src_answer = independent_set_bruteforce(instance)
                reduced = reduce_instance(instance)
                # Ensure reduced instance validates as a VertexCover
                VertexCover.validate(reduced)
                tgt_answer = vertex_cover_bruteforce(reduced)
                if src_answer == tgt_answer:
                    passed += 1
                else:
                    # Print a minimal diagnostic for debugging
                    print("Mismatch!", instance, reduced, src_answer, tgt_answer)

    # Additionally run a number of random larger instances (n up to 8) to catch
    # any hidden issues.
    for _ in range(200):
        inst = generate_random_instance(max_n=8)
        try:
            IndependentSet.validate(inst)
        except Exception:
            continue
        total_tests += 1
        src = independent_set_bruteforce(inst)
        red = reduce_instance(inst)
        VertexCover.validate(red)
        tgt = vertex_cover_bruteforce(red)
        if src == tgt:
            passed += 1
        else:
            print("Random mismatch!", inst, red, src, tgt)

    verdict = {
        "verified": passed == total_tests,
        "tests_run": total_tests,
        "tests_passed": passed,
    }
    Path("verdict.json").write_text(json.dumps(verdict, indent=2))
    print(json.dumps(verdict, indent=2))

if __name__ == "__main__":
    main()
