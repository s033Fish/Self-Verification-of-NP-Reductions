"""Test the reduction from ThreeColoring to SAT.

The script brute‑forces both problems for all graphs with up to 4 vertices
and compares the answer of the reduction with the direct solver.  It also
checks that the produced SAT instance validates against the problem
definition.

The script prints a JSON object with the required fields for the final
verdict.
"""

from __future__ import annotations

import itertools
import json
import sys

from problems import ThreeColoring, Sat, InvalidInstance
import reduce


def solve_three_coloring(instance: dict) -> bool:
    """Brute‑force solver for 3‑Coloring.

    Returns True if the graph is 3‑colorable, False otherwise.
    """
    n = instance["n"]
    edges = [(u, v) for u, v in instance["edges"]]
    # iterate over all assignments of colours 0,1,2 to each vertex
    for assignment in itertools.product(range(3), repeat=n):
        ok = True
        for u, v in edges:
            if assignment[u] == assignment[v]:
                ok = False
                break
        if ok:
            return True
    return False


def solve_sat(instance: dict) -> bool:
    """Brute‑force solver for SAT.

    Returns True if the CNF formula is satisfiable.
    """
    m = instance["num_vars"]
    clauses = instance["clauses"]
    # iterate over all truth assignments (True/False) for variables 1..m
    for bits in itertools.product([False, True], repeat=m):
        # bits[i] corresponds to variable i+1
        satisfied = True
        for clause in clauses:
            # empty clause is never satisfied
            clause_sat = False
            for lit in clause:
                var = abs(lit) - 1
                val = bits[var]
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


def all_graphs(max_n: int):
    """Yield all simple undirected graphs with vertices 0..n-1 for n <= max_n.

    Each graph is represented as a dict matching the ThreeColoring instance
    format.
    """
    for n in range(max_n + 1):
        # generate all possible edge sets without self‑loops and without duplicate
        vertices = list(range(n))
        possible_edges = [(i, j) for i in vertices for j in vertices if i < j]
        for r in range(len(possible_edges) + 1):
            for edges in itertools.combinations(possible_edges, r):
                # convert to required list-of-lists format
                edge_list = [[u, v] for u, v in edges]
                yield {"n": n, "edges": edge_list}


def main() -> None:
    tests_run = 0
    tests_passed = 0
    for instance in all_graphs(4):
        # validate source instance (should never raise)
        try:
            ThreeColoring.validate(instance)
        except InvalidInstance as e:
            print("Invalid source instance", instance, e, file=sys.stderr)
            continue

        expected = solve_three_coloring(instance)
        # apply reduction
        reduced = reduce.reduce(instance)
        # validate target instance
        try:
            Sat.validate(reduced)
        except InvalidInstance as e:
            print("Reduction produced invalid SAT instance", reduced, e, file=sys.stderr)
            continue
        actual = solve_sat(reduced)
        tests_run += 1
        if expected == actual:
            tests_passed += 1
        else:
            print("Mismatch on instance", instance, file=sys.stderr)
            print("expected", expected, "got", actual, file=sys.stderr)
    verdict = {
        "verified": tests_run == tests_passed,
        "tests_run": tests_run,
        "tests_passed": tests_passed,
    }
    print(json.dumps(verdict))

if __name__ == "__main__":
    main()
