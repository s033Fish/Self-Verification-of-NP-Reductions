"""Test the reduction from DominatingSet to SAT.

The script implements brute‑force solvers for both source and target
problems based on the specifications in ``problems.py``.  It then generates
many small random instances, validates them, applies ``reduce`` and checks
that the answers agree.

The script prints a JSON object with the fields required for the final
verdict file.
"""

from __future__ import annotations

import json
import random
import sys
from itertools import combinations, product

import problems
import reduce


def solve_dominating_set(instance: dict) -> bool:
    """Brute‑force solver for Dominating Set.

    Returns True iff there exists a dominating set of size at most k.
    """
    n = instance["n"]
    edges = instance["edges"]
    k = instance["k"]

    # Edge cases directly from the problem statement
    if k < 0:
        return False
    if n == 0:
        return True  # empty graph is dominated trivially
    if k >= n:
        return True

    # Build adjacency list
    adj = [set() for _ in range(n)]
    for u, v in edges:
        adj[u].add(v)
        adj[v].add(u)

    vertices = list(range(n))
    for size in range(k + 1):
        for subset in combinations(vertices, size):
            chosen = set(subset)
            dominated = set(chosen)
            for v in chosen:
                dominated.update(adj[v])
            if len(dominated) == n:
                return True
    return False


def solve_sat(instance: dict) -> bool:
    """Brute‑force SAT solver.

    Returns True iff the CNF formula is satisfiable.
    """
    m = instance["num_vars"]
    clauses = instance["clauses"]

    # Empty clause makes formula unsatisfiable
    for clause in clauses:
        if len(clause) == 0:
            return False

    for bits in product([False, True], repeat=m):
        assignment = {i + 1: bits[i] for i in range(m)}
        ok = True
        for clause in clauses:
            clause_ok = False
            for lit in clause:
                var = abs(lit)
                val = assignment[var]
                if lit > 0 and val:
                    clause_ok = True
                    break
                if lit < 0 and not val:
                    clause_ok = True
                    break
            if not clause_ok:
                ok = False
                break
        if ok:
            return True
    return False


def random_instance(max_n: int = 5) -> dict:
    """Generate a random DominatingSet instance.

    n is chosen in [0, max_n]. Edges are a random subset of possible edges.
    k is chosen in [-1, n+1] to cover edge cases.
    """
    n = random.randint(0, max_n)
    possible_edges = [(u, v) for u in range(n) for v in range(u + 1, n)]
    edges = []
    for e in possible_edges:
        if random.choice([True, False]):
            edges.append(list(e))
    k = random.randint(-1, n + 1)
    return {"n": n, "edges": edges, "k": k}


def main() -> None:
    random.seed(0)
    total = 0
    passed = 0
    for _ in range(200):
        inst = random_instance()
        try:
            problems.DominatingSet.validate(inst)
        except Exception as e:
            print(f"Generated invalid instance: {e}", file=sys.stderr)
            continue
        ans_src = solve_dominating_set(inst)
        red = reduce.reduce(inst)
        try:
            problems.Sat.validate(red)
        except Exception as e:
            print(f"Reduction produced invalid SAT instance: {e}", file=sys.stderr)
            continue
        ans_tgt = solve_sat(red)
        total += 1
        if ans_src == ans_tgt:
            passed += 1
        else:
            print("Mismatch!", file=sys.stderr)
            print("Source:", json.dumps(inst), file=sys.stderr)
            print("Reduced:", json.dumps(red), file=sys.stderr)
            print("src ans", ans_src, "tgt ans", ans_tgt, file=sys.stderr)
    verdict = {
        "verified": passed == total,
        "tests_run": total,
        "tests_passed": passed,
    }
    print(json.dumps(verdict))

if __name__ == "__main__":
    main()
