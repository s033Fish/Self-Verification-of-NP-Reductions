"""Test harness for the Clique → Independent Set reduction.

The task requires us to verify that ``reduce.py`` correctly transforms an
instance of the source problem (Clique) into an equivalent instance of the
target problem (IndependentSet).  Since the repository only provides validation
functions, we implement brute‑force solvers for both problems and compare the
answers on a collection of small random instances as well as on the complete
enumeration of all graphs for n ≤ 5.

The script produces a JSON file ``verdict.json`` with the fields required by
the evaluation harness:

    {
        "verified": <bool>,
        "tests_run": <int>,
        "tests_passed": <int>
    }

If *all* generated tests pass, ``verified`` is true.
"""

from __future__ import annotations

import json
import itertools
import random
import sys
from pathlib import Path

# Import the problem definitions and the reduction implementation.
import problems  # noqa: F401 – ensures validation helpers are loaded.
from problems import Clique, IndependentSet
from reduce import reduce as reduce_instance


def solve_clique(instance: dict) -> bool:
    """Brute‑force solver for Clique.

    Returns True iff the graph has a clique of size at least ``k``.
    """
    n = instance["n"]
    edges = {frozenset(e) for e in instance["edges"]}
    k = instance["k"]

    # Edge cases from the problem statement.
    if k <= 0:
        return True
    if k > n:
        return False
    if k == 1:
        return n >= 1

    # Check all subsets of size >= k.
    vertices = list(range(n))
    for size in range(k, n + 1):
        for subset in itertools.combinations(vertices, size):
            # Every pair must be an edge.
            if all(frozenset((u, v)) in edges for u, v in itertools.combinations(subset, 2)):
                return True
    return False


def solve_independent_set(instance: dict) -> bool:
    """Brute‑force solver for Independent Set.

    Returns True iff the graph has an independent set of size at least ``k``.
    """
    n = instance["n"]
    edges = {frozenset(e) for e in instance["edges"]}
    k = instance["k"]

    if k <= 0:
        return True
    if k > n:
        return False
    if not edges:
        # No edges → any set works.
        return True

    vertices = list(range(n))
    for size in range(k, n + 1):
        for subset in itertools.combinations(vertices, size):
            if all(frozenset((u, v)) not in edges for u, v in itertools.combinations(subset, 2)):
                return True
    return False


def generate_random_instance(n: int, edge_prob: float, k: int) -> dict:
    """Generate a random graph instance with ``n`` vertices.

    ``edge_prob`` is the probability that a given unordered pair is an edge.
    ``k`` is the threshold for the decision problem.
    """
    edges = []
    for u in range(n):
        for v in range(u + 1, n):
            if random.random() < edge_prob:
                edges.append([u, v])
    return {"n": n, "edges": edges, "k": k}


def enumerate_all_graphs(n: int) -> list[dict]:
    """Enumerate every simple undirected graph on ``n`` vertices.

    Returns a list of instances with ``k`` ranging from -1 to n+1 to also hit
    edge‑case values.
    """
    instances: list[dict] = []
    pairs = [(u, v) for u in range(n) for v in range(u + 1, n)]
    for mask in range(1 << len(pairs)):
        edges: list[list[int]] = []
        for i, (u, v) in enumerate(pairs):
            if mask & (1 << i):
                edges.append([u, v])
        # Test a variety of k values, including edge cases.
        for k in range(-1, n + 2):
            instances.append({"n": n, "edges": edges, "k": k})
    return instances


def main() -> None:
    random.seed(0)
    total_tests = 0
    passed = 0

    # 1. Exhaustive enumeration for n up to 5 (computationally feasible).
    for n in range(0, 5 + 1):
        for instance in enumerate_all_graphs(n):
            total_tests += 1
            # Validate instances using the provided classes.
            try:
                Clique.validate(instance)
                IndependentSet.validate(instance)  # validation of target format as well
            except Exception as exc:  # pragma: no cover – should not happen
                print(f"Invalid instance generated: {exc}", file=sys.stderr)
                continue

            reduced = reduce_instance(instance)
            # Ensure reduction output validates as IndependentSet instance.
            try:
                IndependentSet.validate(reduced)
            except Exception as exc:  # pragma: no cover
                print(f"Reduced instance invalid: {exc}", file=sys.stderr)
                continue

            ans_src = solve_clique(instance)
            ans_tgt = solve_independent_set(reduced)
            if ans_src == ans_tgt:
                passed += 1
            else:
                print("Mismatch!", instance, reduced, ans_src, ans_tgt, file=sys.stderr)

    # 2. Additional random tests for n up to 8.
    for _ in range(200):
        n = random.randint(0, 8)
        k = random.randint(-2, n + 2)
        instance = generate_random_instance(n, edge_prob=0.3, k=k)
        total_tests += 1
        try:
            Clique.validate(instance)
        except Exception as exc:  # pragma: no cover
            continue
        reduced = reduce_instance(instance)
        try:
            IndependentSet.validate(reduced)
        except Exception as exc:  # pragma: no cover
            continue
        if solve_clique(instance) == solve_independent_set(reduced):
            passed += 1

    verdict = {
        "verified": passed == total_tests,
        "tests_run": total_tests,
        "tests_passed": passed,
    }
    Path("verdict.json").write_text(json.dumps(verdict, indent=2))
    print(json.dumps(verdict, indent=2))


if __name__ == "__main__":
    main()

