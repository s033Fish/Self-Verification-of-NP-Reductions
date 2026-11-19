"""Automated tests for the Hamiltonian Path → SAT reduction.

The repository provides only validation functions for the two problems.
This test suite implements tiny brute‑force solvers for both problems and
checks that ``reduce`` preserves the answer on a wide range of random
instances (including the edge cases handled specially in the reduction).

The test runner simply executes the script; it prints a summary and exits
with status 0 on success.  The number of generated instances is modest so
that the brute‑force checks finish quickly.
"""

from __future__ import annotations

import itertools
import json
import random
import sys
from typing import List, Dict, Any

from problems import HamiltonianPath, Sat
from reduce import reduce as reduce_instance


def hamiltonian_path_bruteforce(instance: Dict[str, Any]) -> bool:
    """Return True iff the Hamiltonian Path instance is a YES instance.

    The implementation enumerates all permutations of the vertices and
    checks whether the consecutive pairs are edges of the graph.
    """
    n = instance["n"]
    edges = {frozenset(e) for e in instance["edges"]}
    if n == 0:
        return False
    if n == 1:
        return True
    vertices = list(range(n))
    for perm in itertools.permutations(vertices):
        ok = True
        for a, b in zip(perm, perm[1:]):
            if frozenset((a, b)) not in edges:
                ok = False
                break
        if ok:
            return True
    return False


def sat_bruteforce(instance: Dict[str, Any]) -> bool:
    """Return True iff the SAT instance is satisfiable.

    Enumerates all possible assignments for the given number of variables.
    """
    m = instance["num_vars"]
    clauses = instance["clauses"]
    # Empty clause makes the formula unsatisfiable immediately.
    for clause in clauses:
        if not clause:
            return False
    # Enumerate assignments as bit‑vectors where bit i corresponds to variable i+1.
    for bits in range(1 << m):
        assignment = [(bits >> i) & 1 == 1 for i in range(m)]  # True/False list
        satisfied = True
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
                satisfied = False
                break
        if satisfied:
            return True
    return False


def generate_random_instance(max_n: int = 5) -> Dict[str, Any]:
    """Generate a random Hamiltonian‑Path instance with up to ``max_n`` vertices.

    The distribution is uniform over possible edge subsets.
    """
    n = random.randint(0, max_n)
    possible_edges = [(u, v) for u in range(n) for v in range(u + 1, n)]
    edges: List[List[int]] = []
    for (u, v) in possible_edges:
        if random.choice([True, False]):
            edges.append([u, v])
    return {"n": n, "edges": edges}


def main() -> None:
    random.seed(0)
    total = 0
    passed = 0
    # Include explicit edge‑case instances.
    edge_cases = [
        {"n": 0, "edges": []},
        {"n": 1, "edges": []},
        {"n": 2, "edges": []},
        {"n": 2, "edges": [[0, 1]]},
    ]
    # Restrict the random instances to at most 4 vertices to keep brute‑force
    # SAT checking tractable (2^16 = 65536 assignments).
    instances = edge_cases + [generate_random_instance(max_n=4) for _ in range(100)]
    for inst in instances:
        total += 1
        # Validate source instance (should not raise).
        HamiltonianPath.validate(inst)
        hp_answer = hamiltonian_path_bruteforce(inst)
        sat_inst = reduce_instance(inst)
        # Validate reduced instance.
        Sat.validate(sat_inst)
        sat_answer = sat_bruteforce(sat_inst)
        if hp_answer == sat_answer:
            passed += 1
        else:
            print("Mismatch!", file=sys.stderr)
            print("Source:", json.dumps(inst), file=sys.stderr)
            print("Reduced:", json.dumps(sat_inst), file=sys.stderr)
            print("HP answer", hp_answer, "SAT answer", sat_answer, file=sys.stderr)
    # Write verdict file.
    verdict = {
        "verified": passed == total,
        "tests_run": total,
        "tests_passed": passed,
    }
    with open("verdict.json", "w") as f:
        json.dump(verdict, f)
    print(json.dumps(verdict))
    sys.exit(0 if passed == total else 1)

if __name__ == "__main__":
    main()
