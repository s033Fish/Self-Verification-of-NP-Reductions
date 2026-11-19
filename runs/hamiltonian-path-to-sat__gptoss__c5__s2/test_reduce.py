"""Automated tests for the HamiltonianPath → SAT reduction.

The tests generate small random instances of the source problem, run the
provided ``reduce`` function, and compare the answer of a brute‑force
Hamiltonian‑Path solver with that of a brute‑force SAT solver on the
reduction output.

If all generated instances agree, the reduction is considered verified.
The script prints a JSON object with the verification result and a count of
how many tests were executed.
"""

from __future__ import annotations

import json
import random
import itertools
import sys
from typing import List, Dict, Any

from problems import HamiltonianPath, Sat
from reduce import reduce as reduce_instance


def hamiltonian_path_bruteforce(instance: Dict[str, Any]) -> bool:
    """Return True iff the given HamiltonianPath instance has a Hamiltonian path.

    The algorithm enumerates all permutations of the vertices (n ≤ 5 in the
    tests) and checks whether consecutive vertices in the permutation are
    connected by an edge.
    """
    n = instance["n"]
    edges = {frozenset(e) for e in instance["edges"]}
    if n == 0:
        return False
    if n == 1:
        return True
    for perm in itertools.permutations(range(n)):
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

    Enumerates all assignments for ``num_vars`` (up to 8 in the tests).
    """
    m = instance["num_vars"]
    clauses: List[List[int]] = instance["clauses"]
    for c in clauses:
        if len(c) == 0:
            return False
    for bits in range(1 << m):
        ok = True
        for clause in clauses:
            clause_sat = False
            for lit in clause:
                var = abs(lit) - 1
                val = (bits >> var) & 1
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


def run_tests() -> Dict[str, Any]:
    random.seed(0)
    total = 0
    passed = 0

    edge_cases = [
        {"n": 0, "edges": []},
        {"n": 1, "edges": []},
        {"n": 2, "edges": [[0, 1]]},
        {"n": 2, "edges": []},
    ]
    for inst in edge_cases:
        total += 1
        HamiltonianPath.validate(inst)
        sat_inst = reduce_instance(inst)
        Sat.validate(sat_inst)
        src = hamiltonian_path_bruteforce(inst)
        tgt = sat_bruteforce(sat_inst)
        if src == tgt:
            passed += 1
        else:
            print("Mismatch on edge case", inst, file=sys.stderr)

    # Random small graphs (n up to 4) – larger n would create too many SAT variables
    # for the brute‑force SAT solver used in this test.
    for n in range(3, 5):
        for _ in range(10):
            total += 1
            possible = [(i, j) for i in range(n) for j in range(i + 1, n)]
            edges = [list(e) for e in possible if random.random() < 0.5]
            inst = {"n": n, "edges": edges}
            HamiltonianPath.validate(inst)
            sat_inst = reduce_instance(inst)
            Sat.validate(sat_inst)
            src = hamiltonian_path_bruteforce(inst)
            tgt = sat_bruteforce(sat_inst)
            if src == tgt:
                passed += 1
            else:
                print("Mismatch on instance", inst, file=sys.stderr)

    verified = (passed == total)
    return {"verified": verified, "tests_run": total, "tests_passed": passed}

if __name__ == "__main__":
    result = run_tests()
    print(json.dumps(result))
