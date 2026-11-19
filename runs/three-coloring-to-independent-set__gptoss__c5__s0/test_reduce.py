"""Automated tests for the reduction from ThreeColoring to IndependentSet.

The repository provides only validation functions for the two problems and
the reduction implementation.  This test module implements exhaustive brute
force solvers for both problems (suitable for tiny graphs) and then checks
that for a large set of random small instances the answer of the source
instance matches the answer of the reduced target instance.

The script is deliberately simple – it does not depend on any external
testing framework – and prints a short summary that the surrounding harness
can parse.  It also writes ``verdict.json`` with the required fields.
"""

from __future__ import annotations

import json
import random
import itertools
import sys
from typing import List, Dict, Any

from problems import ThreeColoring, IndependentSet
from reduce import reduce as reduce_instance


def three_coloring_bruteforce(instance: Dict[str, Any]) -> bool:
    """Return True iff the given graph is 3‑colorable.

    The graph is tiny (n ≤ 6 in our tests) so we simply try all 3^n colour
    assignments.
    """
    ThreeColoring.validate(instance)
    n = instance["n"]
    edges = instance["edges"]
    # Edge case shortcuts matching the problem statement
    if n == 0:
        return True
    if n <= 3:
        return True
    # Check for K4 (complete graph on 4 vertices) – if present, answer is False
    # This is a quick early exit but not required for correctness.
    if n >= 4:
        # build adjacency set
        adj = {i: set() for i in range(n)}
        for u, v in edges:
            adj[u].add(v)
            adj[v].add(u)
        # check any 4‑subset forms a clique
        for combo in itertools.combinations(range(n), 4):
            if all(v in adj[u] for u, v in itertools.combinations(combo, 2)):
                return False
    # exhaustive search
    for coloring in itertools.product(range(3), repeat=n):
        ok = True
        for u, v in edges:
            if coloring[u] == coloring[v]:
                ok = False
                break
        if ok:
            return True
    return False


def independent_set_bruteforce(instance: Dict[str, Any]) -> bool:
    """Return True iff the graph contains an independent set of size ≥ k.
    """
    IndependentSet.validate(instance)
    n = instance["n"]
    edges = instance["edges"]
    k = instance["k"]
    if k <= 0:
        return True
    if k > n:
        return False
    # Build adjacency matrix for quick checks
    adj = [[False] * n for _ in range(n)]
    for u, v in edges:
        adj[u][v] = adj[v][u] = True
    # iterate over subsets of size k up to n (we only need to find one ≥k)
    for size in range(k, n + 1):
        for subset in itertools.combinations(range(n), size):
            independent = True
            for u, v in itertools.combinations(subset, 2):
                if adj[u][v]:
                    independent = False
                    break
            if independent:
                return True
    return False


def generate_random_instance(max_n: int = 5, edge_prob: float = 0.4) -> Dict[str, Any]:
    n = random.randint(0, max_n)
    edges: List[List[int]] = []
    for u in range(n):
        for v in range(u + 1, n):
            if random.random() < edge_prob:
                edges.append([u, v])
    return {"n": n, "edges": edges}


def main() -> None:
    random.seed(0)
    total_tests = 0
    passed = 0
    # Perform a mix of exhaustive small graphs and random larger ones.
    # Exhaustive for n up to 5 (all possible edge subsets).
    for n in range(0, 5):
        vertices = list(range(n))
        all_possible_edges = list(itertools.combinations(vertices, 2))
        for mask in range(1 << len(all_possible_edges)):
            edges = []
            for i, (u, v) in enumerate(all_possible_edges):
                if mask & (1 << i):
                    edges.append([u, v])
            instance = {"n": n, "edges": edges}
            total_tests += 1
            src_ans = three_coloring_bruteforce(instance)
            try:
                tgt_instance = reduce_instance(instance)
            except Exception as e:
                print(f"Reduction raised an exception on instance {instance}: {e}")
                continue
            tgt_ans = independent_set_bruteforce(tgt_instance)
            if src_ans == tgt_ans:
                passed += 1
            else:
                print("Mismatch!", instance, src_ans, tgt_ans)
    # Additional random tests up to n=7
    for _ in range(200):
        instance = generate_random_instance(max_n=7, edge_prob=0.3)
        total_tests += 1
        src_ans = three_coloring_bruteforce(instance)
        tgt_instance = reduce_instance(instance)
        tgt_ans = independent_set_bruteforce(tgt_instance)
        if src_ans == tgt_ans:
            passed += 1
        else:
            print("Mismatch!", instance, src_ans, tgt_ans)

    verdict = {
        "verified": passed == total_tests,
        "tests_run": total_tests,
        "tests_passed": passed,
    }
    print(json.dumps(verdict))
    # Also write to file as required by the task description.
    with open("verdict.json", "w", encoding="utf-8") as f:
        json.dump(verdict, f)

if __name__ == "__main__":
    main()
