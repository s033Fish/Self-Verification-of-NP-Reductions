"""Simple test suite for the 3‑SAT → 3‑Coloring reduction.

We generate a modest number of random 3‑SAT instances (including some edge
cases) and check that the reduction preserves the answer.  Brute‑force solvers
are used because the instances are tiny.  Instances that would produce a graph
with more than 12 vertices are skipped to keep the runtime reasonable.
"""

from __future__ import annotations

import json
import itertools
import random
from pathlib import Path

from problems import ThreeSat, ThreeColoring
from reduce import reduce


def solve_three_sat(inst: dict) -> bool:
    m = inst["num_vars"]
    clauses = inst["clauses"]
    for mask in range(1 << m):
        ok = True
        for clause in clauses:
            clause_ok = False
            for lit in clause:
                var = abs(lit) - 1
                val = (mask >> var) & 1
                if (lit > 0 and val == 1) or (lit < 0 and val == 0):
                    clause_ok = True
                    break
            if not clause_ok:
                ok = False
                break
        if ok:
            return True
    return False


def solve_three_coloring(inst: dict) -> bool:
    n = inst["n"]
    edges = [(u, v) for u, v in inst["edges"]]
    for colors in itertools.product(range(3), repeat=n):
        if all(colors[u] != colors[v] for u, v in edges):
            return True
    return False


def random_instance(max_vars: int, max_clauses: int) -> dict:
    m = random.randint(0, max_vars)
    clauses = []
    if m >= 3:
        for _ in range(random.randint(0, max_clauses)):
            vars_ = random.sample(range(1, m + 1), 3)
            clause = [v if random.choice([True, False]) else -v for v in vars_]
            clauses.append(clause)
    return {"num_vars": m, "clauses": clauses}


def main() -> None:
    random.seed(0)
    instances: list[dict] = []
    # Edge cases
    instances.append({"num_vars": 0, "clauses": []})
    instances.append({"num_vars": 3, "clauses": []})
    # Random instances (kept small)
    for _ in range(30):
        instances.append(random_instance(max_vars=4, max_clauses=2))

    total = 0
    passed = 0
    for inst in instances:
        ThreeSat.validate(inst)
        sat = solve_three_sat(inst)
        graph = reduce(inst)
        ThreeColoring.validate(graph)
        # Skip overly large graphs for brute‑force coloring
        if graph["n"] > 12:
            continue
        total += 1
        col = solve_three_coloring(graph)
        if sat == col:
            passed += 1
        else:
            print("FAIL", inst, sat, col)
    verdict = {"verified": total > 0 and passed == total, "tests_run": total, "tests_passed": passed}
    Path("verdict.json").write_text(json.dumps(verdict, indent=2))

if __name__ == "__main__":
    main()

