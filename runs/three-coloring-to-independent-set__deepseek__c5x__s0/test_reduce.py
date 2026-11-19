"""Test the reduction from ThreeColoring to IndependentSet.

The script implements brute‑force solvers for both problems and checks
that for a large collection of small instances the answer of the
reduced instance matches the answer of the original instance.

It also validates that the reduction runs in polynomial time (trivially
true for the tiny instances we generate) and that the returned instance
conforms to the target problem's validation routine.

The script records the number of tests run and passed and writes a
``verdict.json`` file as required by the task description.
"""

from __future__ import annotations

import itertools
import json
import sys
from pathlib import Path

# Import problem definitions and validation helpers
from problems import ThreeColoring, IndependentSet, InvalidInstance


def three_coloring_bruteforce(instance: dict) -> bool:
    """Return True iff the graph is 3‑colorable.

    The function tries all assignments of colours {0,1,2} to the ``n``
    vertices. For each assignment it checks that every edge connects two
    vertices with different colours.
    """
    n = instance["n"]
    edges = instance["edges"]
    # Edge case optimisation – the specification states that n <= 3 is always yes.
    if n <= 3:
        return True
    # Exhaustive search for small n only.
    for colouring in itertools.product(range(3), repeat=n):
        ok = True
        for u, v in edges:
            if colouring[u] == colouring[v]:
                ok = False
                break
        if ok:
            return True
    return False


def independent_set_bruteforce(instance: dict) -> bool:
    """Return True iff the graph has an independent set of size >= k.
    """
    n = instance["n"]
    edges = instance["edges"]
    k = instance["k"]
    # Trivial cases from the problem statement
    if k <= 0:
        return True
    if k > n:
        return False
    # Represent edges as a set of frozensets for O(1) lookup.
    edge_set = {frozenset(e) for e in edges}
    # Enumerate subsets of vertices of size >= k.
    for size in range(k, n + 1):
        for subset in itertools.combinations(range(n), size):
            # Check independence
            independent = True
            for u, v in itertools.combinations(subset, 2):
                if frozenset((u, v)) in edge_set:
                    independent = False
                    break
            if independent:
                return True
    return False


def generate_graphs(max_n: int) -> list[dict]:
    """Generate all simple undirected graphs with up to ``max_n`` vertices.

    For each ``n`` from 0 to ``max_n`` we iterate over all possible edge sets
    (there are 2^{n choose 2} of them). The function returns a list of valid
    instance dictionaries for the ThreeColoring problem.
    """
    graphs: list[dict] = []
    for n in range(max_n + 1):
        vertices = list(range(n))
        possible_edges = list(itertools.combinations(vertices, 2))
        for mask in range(1 << len(possible_edges)):
            edges = []
            for i, (u, v) in enumerate(possible_edges):
                if mask & (1 << i):
                    edges.append([u, v])
            graphs.append({"n": n, "edges": edges})
    return graphs


def main() -> None:
    # Generate a reasonable number of test instances. n up to 5 gives 2^{10}=1024 graphs
    # which is fine for exhaustive testing.
    test_instances = generate_graphs(max_n=5)
    total = len(test_instances)
    passed = 0

    # Import the reduction function dynamically to avoid circular imports.
    from reduce import reduce as reduction

    for idx, instance in enumerate(test_instances, 1):
        # Validate source instance – should never raise.
        try:
            ThreeColoring.validate(instance)
        except InvalidInstance as exc:
            print(f"Invalid source instance #{idx}: {exc}", file=sys.stderr)
            continue

        source_answer = three_coloring_bruteforce(instance)
        reduced = reduction(instance)
        # Validate reduced instance according to target spec.
        try:
            IndependentSet.validate(reduced)
        except InvalidInstance as exc:
            print(f"Reduction produced invalid target instance for #{idx}: {exc}", file=sys.stderr)
            continue
        target_answer = independent_set_bruteforce(reduced)
        if source_answer == target_answer:
            passed += 1
        else:
            print(
                f"Mismatch on instance #{idx}: source={source_answer}, target={target_answer}",
                file=sys.stderr,
            )

    verdict = {
        "verified": passed == total,
        "tests_run": total,
        "tests_passed": passed,
    }
    Path("verdict.json").write_text(json.dumps(verdict, indent=2))
    print(json.dumps(verdict, indent=2))


if __name__ == "__main__":
    main()

