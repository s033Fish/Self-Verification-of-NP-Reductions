"""Test suite for the reduction from Hamiltonian Path to Hamiltonian Cycle.

It enumerates all undirected simple graphs with up to 5 vertices, checks that
the reduction defined in ``reduce.py`` preserves the answer, and writes a
verdict JSON file.
"""

from __future__ import annotations

import json
import itertools
import os
import sys
from typing import List, Dict

# Import problem definitions and the reduction.
import problems
import reduce
from solver import hamiltonian_path, hamiltonian_cycle


def all_graphs(n: int) -> List[Dict]:
    """Return a list of all simple undirected graph instances with ``n`` vertices.

    Each instance is a dict ``{"n": n, "edges": [[u, v], ...]}`` following the
    format used by ``problems.py``.
    """
    vertices = list(range(n))
    possible_edges = [(u, v) for u in vertices for v in vertices if u < v]
    graphs: List[Dict] = []
    for mask in range(1 << len(possible_edges)):
        edges: List[List[int]] = []
        for i, (u, v) in enumerate(possible_edges):
            if mask & (1 << i):
                edges.append([u, v])
        graphs.append({"n": n, "edges": edges})
    return graphs


def main() -> None:
    total_tests = 0
    passed_tests = 0
    # Test for n from 0 to 5 inclusive.
    for n in range(0, 6):
        for instance in all_graphs(n):
            total_tests += 1
            # Validate source instance.
            try:
                problems.HamiltonianPath.validate(instance)
            except Exception as e:
                print(f"Invalid source instance for n={n}: {e}", file=sys.stderr)
                continue
            # Compute answer for source.
            src_answer = hamiltonian_path(instance)
            # Apply reduction.
            reduced = reduce.reduce(instance)
            # Validate target instance.
            try:
                problems.HamiltonianCycle.validate(reduced)
            except Exception as e:
                print(f"Reduction produced invalid target instance for n={n}: {e}", file=sys.stderr)
                continue
            # Compute answer for target.
            tgt_answer = hamiltonian_cycle(reduced)
            if src_answer == tgt_answer:
                passed_tests += 1
            else:
                print(f"Mismatch for n={n}, instance={instance}, reduced={reduced}, src={src_answer}, tgt={tgt_answer}", file=sys.stderr)
    verdict = {
        "verified": passed_tests == total_tests,
        "tests_run": total_tests,
        "tests_passed": passed_tests,
    }
    # Write verdict.json in the current directory.
    with open("verdict.json", "w") as f:
        json.dump(verdict, f, indent=2)
    print(json.dumps(verdict, indent=2))


if __name__ == "__main__":
    main()

