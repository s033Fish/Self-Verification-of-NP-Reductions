"""Test suite for the reduction from 3-Coloring to 1-in-3-SAT.

The task requires us to:
1. Implement brute‑force solvers for the source (ThreeColoring) and the
   target (OneInThreeSat) problems.
2. Generate a number of small random instances of the source problem,
   run the provided ``reduce`` function on each, and verify that the
   answer to the reduced instance matches the answer to the original
   instance.
3. Produce a ``verdict.json`` file with the fields ``verified``,
   ``tests_run`` and ``tests_passed`` as described in the task.

The tests are deliberately exhaustive for very small sizes (n ≤ 5) and
include a few hand‑crafted edge cases such as the empty graph, a K4, and
graphs with at most three vertices which are always 3‑colorable.

The script is intended to be executed directly (``python test_reduce.py``)
and will exit with a non‑zero status if any test fails, ensuring that the
automated checker can detect failures.
"""

from __future__ import annotations

import json
import random
import sys
from itertools import product, combinations
from typing import List, Tuple

import problems  # The module containing problem definitions and validation
from reduce import reduce as reduction


def three_coloring_bruteforce(instance: dict) -> bool:
    """Return True iff the given graph is 3‑colorable.

    The instance is assumed to be validated already.  For n up to 5 the
    exhaustive search (3**n assignments) is trivial.
    """
    n: int = instance["n"]
    edges: List[Tuple[int, int]] = [tuple(e) for e in instance["edges"]]

    for coloring in product(range(3), repeat=n):
        ok = True
        for u, v in edges:
            if coloring[u] == coloring[v]:
                ok = False
                break
        if ok:
            return True
    return False


def one_in_three_sat_bruteforce(instance: dict) -> bool:
    """Return True iff the 1‑in‑3‑SAT instance is satisfiable.

    The algorithm performs depth‑first search with pruning based on the
    constraint that each clause must contain exactly one true literal.
    """
    m: int = instance["num_vars"]
    clauses: List[Tuple[int, int, int]] = [tuple(c) for c in instance["clauses"]]

    # Map each variable to the indices of clauses it appears in.
    var_to_clauses: List[List[int]] = [[] for _ in range(m + 1)]
    for ci, (a, b, c) in enumerate(clauses):
        var_to_clauses[a].append(ci)
        var_to_clauses[b].append(ci)
        var_to_clauses[c].append(ci)

    true_counts = [0] * len(clauses)
    unassigned_counts = [3] * len(clauses)
    assignment: List[bool | None] = [None] * (m + 1)

    def backtrack(var: int) -> bool:
        if var > m:
            return all(tc == 1 for tc in true_counts)
        for val in (False, True):
            assignment[var] = val
            affected = var_to_clauses[var]
            rollback = []
            consistent = True
            for ci in affected:
                tb, ub = true_counts[ci], unassigned_counts[ci]
                rollback.append((ci, tb, ub))
                if val:
                    true_counts[ci] += 1
                unassigned_counts[ci] -= 1
                if true_counts[ci] > 1:
                    consistent = False
                    break
                if unassigned_counts[ci] == 0 and true_counts[ci] != 1:
                    consistent = False
                    break
            if consistent and backtrack(var + 1):
                return True
            # revert changes
            for ci, tb, ub in rollback:
                true_counts[ci] = tb
                unassigned_counts[ci] = ub
            assignment[var] = None
        return False

    return backtrack(1)


def generate_random_graph(max_vertices: int) -> dict:
    """Generate a random valid graph with up to ``max_vertices`` vertices.

    The number of vertices is chosen uniformly from 0..max_vertices.  All
    possible edges are considered and each is included with probability
    0.5.
    """
    n = random.randint(0, max_vertices)
    edges = []
    for u, v in combinations(range(n), 2):
        if random.choice([True, False]):
            edges.append([u, v])
    return {"n": n, "edges": edges}


def run_tests() -> Tuple[int, int]:
    """Execute a suite of tests and return (tests_run, tests_passed)."""
    tests_run = 0
    passed = 0

    # Hand‑crafted edge cases
    edge_cases = [
        {"n": 0, "edges": []},  # empty graph, should be yes
        {"n": 1, "edges": []},
        {"n": 2, "edges": []},
        {"n": 3, "edges": []},
        # K4 (non‑3‑colorable). Build explicit edges for vertices 0..3
        {
            "n": 4,
            "edges": [[u, v] for u, v in combinations(range(4), 2)],
        },
    ]

    for instance in edge_cases:
        tests_run += 1
        try:
            problems.ThreeColoring.validate(instance)
        except Exception as e:
            print(f"Validation failed for edge case {instance}: {e}", file=sys.stderr)
            continue
        src_ans = three_coloring_bruteforce(instance)
        reduced = reduction(instance)
        problems.OneInThreeSat.validate(reduced)
        tgt_ans = one_in_three_sat_bruteforce(reduced)
        if src_ans == tgt_ans:
            passed += 1
        else:
            print(
                f"Mismatch on edge case {instance}: src={src_ans}, tgt={tgt_ans}",
                file=sys.stderr,
            )

    # Random tests for small graphs (up to 5 vertices).
    random.seed(0)
    for _ in range(200):
        instance = generate_random_graph(5)
        tests_run += 1
        try:
            problems.ThreeColoring.validate(instance)
        except Exception as e:
            print(f"Generated invalid instance {instance}: {e}", file=sys.stderr)
            continue
        src_ans = three_coloring_bruteforce(instance)
        reduced = reduction(instance)
        problems.OneInThreeSat.validate(reduced)
        tgt_ans = one_in_three_sat_bruteforce(reduced)
        if src_ans == tgt_ans:
            passed += 1
        else:
            print(
                f"Mismatch on random instance {instance}: src={src_ans}, tgt={tgt_ans}",
                file=sys.stderr,
            )

    return tests_run, passed


def main() -> None:
    tests_run, passed = run_tests()
    verified = tests_run == passed
    verdict = {"verified": verified, "tests_run": tests_run, "tests_passed": passed}
    with open("verdict.json", "w", encoding="utf-8") as f:
        json.dump(verdict, f, indent=2)
    print(json.dumps(verdict, indent=2))
    sys.exit(0 if verified else 1)


if __name__ == "__main__":
    main()
