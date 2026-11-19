"""Test suite for the reduction from ThreeColoring to OneInThreeSat.

The script brute‑forces both source and target problems for a selection of
small graphs and checks that the answer of the reduced instance matches the
answer of the original instance.  It writes a ``verdict.json`` file required
by the task description.
"""

from __future__ import annotations

import json
import itertools
import sys
from pathlib import Path

from problems import ThreeColoring, OneInThreeSat
from reduce import reduce as reduce_instance


def three_coloring_bruteforce(instance: dict) -> bool:
    """Return True iff the graph is 3‑colorable.

    The instance is assumed to be validated already.  We simply try all
    assignments of colours {0,1,2} to the vertices.
    """
    n = instance["n"]
    edges = instance["edges"]
    for colors in itertools.product(range(3), repeat=n):
        ok = True
        for u, v in edges:
            if colors[u] == colors[v]:
                ok = False
                break
        if ok:
            return True
    return False


def one_in_three_sat_bruteforce(instance: dict) -> bool:
    """Return True iff there exists an assignment satisfying the 1‑in‑3 condition.

    ``instance`` follows the ``OneInThreeSat`` format.  Variables are 1‑based.
    """
    m = instance["num_vars"]
    clauses = instance["clauses"]
    for bits in itertools.product([False, True], repeat=m):
        ok = True
        for clause in clauses:
            true_count = 0
            for lit in clause:
                var = lit - 1
                if bits[var]:
                    true_count += 1
            if true_count != 1:
                ok = False
                break
        if ok:
            return True
    return False


def generate_all_graphs(max_n: int) -> list[dict]:
    """Generate all simple undirected graphs with vertices 0..n-1 for n ≤ max_n.
    """
    graphs: list[dict] = []
    for n in range(max_n + 1):
        vertices = list(range(n))
        possible_edges = [(i, j) for i in vertices for j in vertices if i < j]
        for mask in range(1 << len(possible_edges)):
            edges = []
            for idx, (u, v) in enumerate(possible_edges):
                if mask & (1 << idx):
                    edges.append([u, v])
            graphs.append({"n": n, "edges": edges})
    return graphs


def main() -> None:
    # Exhaustively test all graphs up to n=3 (manageable size).
    test_instances = generate_all_graphs(3)
    # Add a limited set of n=4 graphs (up to 3 edges) to keep runtime low.
    n = 4
    vertices = list(range(n))
    possible_edges = [(i, j) for i in vertices for j in vertices if i < j]
    for mask in range(1 << len(possible_edges)):
        if bin(mask).count("1") > 3:
            continue
        edges = []
        for idx, (u, v) in enumerate(possible_edges):
            if mask & (1 << idx):
                edges.append([u, v])
        test_instances.append({"n": n, "edges": edges})

    total = len(test_instances)
    passed = 0
    for instance in test_instances:
        ThreeColoring.validate(instance)
        src_ans = three_coloring_bruteforce(instance)
        reduced = reduce_instance(instance)
        OneInThreeSat.validate(reduced)
        tgt_ans = one_in_three_sat_bruteforce(reduced)
        if src_ans == tgt_ans:
            passed += 1
        else:
            print("Mismatch found!", file=sys.stderr)
            print("Source instance:", instance, file=sys.stderr)
            print("Reduced instance:", reduced, file=sys.stderr)
            print("Source answer:", src_ans, "Target answer:", tgt_ans, file=sys.stderr)
    verdict = {
        "verified": passed == total,
        "tests_run": total,
        "tests_passed": passed,
    }
    Path("verdict.json").write_text(json.dumps(verdict, indent=2))
    print(json.dumps(verdict, indent=2))

if __name__ == "__main__":
    main()
