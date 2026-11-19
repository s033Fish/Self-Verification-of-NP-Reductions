"""Test the reduction from ThreeColoring to IndependentSet.

The test generates a range of small graph instances, solves both the
source and target problems by exhaustive search, applies the provided
``reduce`` function and checks that the answers correspond.

If every generated instance satisfies the equivalence, the reduction is
considered verified.
"""

from __future__ import annotations

import itertools
import json
import sys
from typing import List, Tuple

# Import the problem definitions and the reduction implementation.
import problems  # noqa: F401  (ensures validation code is available)
from reduce import reduce as reduce_instance


def three_coloring_bruteforce(instance: dict) -> bool:
    """Return True iff the graph is 3‑colorable.

    Exhaustively tries all assignments of colours {0,1,2} to the vertices.
    """
    n: int = instance["n"]
    edges: List[Tuple[int, int]] = [tuple(e) for e in instance["edges"]]
    # Early trivial cases from the problem statement.
    if n == 0:
        return True
    if n <= 3:
        return True
    # Exhaustive search.
    for coloring in itertools.product(range(3), repeat=n):
        ok = True
        for u, v in edges:
            if coloring[u] == coloring[v]:
                ok = False
                break
        if ok:
            return True
    return False


def independent_set_bruteforce(instance: dict) -> bool:
    """Return True iff the graph has an independent set of size at least k.
    """
    n: int = instance["n"]
    edges_set = {frozenset(e) for e in instance["edges"]}
    k: int = instance["k"]
    if k <= 0:
        return True
    if k > n:
        return False
    vertices = list(range(n))
    for size in range(k, n + 1):
        for subset in itertools.combinations(vertices, size):
            good = True
            for u, v in itertools.combinations(subset, 2):
                if frozenset((u, v)) in edges_set:
                    good = False
                    break
            if good:
                return True
    return False


def generate_all_graphs(n: int) -> List[dict]:
    """Generate every simple undirected graph on n vertices.

    Each graph is represented as a dict with keys ``n`` and ``edges``.
    """
    vertices = list(range(n))
    possible_edges = list(itertools.combinations(vertices, 2))
    graphs = []
    for mask in range(1 << len(possible_edges)):
        edges = []
        for i, e in enumerate(possible_edges):
            if mask & (1 << i):
                edges.append([e[0], e[1]])
        graphs.append({"n": n, "edges": edges})
    return graphs


def main() -> None:
    total_tests = 0
    passed_tests = 0
    # Test all graphs up to 5 vertices (manageable enumeration).
    for n in range(0, 6):
        for src_instance in generate_all_graphs(n):
            problems.ThreeColoring.validate(src_instance)
            src_answer = three_coloring_bruteforce(src_instance)
            tgt_instance = reduce_instance(src_instance)
            problems.IndependentSet.validate(tgt_instance)
            tgt_answer = independent_set_bruteforce(tgt_instance)
            total_tests += 1
            if src_answer == tgt_answer:
                passed_tests += 1
            else:
                print("FAILURE", file=sys.stderr)
                print("Source instance:", json.dumps(src_instance), file=sys.stderr)
                print("Reduced instance:", json.dumps(tgt_instance), file=sys.stderr)
                print("Source answer:", src_answer, "Target answer:", tgt_answer, file=sys.stderr)
    # Additional random tests for slightly larger graphs (n up to 7).
    import random
    random.seed(0)
    for n in range(6, 8):
        for _ in range(200):
            edges = []
            for u, v in itertools.combinations(range(n), 2):
                if random.random() < 0.3:
                    edges.append([u, v])
            src_instance = {"n": n, "edges": edges}
            problems.ThreeColoring.validate(src_instance)
            src_answer = three_coloring_bruteforce(src_instance)
            tgt_instance = reduce_instance(src_instance)
            problems.IndependentSet.validate(tgt_instance)
            tgt_answer = independent_set_bruteforce(tgt_instance)
            total_tests += 1
            if src_answer == tgt_answer:
                passed_tests += 1
            else:
                print("FAILURE (random)", file=sys.stderr)
                print(src_instance, file=sys.stderr)
                print(tgt_instance, file=sys.stderr)
                print(src_answer, tgt_answer, file=sys.stderr)
    verdict = {
        "verified": passed_tests == total_tests,
        "tests_run": total_tests,
        "tests_passed": passed_tests,
    }
    with open("verdict.json", "w") as f:
        json.dump(verdict, f)
    print(json.dumps(verdict))

if __name__ == "__main__":
    main()
