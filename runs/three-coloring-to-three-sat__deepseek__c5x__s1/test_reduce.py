"""Automated tests for the reduction from ThreeColoring to ThreeSat.

The repository provides only validation functions for the two problems.
To verify the correctness of ``reduce.py`` we implement simple brute‑force
solvers for both source and target problems and compare their answers on a
large set of small instances.

For each generated ThreeColoring instance we:
1. Compute the exact answer using a exhaustive colour assignment.
2. Run ``reduce`` to obtain a ThreeSat instance.
3. Validate the produced ThreeSat instance using the problem definition.
4. Solve the ThreeSat instance by enumerating all assignments.
5. Check that both answers agree.

If all tests pass we write ``verdict.json`` with ``verified: true`` and the
number of tests run/passed.  Otherwise ``verified`` is false and the counts
reflect the outcomes.
"""

from __future__ import annotations

import itertools
import json
import sys
from pathlib import Path

# Import the problem definitions and the reduction implementation.
import problems  # provides ThreeColoring and ThreeSat with .validate
from reduce import reduce as reduce_instance


def solve_three_coloring(instance: dict) -> bool:
    """Brute‑force solver for 3‑Coloring.

    Returns True iff the graph described by ``instance`` is 3‑colourable.
    """
    n = instance["n"]
    edges = instance["edges"]
    # Iterate over all colour assignments (3^n possibilities).
    for colors in itertools.product(range(3), repeat=n):
        ok = True
        for u, v in edges:
            if colors[u] == colors[v]:
                ok = False
                break
        if ok:
            return True
    return False


def solve_three_sat(instance: dict) -> bool:
    """Brute‑force SAT solver for 3‑SAT.

    ``instance`` follows the format ``{"num_vars": m, "clauses": [[l,...], ...]}``
    where each literal is an int, positive for true, negative for false.
    """
    m = instance["num_vars"]
    clauses = instance["clauses"]
    # Enumerate all assignments of m boolean variables.
    for bits in range(1 << m):
        # bits's i‑th bit corresponds to variable i+1 being True.
        satisfied = True
        for clause in clauses:
            clause_sat = False
            for lit in clause:
                var = abs(lit) - 1
                val = bool(bits & (1 << var))
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


def generate_all_graphs(max_n: int) -> list[dict]:
    """Generate every simple undirected graph with up to ``max_n`` vertices.

    For n <= max_n we enumerate all subsets of possible edges (n choose 2).
    The total number of graphs grows quickly, so the caller should limit
    ``max_n`` to a small value (e.g., 4) to keep the test suite fast.
    """
    graphs: list[dict] = []
    for n in range(max_n + 1):
        vertices = list(range(n))
        possible_edges = [(i, j) for i in vertices for j in vertices if i < j]
        for edge_mask in range(1 << len(possible_edges)):
            edges = []
            for idx, (u, v) in enumerate(possible_edges):
                if edge_mask & (1 << idx):
                    edges.append([u, v])
            graphs.append({"n": n, "edges": edges})
    return graphs


def main() -> None:
    # Generate a reasonable number of test instances.
    test_instances = generate_all_graphs(max_n=4)  # includes n=0..4
    total = len(test_instances)
    passed = 0

    for instance in test_instances:
        # Validate source instance (should always pass).
        problems.ThreeColoring.validate(instance)
        source_ans = solve_three_coloring(instance)
        # Apply reduction.
        target_instance = reduce_instance(instance)
        # Validate target instance according to ThreeSat definition.
        problems.ThreeSat.validate(target_instance)
        target_ans = solve_three_sat(target_instance)
        if source_ans == target_ans:
            passed += 1
        else:
            print("Mismatch!", instance, file=sys.stderr)
            print("source answer", source_ans, "target answer", target_ans, file=sys.stderr)

    verdict = {
        "verified": passed == total,
        "tests_run": total,
        "tests_passed": passed,
    }
    # Write verdict.json in the repository root.
    Path("verdict.json").write_text(json.dumps(verdict, indent=2))
    print(json.dumps(verdict, indent=2))

if __name__ == "__main__":
    main()
