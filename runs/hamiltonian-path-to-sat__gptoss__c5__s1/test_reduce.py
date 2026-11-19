"""Tests for the Hamiltonian Path → SAT reduction.

The test suite brute‑forces the answer for both problems on tiny instances
and checks that the reduction preserves the answer.

If any test fails the script exits with a non‑zero status code so that the
verdict can be generated automatically.
"""

from __future__ import annotations

import itertools
import json
import sys
from pathlib import Path

from problems import HamiltonianPath, Sat
from reduce import reduce as reduce_instance


def solve_hamiltonian(instance: dict) -> bool:
    """Brute‑force Hamiltonian path solver for tiny graphs.

    Returns True iff there exists a permutation of the vertices that forms a
    path using only edges present in the instance.
    """
    n = instance["n"]
    if n == 0:
        return False
    if n == 1:
        return True
    edges = {frozenset(e) for e in instance["edges"]}
    for perm in itertools.permutations(range(n)):
        ok = True
        for a, b in zip(perm, perm[1:]):
            if frozenset((a, b)) not in edges:
                ok = False
                break
        if ok:
            return True
    return False


def solve_sat(instance: dict) -> bool:
    """Brute‑force SAT solver for tiny formulas.

    Tries all assignments to the variables (up to 6 variables comfortably).
    """
    m = instance["num_vars"]
    clauses = instance["clauses"]
    # Empty clause makes formula unsatisfiable immediately
    for clause in clauses:
        if len(clause) == 0:
            return False
    for bits in range(1 << m):
        # assignment: variable i (1‑based) is True if bit i‑1 is set
        ok = True
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
                ok = False
                break
        if ok:
            return True
    return False


def generate_all_graphs(max_n: int) -> list[dict]:
    """Generate every undirected graph with up to ``max_n`` vertices.

    For each n we iterate over all subsets of the possible edges. The total
    number grows quickly, so we keep ``max_n`` small (4 or 5).
    """
    instances = []
    for n in range(max_n + 1):
        vertices = list(range(n))
        possible_edges = [(u, v) for u in vertices for v in vertices if u < v]
        for mask in range(1 << len(possible_edges)):
            edges = []
            for idx, (u, v) in enumerate(possible_edges):
                if mask & (1 << idx):
                    edges.append([u, v])
            instances.append({"n": n, "edges": edges})
    return instances


def main() -> None:
    max_n = 4  # keep runtime reasonable
    tests = generate_all_graphs(max_n)
    total = len(tests)
    passed = 0
    for idx, hp_inst in enumerate(tests, 1):
        # Validate source instance (should always pass)
        HamiltonianPath.validate(hp_inst)
        hp_ans = solve_hamiltonian(hp_inst)
        sat_inst = reduce_instance(hp_inst)
        # Validate target instance (ensured by reduce)
        Sat.validate(sat_inst)
        sat_ans = solve_sat(sat_inst)
        if hp_ans != sat_ans:
            print(
                f"Mismatch on test {idx}/{total}: n={hp_inst['n']} edges={hp_inst['edges']}",
                file=sys.stderr,
            )
            print(f"Hamiltonian answer: {hp_ans}, SAT answer: {sat_ans}", file=sys.stderr)
            sys.exit(1)
        passed += 1
    # Write verdict.json
    verdict = {"verified": True, "tests_run": total, "tests_passed": passed}
    Path("verdict.json").write_text(json.dumps(verdict))
    print(json.dumps(verdict))

if __name__ == "__main__":
    main()
