"""Test suite for the reduction HamiltonianCycle -> HamiltonianPath.

It enumerates all small graphs (n <= 5) and checks that the answer of the
source instance matches the answer of the reduced target instance.
"""

from __future__ import annotations

import itertools
import json
import sys
from pathlib import Path

# Import the reduction and brute‑force solvers.
from reduce import reduce as reduce_instance
from solve_bruteforce import (
    hamiltonian_cycle_bruteforce,
    hamiltonian_path_bruteforce,
)


def generate_graphs(max_n: int = 5):
    """Yield all valid graph instances with n vertices (0..max_n)."""
    for n in range(max_n + 1):
        # All possible undirected edges without self‑loops.
        possible_edges = [(u, v) for u in range(n) for v in range(u + 1, n)]
        # Iterate over all subsets of possible edges.
        for r in range(len(possible_edges) + 1):
            for combo in itertools.combinations(possible_edges, r):
                edges = [list(e) for e in combo]
                yield {"n": n, "edges": edges}


def main():
    total = 0
    passed = 0
    for instance in generate_graphs(5):
        total += 1
        # Compute answers.
        try:
            source_ans = hamiltonian_cycle_bruteforce(instance)
        except Exception as e:
            print(f"Error in source brute solver on {instance}: {e}", file=sys.stderr)
            continue
        # Reduce.
        try:
            reduced = reduce_instance(instance)
        except Exception as e:
            print(f"Reduction raised on {instance}: {e}", file=sys.stderr)
            continue
        # Compute answer on reduced instance.
        try:
            target_ans = hamiltonian_path_bruteforce(reduced)
        except Exception as e:
            print(f"Error in target brute solver on reduced {reduced}: {e}", file=sys.stderr)
            continue
        if source_ans == target_ans:
            passed += 1
        else:
            print("Mismatch!", instance, "->", reduced, "source", source_ans, "target", target_ans, file=sys.stderr)
    verdict = {
        "verified": passed == total,
        "tests_run": total,
        "tests_passed": passed,
    }
    Path("verdict.json").write_text(json.dumps(verdict, indent=2))
    print(json.dumps(verdict, indent=2))

if __name__ == "__main__":
    main()
