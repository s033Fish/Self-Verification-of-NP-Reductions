"""Test the reduction from Independent Set to Vertex Cover.

The reduction is defined in ``reduce.py`` and should satisfy the following
property for every instance ``I`` of ``IndependentSet``:

    IndependentSet(I) is a YES instance  <=>  VertexCover(reduce(I)) is a YES instance

Because the repository does not provide solvers, we implement small brute‑
force solvers for both problems.  The tests enumerate all subsets of the
vertex set for graphs with up to six vertices – this is exhaustive but still
fast.  For each generated instance we compare the answer of the solvers with
the answer obtained after applying the reduction.

If every test succeeds we write a ``verdict.json`` file indicating that the
reduction has been verified.
"""

from __future__ import annotations

import json
import random
import itertools
from pathlib import Path
from typing import List, Dict, Any

from problems import IndependentSet, VertexCover, InvalidInstance
from reduce import reduce as reduce_instance


def independent_set_bruteforce(instance: Dict[str, Any]) -> bool:
    """Return True iff the instance has an independent set of size at least k.

    The function assumes the instance is valid (i.e., ``IndependentSet.validate``
    would not raise).  It enumerates all subsets of vertices and checks the
    independence condition.
    """
    n = instance["n"]
    edges = {frozenset(e) for e in instance["edges"]}
    k = instance["k"]
    if k <= 0:
        return True
    if k > n:
        return False
    # enumerate subsets of size >= k (early exit when found)
    vertices = list(range(n))
    for size in range(k, n + 1):
        for subset in itertools.combinations(vertices, size):
            # check if any edge is inside the subset
            bad = any(frozenset((u, v)) in edges for u, v in itertools.combinations(subset, 2))
            if not bad:
                return True
    return False


def vertex_cover_bruteforce(instance: Dict[str, Any]) -> bool:
    """Return True iff the instance has a vertex cover of size at most k.

    Similar to ``independent_set_bruteforce`` but checks the cover condition.
    """
    n = instance["n"]
    edges = [tuple(e) for e in instance["edges"]]
    k = instance["k"]
    if k < 0:
        return False
    if k >= n:
        return True
    vertices = list(range(n))
    for size in range(0, k + 1):
        for subset in itertools.combinations(vertices, size):
            cover_set = set(subset)
            if all(u in cover_set or v in cover_set for u, v in edges):
                return True
    return False


def generate_random_instance(max_n: int = 6, edge_prob: float = 0.4) -> Dict[str, Any]:
    """Generate a random IndependentSet instance.

    The number of vertices ``n`` is chosen uniformly from 0..max_n.  Each
    unordered pair of distinct vertices becomes an edge with probability
    ``edge_prob``.  ``k`` is chosen uniformly from ``[-max_n, max_n * 2]`` to
    exercise edge cases (negative, zero, larger than n, etc.).
    """
    n = random.randint(0, max_n)
    edges: List[List[int]] = []
    for u in range(n):
        for v in range(u + 1, n):
            if random.random() < edge_prob:
                edges.append([u, v])
    k = random.randint(-max_n, max_n * 2)
    instance = {"n": n, "edges": edges, "k": k}
    # Ensure the instance is valid according to the problem definition.
    IndependentSet.validate(instance)
    return instance


def main() -> None:
    random.seed(0)  # deterministic for reproducibility
    tests_run = 0
    tests_passed = 0
    # Exhaustively test all small graphs up to n=5 (including all edge subsets)
    for n in range(0, 6):
        vertices = list(range(n))
        all_possible_edges = [(u, v) for u in vertices for v in vertices if u < v]
        # iterate over a subset of edge subsets to keep runtime reasonable
        for edge_mask in range(0, 1 << len(all_possible_edges)):
            edges = [list(all_possible_edges[i]) for i in range(len(all_possible_edges)) if (edge_mask >> i) & 1]
            # test a range of k values covering edge cases
            for k in range(-1, n + 3):
                instance = {"n": n, "edges": edges, "k": k}
                # validate
                IndependentSet.validate(instance)
                # compute answers
                indep_yes = independent_set_bruteforce(instance)
                reduced = reduce_instance(instance)
                # reduced instance should be valid for VertexCover
                VertexCover.validate(reduced)
                vc_yes = vertex_cover_bruteforce(reduced)
                tests_run += 1
                if indep_yes == vc_yes:
                    tests_passed += 1
                else:
                    # print diagnostic for failure
                    print("FAIL", instance, reduced, indep_yes, vc_yes)
    # also run a number of random instances for robustness
    for _ in range(200):
        instance = generate_random_instance()
        indep_yes = independent_set_bruteforce(instance)
        reduced = reduce_instance(instance)
        VertexCover.validate(reduced)
        vc_yes = vertex_cover_bruteforce(reduced)
        tests_run += 1
        if indep_yes == vc_yes:
            tests_passed += 1
        else:
            print("FAIL random", instance, reduced, indep_yes, vc_yes)

    verdict = {
        "verified": tests_run == tests_passed,
        "tests_run": tests_run,
        "tests_passed": tests_passed,
    }
    Path("verdict.json").write_text(json.dumps(verdict, indent=2))
    print(json.dumps(verdict, indent=2))


if __name__ == "__main__":
    main()

