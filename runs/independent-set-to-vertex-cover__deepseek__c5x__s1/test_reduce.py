"""Automated tests for the reduction from IndependentSet to VertexCover.

The repository provides only validation functions for the two problems.
To check the correctness of ``reduce.py`` we implement straightforward
brute‑force solvers for both source and target problems and then generate
many small random instances. For each instance we compare the answer of
the source solver with the answer of the target solver applied to the
reduced instance.

If all generated instances agree we consider the reduction verified.
The script prints a JSON object ``verdict.json`` containing the number of
tests run, the number passed and a boolean ``verified`` flag.
"""

from __future__ import annotations

import json
import random
import sys
from itertools import combinations

import problems  # the module containing the problem classes
from reduce import reduce as reduce_instance


def independent_set_bruteforce(instance: dict) -> bool:
    """Return True iff the graph has an independent set of size >= k.

    The implementation follows the definition in ``IndependentSet``.
    """
    n = instance["n"]
    edges = [(u, v) for u, v in instance["edges"]]
    k = instance["k"]

    # Edge cases from the problem statement
    if k <= 0:
        return True
    if k > n:
        return False

    vertices = list(range(n))
    # Iterate subsets in decreasing size to early‑exit when we find a large enough independent set.
    for size in range(n, k - 1, -1):
        for subset in combinations(vertices, size):
            subset_set = set(subset)
            independent = True
            for u, v in edges:
                if u in subset_set and v in subset_set:
                    independent = False
                    break
            if independent:
                return True
    return False


def vertex_cover_bruteforce(instance: dict) -> bool:
    """Return True iff the graph has a vertex cover of size <= k.

    Mirrors the definition in ``VertexCover``.
    """
    n = instance["n"]
    edges = [(u, v) for u, v in instance["edges"]]
    k = instance["k"]

    # Edge cases from the problem statement
    if k < 0:
        return False
    if not edges:
        return True
    if k >= n:
        return True

    vertices = list(range(n))
    for size in range(0, min(k, n) + 1):
        for subset in combinations(vertices, size):
            subset_set = set(subset)
            covers_all = True
            for u, v in edges:
                if u not in subset_set and v not in subset_set:
                    covers_all = False
                    break
            if covers_all:
                return True
    return False


def generate_random_instance(max_n: int = 6) -> dict:
    """Generate a random graph instance with fields n, edges, k.

    The generator respects the validation rules (no duplicate edges,
    no self‑loops). ``k`` may be negative, zero, or larger than ``n`` to
    exercise edge cases.
    """
    n = random.randint(0, max_n)
    possible_edges = [(u, v) for u in range(n) for v in range(u + 1, n)]
    edges = []
    for (u, v) in possible_edges:
        if random.random() < 0.3:
            edges.append([u, v])
    k = random.randint(-2, n + 2)
    return {"n": n, "edges": edges, "k": k}


def main() -> None:
    random.seed(0)
    tests_run = 0
    tests_passed = 0
    for _ in range(500):
        src_instance = generate_random_instance()
        try:
            problems.IndependentSet.validate(src_instance)
        except Exception as exc:
            print(f"Generated invalid source instance: {exc}", file=sys.stderr)
            continue
        src_answer = independent_set_bruteforce(src_instance)
        tgt_instance = reduce_instance(src_instance)
        try:
            problems.VertexCover.validate(tgt_instance)
        except Exception as exc:
            print(f"Reduction produced invalid target instance: {exc}", file=sys.stderr)
            continue
        tgt_answer = vertex_cover_bruteforce(tgt_instance)
        tests_run += 1
        if src_answer == tgt_answer:
            tests_passed += 1
        else:
            print("Mismatch found:")
            print("Source instance:", src_instance)
            print("Reduced instance:", tgt_instance)
            print("Source answer:", src_answer, "Target answer:", tgt_answer)
    verdict = {
        "verified": tests_run == tests_passed,
        "tests_run": tests_run,
        "tests_passed": tests_passed,
    }
    with open("verdict.json", "w", encoding="utf-8") as f:
        json.dump(verdict, f, indent=2)
    print(json.dumps(verdict, indent=2))

if __name__ == "__main__":
    main()
