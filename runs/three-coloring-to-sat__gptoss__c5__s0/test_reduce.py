"""Test the reduction from ThreeColoring to SAT.

The script enumerates all small graphs (up to 5 vertices) and checks that
the SAT instance produced by ``reduce`` is satisfiable exactly when the
original graph is 3‑colorable.

It also validates that ``reduce`` does not raise any unexpected errors
and that the produced SAT instance passes the problem validator.

The script prints a JSON object with the verification result, matching the required ``verdict.json`` format.
"""

from __future__ import annotations

import itertools
import json
import sys
from typing import List, Dict, Tuple

from problems import ThreeColoring, Sat
from reduce import reduce as reduce_instance


def three_coloring_bruteforce(instance: Dict) -> bool:
    """Return True iff the graph is 3‑colorable.

    The instance is assumed to be validated already.
    """
    n: int = instance["n"]
    edges: List[Tuple[int, int]] = [tuple(e) for e in instance["edges"]]
    # iterate over all assignments of colors 0,1,2 to each vertex
    for colors in itertools.product(range(3), repeat=n):
        ok = True
        for u, v in edges:
            if colors[u] == colors[v]:
                ok = False
                break
        if ok:
            return True
    return False


def sat_bruteforce(instance: Dict) -> bool:
    """Return True iff the CNF formula is satisfiable.

    Handles empty clause (unsatisfiable) and empty clause list (satisfiable).
    """
    m: int = instance["num_vars"]
    clauses: List[List[int]] = instance["clauses"]
    # early detection of empty clause
    for clause in clauses:
        if len(clause) == 0:
            return False
    # iterate over all assignments of truth values to variables 1..m
    for assignment in itertools.product([False, True], repeat=m):
        # assignment[i] corresponds to variable i+1
        satisfied = True
        for clause in clauses:
            clause_sat = False
            for lit in clause:
                var = abs(lit) - 1
                val = assignment[var]
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
    """Generate all simple undirected graphs with vertices 0..n-1 for n<=max_n.
    Returns a list of instances (dicts) as expected by ThreeColoring.
    """
    instances: List[Dict] = []
    for n in range(max_n + 1):
        vertices = list(range(n))
        possible_edges = [(i, j) for i in vertices for j in vertices if i < j]
        for mask in range(1 << len(possible_edges)):
            edges = []
            for idx, (u, v) in enumerate(possible_edges):
                if mask & (1 << idx):
                    edges.append([u, v])
            instances.append({"n": n, "edges": edges})
    return instances


def main() -> None:
    max_n = 5  # keep enumeration tractable
    instances = generate_all_graphs(max_n)
    total = len(instances)
    passed = 0
    for inst in instances:
        # Validate source instance (should never raise)
        ThreeColoring.validate(inst)
        # Compute answers
        expected = three_coloring_bruteforce(inst)
        # Reduce
        try:
            sat_inst = reduce_instance(inst)
        except Exception as e:
            print(f"Reduction raised an exception on instance {inst}: {e}", file=sys.stderr)
            continue
        # Validate target instance
        Sat.validate(sat_inst)
        got = sat_bruteforce(sat_inst)
        if expected == got:
            passed += 1
        else:
            print(f"Mismatch on instance {inst}: expected {expected}, got {got}", file=sys.stderr)
    verdict = {
        "verified": passed == total,
        "tests_run": total,
        "tests_passed": passed,
    }
    # Write verdict.json
    with open("verdict.json", "w", encoding="utf-8") as f:
        json.dump(verdict, f, indent=2)
    # Also print to stdout for visibility
    print(json.dumps(verdict, indent=2))

if __name__ == "__main__":
    main()

