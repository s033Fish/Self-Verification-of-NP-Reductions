"""Test the reduction from ThreeColoring to IndependentSet.

The script implements exhaustive (brute‑force) solvers for both source and
target problems based directly on the definitions in ``problems.py``.  It then
generates a collection of small random instances, applies ``reduce`` and checks
that the answers agree.

The script prints a JSON object with the fields required for the final
``verdict.json`` file:

    {"verified": <bool>, "tests_run": <int>, "tests_passed": <int>}

The script is intended to be executed directly (``python test_reduce.py``) and
will exit with status 0 regardless of the outcome – the calling process reads
the printed JSON.
"""

from __future__ import annotations

import json
import random
import sys
from itertools import combinations, product
from typing import List, Dict

from problems import ThreeColoring, IndependentSet, InvalidInstance
from reduce import reduce as reduce_instance


def solve_three_coloring(instance: Dict) -> bool:
    """Brute‑force solver for 3‑Coloring.

    Returns True iff the graph is 3‑colorable.
    """
    n = instance["n"]
    edges = instance["edges"]
    # Edge cases from the problem statement
    if n == 0:
        return True
    if n <= 3:
        return True
    # Check for K4 (complete graph on 4 vertices) – a quick sufficient
    # condition for a NO answer, but not necessary. The exhaustive search
    # below will handle all cases, so we only use it for early exit.
    if n >= 4:
        # If there exists a set of 4 vertices that are all pairwise adjacent,
        # the answer is definitely NO.
        verts = list(range(n))
        edge_set = {frozenset(e) for e in edges}
        for combo in combinations(verts, 4):
            if all(frozenset((a, b)) in edge_set for a, b in combinations(combo, 2)):
                return False
    # Exhaustive assignment of colours 0,1,2 to each vertex
    for coloring in product(range(3), repeat=n):
        ok = True
        for u, v in edges:
            if coloring[u] == coloring[v]:
                ok = False
                break
        if ok:
            return True
    return False


def solve_independent_set(instance: Dict) -> bool:
    """Brute‑force solver for Independent Set.

    Returns True iff there exists an independent set of size at least ``k``.
    """
    n = instance["n"]
    edges = instance["edges"]
    k = instance["k"]
    # Edge cases
    if k <= 0:
        return True
    if k > n:
        return False
    if not edges:
        return True  # any set works
    edge_set = {frozenset(e) for e in edges}
    # Check all subsets of size >= k (search from k up to n for early exit)
    verts = list(range(n))
    for size in range(k, n + 1):
        for combo in combinations(verts, size):
            # Verify independence
            independent = True
            for a, b in combinations(combo, 2):
                if frozenset((a, b)) in edge_set:
                    independent = False
                    break
            if independent:
                return True
    return False


def random_graph(n: int, edge_prob: float = 0.5) -> List[List[int]]:
    """Generate a random simple undirected graph with ``n`` vertices.

    ``edge_prob`` is the probability that any given unordered pair becomes an
    edge.  The graph is returned as a list of ``[u, v]`` edge lists.
    """
    edges = []
    for u, v in combinations(range(n), 2):
        if random.random() < edge_prob:
            edges.append([u, v])
    return edges


def main() -> None:
    random.seed(0)  # deterministic for reproducibility
    tests_run = 0
    tests_passed = 0
    verified = True

    # Exhaustively test all graphs up to n=4 (there are 2^{n choose 2} graphs).
    for n in range(0, 5):
        all_pairs = list(combinations(range(n), 2))
        for mask in range(1 << len(all_pairs)):
            edges = []
            for i, (u, v) in enumerate(all_pairs):
                if mask & (1 << i):
                    edges.append([u, v])
            src_instance = {"n": n, "edges": edges}
            try:
                ThreeColoring.validate(src_instance)
            except InvalidInstance:
                # Should never happen because we generate valid instances
                continue
            src_ans = solve_three_coloring(src_instance)
            tgt_instance = reduce_instance(src_instance)
            tgt_ans = solve_independent_set(tgt_instance)
            tests_run += 1
            if src_ans == tgt_ans:
                tests_passed += 1
            else:
                verified = False

    # Additionally run a number of random larger instances (n up to 7) to catch
    # any subtle bugs.
    for _ in range(200):
        n = random.randint(0, 7)
        edges = random_graph(n, edge_prob=0.4)
        src_instance = {"n": n, "edges": edges}
        try:
            ThreeColoring.validate(src_instance)
        except InvalidInstance:
            continue
        src_ans = solve_three_coloring(src_instance)
        tgt_instance = reduce_instance(src_instance)
        tgt_ans = solve_independent_set(tgt_instance)
        tests_run += 1
        if src_ans == tgt_ans:
            tests_passed += 1
        else:
            verified = False

    result = {"verified": verified, "tests_run": tests_run, "tests_passed": tests_passed}
    print(json.dumps(result))

if __name__ == "__main__":
    main()
