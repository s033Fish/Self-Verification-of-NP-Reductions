"""Automated tests for the reduction from Independent Set to Clique.

The file defines brute‑force solvers for both problems and then generates a
large number of small random instances.  For each instance we:

1. Validate the source instance using ``IndependentSet.validate``.
2. Run the provided ``reduce`` function to obtain a target instance.
3. Validate the target instance using ``Clique.validate``.
4. Compare the answers of the two solvers.  The answers must match for the
   reduction to be correct.

The script prints a JSON object with the fields required by the task:

```
{"verified": <bool>, "tests_run": <int>, "tests_passed": <int>}
```

The test suite is deliberately exhaustive for n ≤ 6 (all possible graphs) and
also includes a few random larger instances (up to n = 10) to increase coverage.
"""

from __future__ import annotations

import itertools
import json
import random
import sys
from typing import List, Dict, Any

import problems  # provides IndependentSet and Clique classes
from reduce import reduce as reduction


def independent_set_solver(instance: Dict[str, Any]) -> bool:
    """Brute‑force solver for Independent Set.

    Returns True iff the graph has an independent set of size at least ``k``.
    """
    n = instance["n"]
    edges = instance["edges"]
    k = instance["k"]
    if k <= 0:
        return True
    if k > n:
        return False
    # Build adjacency set for quick checks
    adj = {i: set() for i in range(n)}
    for u, v in edges:
        adj[u].add(v)
        adj[v].add(u)
    # Iterate over subsets of vertices
    for size in range(k, n + 1):
        for subset in itertools.combinations(range(n), size):
            ok = True
            for u in subset:
                # If any neighbor also in subset, not independent
                if any(v in subset for v in adj[u]):
                    ok = False
                    break
            if ok:
                return True
    return False


def clique_solver(instance: Dict[str, Any]) -> bool:
    """Brute‑force solver for Clique.

    Returns True iff the graph has a clique of size at least ``k``.
    """
    n = instance["n"]
    edges = instance["edges"]
    k = instance["k"]
    if k <= 0:
        return True
    if k == 1:
        return n >= 1
    if k > n:
        return False
    # Build adjacency set (including self for convenience)
    adj = {i: set() for i in range(n)}
    for u, v in edges:
        adj[u].add(v)
        adj[v].add(u)
    for size in range(k, n + 1):
        for subset in itertools.combinations(range(n), size):
            # Check every pair is connected
            if all(v in adj[u] for u, v in itertools.combinations(subset, 2)):
                return True
    return False


def generate_all_graphs(n: int) -> List[List[List[int]]]:
    """Generate all undirected simple graphs on ``n`` vertices.

    Each graph is represented as a list of edges ``[u, v]`` with ``u < v``.
    """
    vertices = list(range(n))
    possible_edges = [(i, j) for i in vertices for j in vertices if i < j]
    graphs: List[List[List[int]]] = []
    for mask in range(1 << len(possible_edges)):
        edges: List[List[int]] = []
        for bit, (u, v) in enumerate(possible_edges):
            if mask & (1 << bit):
                edges.append([u, v])
        graphs.append(edges)
    return graphs


def run_tests() -> Dict[str, Any]:
    tests_run = 0
    tests_passed = 0
    # Exhaustive tests for n up to 6
    for n in range(0, 7):
        all_edges = generate_all_graphs(n)
        # Test a range of k values, including edge cases
        ks = list(range(-1, n + 3))  # includes negative, zero, >n
        for edges in all_edges:
            for k in ks:
                instance = {"n": n, "edges": edges, "k": k}
                # Validate source instance
                try:
                    problems.IndependentSet.validate(instance)
                except Exception as e:
                    # Validation should never fail for generated instances
                    print("Invalid source instance", instance, e, file=sys.stderr)
                    continue
                reduced = reduction(instance)
                # Validate target instance
                try:
                    problems.Clique.validate(reduced)
                except Exception as e:
                    print("Invalid reduced instance", reduced, e, file=sys.stderr)
                    continue
                src_ans = independent_set_solver(instance)
                tgt_ans = clique_solver(reduced)
                tests_run += 1
                if src_ans == tgt_ans:
                    tests_passed += 1
                else:
                    print("Mismatch!", instance, reduced, src_ans, tgt_ans, file=sys.stderr)
    # Additional random tests for n up to 10
    random.seed(0)
    for _ in range(200):
        n = random.randint(0, 10)
        possible = [(i, j) for i in range(n) for j in range(i + 1, n)]
        edges = []
        for u, v in possible:
            if random.random() < 0.3:
                edges.append([u, v])
        k = random.randint(-2, n + 2)
        instance = {"n": n, "edges": edges, "k": k}
        try:
            problems.IndependentSet.validate(instance)
        except Exception:
            continue
        reduced = reduction(instance)
        try:
            problems.Clique.validate(reduced)
        except Exception:
            continue
        src_ans = independent_set_solver(instance)
        tgt_ans = clique_solver(reduced)
        tests_run += 1
        if src_ans == tgt_ans:
            tests_passed += 1
        else:
            print("Random mismatch!", instance, reduced, src_ans, tgt_ans, file=sys.stderr)
    verified = tests_run == tests_passed
    return {"verified": verified, "tests_run": tests_run, "tests_passed": tests_passed}


if __name__ == "__main__":
    result = run_tests()
    print(json.dumps(result))
