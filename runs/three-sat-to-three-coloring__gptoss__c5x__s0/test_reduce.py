"""Independent tests for reduce.py (3-SAT -> 3-Coloring).

We implement our own brute-force solvers for both problems directly from the
definitions in problems.py, generate many small source instances (including
exhaustive coverage for m = 3 and random instances for larger m), reduce each
one, and check that the source answer equals the target answer.

Run:  python3 test_reduce.py
"""

from __future__ import annotations

import itertools
import random
from typing import Dict, List, Tuple

from problems import ThreeSat, ThreeColoring
from reduce import reduce


# ----------------------------------------------------------------------
# Brute-force solver for 3-SAT (SOURCE)
# ----------------------------------------------------------------------

def sat_solve(instance: Dict) -> bool:
    """Return True iff the 3-SAT instance is satisfiable (brute force)."""
    ThreeSat.validate(instance)
    m = instance["num_vars"]
    clauses = instance["clauses"]
    for bits in itertools.product((False, True), repeat=m):
        ok = True
        for clause in clauses:
            if not any(
                (bits[abs(lit) - 1] if lit > 0 else not bits[abs(lit) - 1])
                for lit in clause
            ):
                ok = False
                break
        if ok:
            return True
    return False


# ----------------------------------------------------------------------
# Brute-force solver for 3-Coloring (TARGET)
# ----------------------------------------------------------------------

def color_solve(instance: Dict) -> bool:
    """Return True iff the graph is 3-colorable (backtracking with MRV)."""
    ThreeColoring.validate(instance)
    n = instance["n"]
    adj: List[set] = [set() for _ in range(n)]
    for u, v in instance["edges"]:
        adj[u].add(v)
        adj[v].add(u)

    colors = [-1] * n

    def backtrack() -> bool:
        # Most-constrained-variable heuristic.
        best = -1
        best_avail = None
        for v in range(n):
            if colors[v] == -1:
                avail = [
                    c
                    for c in range(3)
                    if all(colors[w] != c for w in adj[v])
                ]
                if best == -1 or len(avail) < len(best_avail):
                    best = v
                    best_avail = avail
                    if not avail:
                        return False
        if best == -1:
            return True
        for c in best_avail:
            colors[best] = c
            if backtrack():
                return True
            colors[best] = -1
        return False

    return backtrack()


# ----------------------------------------------------------------------
# Instance generation
# ----------------------------------------------------------------------

def all_clauses_for_vars(vars_: Tuple[int, ...]) -> List[List[int]]:
    """All clauses using exactly the given variables (one sign each)."""
    out = []
    for signs in itertools.product((1, -1), repeat=len(vars_)):
        out.append([s * v for s, v in zip(signs, vars_)])
    return out


def exhaustive_m3_instances() -> List[Dict]:
    """Every subset of the 8 possible clauses over variables 1,2,3."""
    clauses = all_clauses_for_vars((1, 2, 3))
    instances = []
    for mask in range(1 << len(clauses)):
        chosen = [clauses[i] for i in range(len(clauses)) if mask & (1 << i)]
        instances.append({"num_vars": 3, "clauses": chosen})
    return instances


def random_instances(rng: random.Random, count: int) -> List[Dict]:
    instances = []
    for _ in range(count):
        m = rng.randint(3, 6)
        n_clauses = rng.randint(0, 8)
        clauses = []
        for _ in range(n_clauses):
            vs = rng.sample(range(1, m + 1), 3)
            clauses.append([v if rng.random() < 0.5 else -v for v in vs])
        instances.append({"num_vars": m, "clauses": clauses})
    return instances


def edge_case_instances() -> List[Dict]:
    cases = [
        {"num_vars": 0, "clauses": []},
        {"num_vars": 1, "clauses": []},
        {"num_vars": 2, "clauses": []},
        {"num_vars": 3, "clauses": []},
        {"num_vars": 4, "clauses": []},
        # duplicate clauses (allowed)
        {"num_vars": 3, "clauses": [[1, 2, 3], [1, 2, 3]]},
        # unused variables
        {"num_vars": 5, "clauses": [[1, 2, 3]]},
        # the all-true counterexample
        {
            "num_vars": 3,
            "clauses": [[1, 2, 3], [1, 2, -3], [1, -2, 3], [-1, 2, 3]],
        },
        # trivially unsatisfiable: all 8 clauses
        {
            "num_vars": 3,
            "clauses": all_clauses_for_vars((1, 2, 3)),
        },
    ]
    return cases


# ----------------------------------------------------------------------
# Test driver
# ----------------------------------------------------------------------

def main() -> int:
    rng = random.Random(12345)
    instances = edge_case_instances() + exhaustive_m3_instances()
    instances += random_instances(rng, 400)

    tests_run = 0
    tests_passed = 0
    failures = []

    for inst in instances:
        tests_run += 1
        src = sat_solve(inst)
        graph = reduce(inst)
        # The reduction must return a well-formed target instance.
        ThreeColoring.validate(graph)
        tgt = color_solve(graph)
        if src == tgt:
            tests_passed += 1
        else:
            if len(failures) < 10:
                failures.append((inst, src, tgt))

    print(f"tests_run    = {tests_run}")
    print(f"tests_passed = {tests_passed}")
    print(f"tests_failed = {tests_run - tests_passed}")
    if failures:
        print("\nExample mismatches (source answer != reduced answer):")
        for inst, src, tgt in failures:
            print(f"  {inst}  sat={src}  colorable={tgt}")

    return 0 if tests_passed == tests_run else 1


if __name__ == "__main__":
    raise SystemExit(main())
