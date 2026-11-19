"""Test the reduction from ThreeColoring to IndependentSet.

The script enumerates all graphs with up to 5 vertices, checks that the
reduction produces a valid IndependentSet instance, and verifies that the
answers of the source and target instances match.

It reports the number of tests run and how many passed.  The results are
written to ``verdict.json`` as required by the task description.
"""

from __future__ import annotations

import itertools
import json
import sys
from pathlib import Path

import problems
from reduce import reduce


def three_coloring_bruteforce(instance: dict) -> bool:
    """Return True iff the graph is 3‑colorable.

    The instance is assumed to have been validated already.
    """
    n = instance["n"]
    edges = [(u, v) for u, v in instance["edges"]]
    # iterate over all assignments of colours 0,1,2 to n vertices
    for colors in itertools.product(range(3), repeat=n):
        ok = True
        for u, v in edges:
            if colors[u] == colors[v]:
                ok = False
                break
        if ok:
            return True
    return False


def independent_set_bruteforce(instance: dict) -> bool:
    """Return True iff there is an independent set of size >= k.

    The instance is assumed to have been validated already.
    """
    n = instance["n"]
    k = instance["k"]
    edges = {(u, v) for u, v in instance["edges"]}
    # check all subsets of vertices of size >= k
    for r in range(k, n + 1):
        for subset in itertools.combinations(range(n), r):
            # verify independence
            independent = True
            for i, j in itertools.combinations(subset, 2):
                if (i, j) in edges or (j, i) in edges:
                    independent = False
                    break
            if independent:
                return True
    return False


def generate_all_graphs(max_n: int) -> list[dict]:
    """Generate all simple undirected graphs with up to ``max_n`` vertices.

    Each graph is represented as a dict matching the ThreeColoring format.
    """
    graphs: list[dict] = []
    for n in range(max_n + 1):
        # list all possible edges (u < v)
        possible_edges = [(u, v) for u in range(n) for v in range(u + 1, n)]
        for mask in range(1 << len(possible_edges)):
            edges = []
            for i, (u, v) in enumerate(possible_edges):
                if mask & (1 << i):
                    edges.append([u, v])
            graphs.append({"n": n, "edges": edges})
    return graphs


def main() -> None:
    max_n = 5
    instances = generate_all_graphs(max_n)
    total = 0
    passed = 0

    for instance in instances:
        total += 1
        # Validate source instance
        try:
            problems.ThreeColoring.validate(instance)
        except Exception as e:
            print(f"Invalid source instance {instance}: {e}", file=sys.stderr)
            continue

        # Compute answers
        src_ans = three_coloring_bruteforce(instance)
        # Reduce
        tgt_instance = reduce(instance)
        # Validate target instance
        try:
            problems.IndependentSet.validate(tgt_instance)
        except Exception as e:
            print(f"Reduction produced invalid target instance {tgt_instance}: {e}", file=sys.stderr)
            continue
        tgt_ans = independent_set_bruteforce(tgt_instance)
        if src_ans == tgt_ans:
            passed += 1
        else:
            print("Mismatch!", file=sys.stderr)
            print("Source instance:", instance, file=sys.stderr)
            print("Source answer:", src_ans, file=sys.stderr)
            print("Target instance:", tgt_instance, file=sys.stderr)
            print("Target answer:", tgt_ans, file=sys.stderr)

    verdict = {
        "verified": passed == total,
        "tests_run": total,
        "tests_passed": passed,
    }
    Path("verdict.json").write_text(json.dumps(verdict, indent=2))
    print(json.dumps(verdict, indent=2))

if __name__ == "__main__":
    main()
