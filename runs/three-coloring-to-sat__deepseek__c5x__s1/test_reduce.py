"""Test suite for the reduction from ThreeColoring to SAT.

The repository provides a `reduce` function that maps a 3‑Coloring instance
to a SAT instance.  This file implements brute‑force solvers for both
problems, generates a variety of small graph instances, applies the
reduction and checks that the answers agree.

The script exits with a non‑zero status if any test fails, otherwise it
creates ``verdict.json`` with the required fields.
"""

from __future__ import annotations

import itertools
import json
import sys
from typing import List, Dict, Tuple

from problems import ThreeColoring, Sat
from reduce import reduce as reduce_instance


def solve_three_coloring(instance: Dict) -> bool:
    """Brute‑force solver for 3‑Coloring.

    Returns True iff the graph is 3‑colorable.
    """
    ThreeColoring.validate(instance)
    n: int = instance["n"]
    edges: List[Tuple[int, int]] = [tuple(e) for e in instance["edges"]]
    # iterate over all assignments of 0,1,2 to each vertex
    for coloring in itertools.product(range(3), repeat=n):
        ok = True
        for u, v in edges:
            if coloring[u] == coloring[v]:
                ok = False
                break
        if ok:
            return True
    return False


def solve_sat(instance: Dict) -> bool:
    """Brute‑force solver for SAT.

    Returns True iff the CNF formula is satisfiable.
    """
    Sat.validate(instance)
    m: int = instance["num_vars"]
    clauses: List[List[int]] = instance["clauses"]
    # assignment is a tuple of booleans for variables 1..m (index 0 unused)
    for assign in itertools.product([False, True], repeat=m):
        # assign[i] corresponds to variable i+1
        satisfied = True
        for clause in clauses:
            clause_sat = False
            for lit in clause:
                var = abs(lit) - 1
                val = assign[var]
                if lit > 0 and val:
                    clause_sat = True
                    break
                if lit < 0 and not val:
                    clause_sat = True
                    break
            if not clause_sat:
                satisfied = False
                break
        if satisfied:
            return True
    return False


def generate_all_graphs(max_n: int) -> List[Dict]:
    """Generate every simple undirected graph with up to ``max_n`` vertices.

    For n > 0 we consider all subsets of the possible edges ``(i, j)`` with
    ``i < j``.  The empty graph (n = 0) is also included.
    """
    graphs: List[Dict] = []
    for n in range(max_n + 1):
        vertices = list(range(n))
        possible_edges = [(i, j) for i in vertices for j in vertices if i < j]
        for edge_subset in itertools.product([0, 1], repeat=len(possible_edges)):
            edges = [list(e) for e, include in zip(possible_edges, edge_subset) if include]
            graphs.append({"n": n, "edges": edges})
    return graphs


def main() -> None:
    # generate exhaustive graphs up to 4 vertices (manageable size)
    test_instances = generate_all_graphs(4)
    # also add a few random larger instances (n=5,6) to increase coverage
    import random
    random.seed(0)
    for n in (5, 6):
        for _ in range(20):
            edges = []
            for i in range(n):
                for j in range(i + 1, n):
                    if random.random() < 0.3:
                        edges.append([i, j])
            test_instances.append({"n": n, "edges": edges})

    total = len(test_instances)
    passed = 0
    for idx, instance in enumerate(test_instances, 1):
        # Validate source instance (should be valid by construction)
        try:
            ThreeColoring.validate(instance)
        except Exception as e:
            print(f"Invalid source instance #{idx}: {e}", file=sys.stderr)
            continue
        # Compute answers
        ans_source = solve_three_coloring(instance)
        reduced = reduce_instance(instance)
        ans_target = solve_sat(reduced)
        if ans_source == ans_target:
            passed += 1
        else:
            print(
                f"Mismatch on instance #{idx}: source={ans_source}, target={ans_target}\n{instance}\nReduced={reduced}",
                file=sys.stderr,
            )
    verdict = {"verified": passed == total, "tests_run": total, "tests_passed": passed}
    with open("verdict.json", "w") as f:
        json.dump(verdict, f)
    # Exit with non‑zero if not verified so CI can see failure
    if not verdict["verified"]:
        sys.exit(1)

if __name__ == "__main__":
    main()
