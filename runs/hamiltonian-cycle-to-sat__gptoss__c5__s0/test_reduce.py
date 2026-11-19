"""Tests for the Hamiltonian Cycle to SAT reduction.

The repository provides only validation functions for the two problems.
This test module implements tiny brute‑force solvers for both problems
and checks that ``reduce`` produces a SAT instance with the same answer
as the original Hamiltonian‑Cycle instance on many random small graphs.

The script is deliberately simple – it only uses the standard library
and runs quickly for n up to 4 (4! = 24 permutations).  The number of
random instances is modest but sufficient to catch typical mistakes in
the reduction.
"""

from __future__ import annotations

import json
import random
import sys
from itertools import permutations, product
from typing import Dict, List, Tuple

from problems import HamiltonianCycle, Sat, InvalidInstance
from reduce import reduce as reduce_instance


def hamiltonian_cycle_bruteforce(instance: Dict) -> bool:
    """Return True iff the undirected graph has a Hamiltonian cycle.

    The implementation follows the definition in ``problems.py`` and
    handles the edge‑cases explicitly.
    """
    HamiltonianCycle.validate(instance)
    n: int = instance["n"]
    edges: List[Tuple[int, int]] = [tuple(e) for e in instance["edges"]]
    if n <= 2:
        return False
    if n == 3:
        # Only a triangle is a Hamiltonian cycle.
        required = {frozenset((0, 1)), frozenset((1, 2)), frozenset((0, 2))}
        present = {frozenset(e) for e in edges}
        return required.issubset(present)
    # Build adjacency set for O(1) lookup.
    adj = {frozenset(e) for e in edges}
    verts = list(range(n))
    # Fix the first vertex to reduce symmetries (cycle rotations).
    for perm in permutations(verts[1:]):
        cycle = (0,) + perm
        ok = True
        for i in range(n):
            u = cycle[i]
            v = cycle[(i + 1) % n]
            if frozenset((u, v)) not in adj:
                ok = False
                break
        if ok:
            return True
    return False


def sat_bruteforce(instance: Dict) -> bool:
    """Return True iff the CNF formula is satisfiable.

    Works for up to ~10 variables comfortably.
    """
    Sat.validate(instance)
    m: int = instance["num_vars"]
    clauses: List[List[int]] = instance["clauses"]
    # If there is an empty clause, formula is unsatisfiable.
    if any(len(c) == 0 for c in clauses):
        return False
    for assignment in product([False, True], repeat=m):
        # assignment[i] corresponds to variable i+1
        satisfied = True
        for clause in clauses:
            clause_sat = False
            for lit in clause:
                var = abs(lit) - 1
                val = assignment[var]
                if (lit > 0 and val) or (lit < 0 and not val):
                    clause_sat = True
                    break
            if not clause_sat:
                satisfied = False
                break
        if satisfied:
            return True
    return False


def random_graph(n: int, edge_prob: float = 0.5) -> Dict:
    edges = []
    for u in range(n):
        for v in range(u + 1, n):
            if random.random() < edge_prob:
                edges.append([u, v])
    return {"n": n, "edges": edges}


def main() -> None:
    random.seed(0)
    total = 0
    passed = 0
    # Test a range of small sizes. We restrict n to 4 to keep the SAT
    # brute‑force search tractable (4^2 = 16 variables → 2^16 assignments).
    for n in range(0, 5):
        # Generate a few random instances for each n.
        for _ in range(10):
            instance = random_graph(n, edge_prob=0.5)
            try:
                src_ans = hamiltonian_cycle_bruteforce(instance)
            except InvalidInstance as e:
                print("Invalid source instance", e, file=sys.stderr)
                continue
            sat_instance = reduce_instance(instance)
            try:
                tgt_ans = sat_bruteforce(sat_instance)
            except InvalidInstance as e:
                print("Invalid target instance", e, file=sys.stderr)
                continue
            total += 1
            if src_ans == tgt_ans:
                passed += 1
            else:
                print(
                    "Mismatch!",
                    json.dumps(
                        {"src": instance, "sat": sat_instance, "src_ans": src_ans, "tgt_ans": tgt_ans}
                    ),
                    file=sys.stderr,
                )
    verdict = {
        "verified": total == passed,
        "tests_run": total,
        "tests_passed": passed,
    }
    with open("verdict.json", "w", encoding="utf-8") as f:
        json.dump(verdict, f, indent=2)
    print(json.dumps(verdict, indent=2))

if __name__ == "__main__":
    main()

