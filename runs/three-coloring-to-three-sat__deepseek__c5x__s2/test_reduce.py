"""Test suite for the reduction from ThreeColoring to ThreeSat.

The test generates all small graph instances (n up to 4) and checks that
the answer of the source problem matches the answer of the reduced target
instance.  It also validates that the reduction output conforms to the
ThreeSat instance format.
"""

from itertools import combinations, product
import json
import sys

import problems
import reduce


def solve_three_coloring(instance):
    """Brute‑force solver for 3‑Coloring.

    Returns True iff the graph is 3‑colorable.
    """
    problems.ThreeColoring.validate(instance)
    n = instance["n"]
    edges = [(u, v) for u, v in instance["edges"]]
    # Try all assignments of colours 0,1,2 to each vertex.
    for colors in product(range(3), repeat=n):
        ok = True
        for u, v in edges:
            if colors[u] == colors[v]:
                ok = False
                break
        if ok:
            return True
    return False


def solve_three_sat(instance):
    """Brute‑force solver for 3‑SAT.

    Returns True iff the CNF formula is satisfiable.
    """
    problems.ThreeSat.validate(instance)
    m = instance["num_vars"]
    clauses = instance["clauses"]
    # Assignment is a tuple of booleans for variables 1..m (index 0 unused).
    for assignment in product([False, True], repeat=m):
        # assignment[i] corresponds to variable i+1
        sat = True
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
                sat = False
                break
        if sat:
            return True
    return False


def generate_graphs(max_n: int):
    """Yield all graph instances with vertices 0..n-1 for n <= max_n.

    For each n we generate every possible subset of the undirected edge set
    without self‑loops or duplicate edges.
    """
    for n in range(max_n + 1):
        vertices = list(range(n))
        possible_edges = list(combinations(vertices, 2))
        for r in range(len(possible_edges) + 1):
            for edge_set in combinations(possible_edges, r):
                # Convert to required list-of-lists format
                edges = [[u, v] for u, v in edge_set]
                yield {"n": n, "edges": edges}


def main():
    total = 0
    passed = 0
    for instance in generate_graphs(4):
        total += 1
        source_ans = solve_three_coloring(instance)
        reduced = reduce.reduce(instance)
        # Validate the reduced instance using the problem's validator.
        try:
            problems.ThreeSat.validate(reduced)
        except Exception as e:
            print("Invalid reduced instance:", e, file=sys.stderr)
            continue
        target_ans = solve_three_sat(reduced)
        if source_ans == target_ans:
            passed += 1
        else:
            print("Mismatch on instance:", json.dumps(instance), file=sys.stderr)
            print("source answer", source_ans, "target answer", target_ans, file=sys.stderr)
    verdict = {
        "verified": passed == total,
        "tests_run": total,
        "tests_passed": passed,
    }
    print(json.dumps(verdict))

if __name__ == "__main__":
    main()

