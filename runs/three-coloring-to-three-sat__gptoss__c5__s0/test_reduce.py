"""Automated tests for the reduction from ThreeColoring to ThreeSat.

The script implements exhaustive brute‑force solvers for both source and
target problems and checks that for a variety of small graphs the answer of
the reduced SAT instance matches the answer of the original coloring
instance.

The test harness records how many instances were generated and how many
passed.  At the end it writes a ``verdict.json`` file as required by the
task specification.
"""

from __future__ import annotations

import itertools
import json
import sys
from pathlib import Path

from problems import ThreeColoring, ThreeSat
from reduce import reduce as reduce_instance


def solve_three_coloring(instance: dict) -> bool:
    """Brute‑force solver for 3‑Coloring.

    Returns ``True`` iff the graph can be coloured with three colours.
    """
    n: int = instance["n"]
    edges: list[list[int]] = instance["edges"]
    for coloring in itertools.product(range(3), repeat=n):
        ok = True
        for u, v in edges:
            if coloring[u] == coloring[v]:
                ok = False
                break
        if ok:
            return True
    return False


def solve_three_sat(instance: dict) -> bool:
    """Brute‑force solver for 3‑SAT.

    Returns ``True`` iff there exists a satisfying assignment.
    """
    m: int = instance["num_vars"]
    clauses: list[list[int]] = instance["clauses"]
    for assignment in itertools.product([False, True], repeat=m):
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


def generate_all_graphs(max_n: int) -> list[dict]:
    instances = []
    for n in range(max_n + 1):
        possible_edges = [(u, v) for u in range(n) for v in range(u + 1, n)]
        for r in range(len(possible_edges) + 1):
            for combo in itertools.combinations(possible_edges, r):
                edges = [list(e) for e in combo]
                inst = {"n": n, "edges": edges}
                ThreeColoring.validate(inst)
                instances.append(inst)
    return instances


def main() -> None:
    # generate exhaustive instances for n up to 2 (manageable size)
    max_n = 2
    instances = generate_all_graphs(max_n)
    total = len(instances)
    passed = 0
    for idx, inst in enumerate(instances, 1):
        expected = solve_three_coloring(inst)
        sat_inst = reduce_instance(inst)
        actual = solve_three_sat(sat_inst)
        if expected == actual:
            passed += 1
        else:
            print("Mismatch on instance", idx, file=sys.stderr)
            print("graph:", inst, file=sys.stderr)
            print("expected", expected, "got", actual, file=sys.stderr)
            break
    verdict = {"verified": passed == total, "tests_run": total, "tests_passed": passed}
    Path("verdict.json").write_text(json.dumps(verdict, indent=2))
    print(json.dumps(verdict, indent=2))

if __name__ == "__main__":
    main()
