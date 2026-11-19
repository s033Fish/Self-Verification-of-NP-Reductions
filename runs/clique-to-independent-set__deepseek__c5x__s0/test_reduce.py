"""Tests for the reduction from Clique to Independent Set.

The script implements brute‑force solvers for both problems and checks that
the answer on a randomly generated Clique instance matches the answer on the
instance produced by ``reduce``.  It reports the number of tests run and the
number of passed tests and writes a ``verdict.json`` file as required by the
task description.
"""

from __future__ import annotations

import json
import random
import sys
from itertools import combinations

import problems  # the module containing the problem definitions
from reduce import reduce as reduce_instance


def solve_clique(instance: dict) -> bool:
    """Brute‑force solver for the Clique problem.

    Returns ``True`` iff the graph has a clique of size at least ``k``.
    """
    n = instance["n"]
    k = instance["k"]
    # Edge set for quick lookup
    edge_set = {frozenset(e) for e in instance["edges"]}

    # Edge cases from the problem statement
    if k <= 0:
        return True
    if k == 1:
        return n >= 1
    if k > n:
        return False

    # Check all subsets of size >= k (we can stop at the first success)
    for size in range(k, n + 1):
        for subset in combinations(range(n), size):
            # Verify that every pair in the subset is an edge
            if all(frozenset((u, v)) in edge_set for u, v in combinations(subset, 2)):
                return True
    return False


def solve_independent_set(instance: dict) -> bool:
    """Brute‑force solver for the Independent Set problem.

    Returns ``True`` iff the graph has an independent set of size at least
    ``k``.
    """
    n = instance["n"]
    k = instance["k"]
    edge_set = {frozenset(e) for e in instance["edges"]}

    if k <= 0:
        return True
    if k > n:
        return False
    if not edge_set:
        # No edges – any set works
        return True

    for size in range(k, n + 1):
        for subset in combinations(range(n), size):
            # No pair should be an edge
            if all(frozenset((u, v)) not in edge_set for u, v in combinations(subset, 2)):
                return True
    return False


def generate_random_instance(max_n: int = 6) -> dict:
    """Generate a random Clique instance respecting the validation rules.

    ``max_n`` limits the number of vertices to keep the brute‑force search
    tractable.
    """
    n = random.randint(0, max_n)
    possible_edges = [(u, v) for u in range(n) for v in range(u + 1, n)]
    edges: list[list[int]] = []
    for u, v in possible_edges:
        if random.choice([True, False]):
            edges.append([u, v])
    # Choose k in a range that includes edge cases
    k = random.randint(-1, n + 2)
    instance = {"n": n, "edges": edges, "k": k}
    # Validate using the provided validator – will raise if malformed
    problems.Clique.validate(instance)
    return instance


def main() -> None:
    random.seed(0)  # deterministic for reproducibility
    tests_run = 0
    tests_passed = 0
    for _ in range(500):  # enough random tests for confidence
        instance = generate_random_instance()
        answer_clique = solve_clique(instance)
        reduced = reduce_instance(instance)
        # Validate the reduced instance as an Independent Set problem
        problems.IndependentSet.validate(reduced)
        answer_indep = solve_independent_set(reduced)
        tests_run += 1
        if answer_clique == answer_indep:
            tests_passed += 1
        else:
            # Print a minimal diagnostic for debugging
            print("Mismatch!", file=sys.stderr)
            print("Original:", instance, file=sys.stderr)
            print("Reduced:", reduced, file=sys.stderr)
            print("Clique answer:", answer_clique, "Independent answer:", answer_indep, file=sys.stderr)
    verdict = {
        "verified": tests_passed == tests_run,
        "tests_run": tests_run,
        "tests_passed": tests_passed,
    }
    with open("verdict.json", "w", encoding="utf-8") as f:
        json.dump(verdict, f)
    # Also print the verdict for immediate visibility
    print(json.dumps(verdict))

if __name__ == "__main__":
    main()

