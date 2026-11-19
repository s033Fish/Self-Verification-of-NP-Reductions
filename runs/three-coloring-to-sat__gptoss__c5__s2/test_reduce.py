"""Test the reduction from ThreeColoring to SAT.

The script enumerates all small graphs (up to 4 vertices) and checks that
the answer of the source instance matches the answer of the reduced SAT
instance.  It uses exhaustive brute‑force solvers for both problems.

The result of the test run is written to ``verdict.json`` with the fields
required by the task description.
"""

from __future__ import annotations

import itertools
import json
from pathlib import Path

from problems import ThreeColoring, Sat
from reduce import reduce


def solve_three_coloring(instance: dict) -> bool:
    """Brute‑force solver for 3‑Coloring.

    Returns True iff the graph is 3‑colorable.
    """
    n: int = instance["n"]
    edges: list[list[int]] = instance["edges"]
    for colors in itertools.product(range(3), repeat=n):
        ok = True
        for u, v in edges:
            if colors[u] == colors[v]:
                ok = False
                break
        if ok:
            return True
    return False


def solve_sat(instance: dict) -> bool:
    """Brute‑force solver for SAT.

    Returns True iff the CNF formula is satisfiable.
    """
    m: int = instance["num_vars"]
    clauses: list[list[int]] = instance["clauses"]
    for bits in itertools.product([False, True], repeat=m):
        assignment = {i + 1: bits[i] for i in range(m)}
        satisfied = True
        for clause in clauses:
            if not clause:
                satisfied = False
                break
            clause_sat = False
            for lit in clause:
                var = abs(lit)
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


def generate_graph_instances(max_n: int = 4) -> list[dict]:
    """Generate all simple undirected graphs with up to ``max_n`` vertices.

    Each instance is a dict matching the ``ThreeColoring`` format.
    """
    instances: list[dict] = []
    for n in range(max_n + 1):
        possible_edges = [(i, j) for i in range(n) for j in range(i + 1, n)]
        for r in range(len(possible_edges) + 1):
            for combo in itertools.combinations(possible_edges, r):
                edges = [[u, v] for u, v in combo]
                instances.append({"n": n, "edges": edges})
    return instances


def main() -> None:
    instances = generate_graph_instances(4)
    total = len(instances)
    passed = 0
    for inst in instances:
        ThreeColoring.validate(inst)
        source_ans = solve_three_coloring(inst)
        sat_inst = reduce(inst)
        Sat.validate(sat_inst)
        target_ans = solve_sat(sat_inst)
        if source_ans == target_ans:
            passed += 1
        else:
            print("Mismatch found:")
            print(json.dumps(inst, indent=2))
            print("source answer", source_ans)
            print("target answer", target_ans)
            break
    verified = passed == total
    verdict = {"verified": verified, "tests_run": total, "tests_passed": passed}
    Path("verdict.json").write_text(json.dumps(verdict, indent=2))
    print(json.dumps(verdict, indent=2))

if __name__ == "__main__":
    main()
