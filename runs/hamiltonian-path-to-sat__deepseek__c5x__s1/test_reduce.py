"""Test the correctness of the reduction from HamiltonianPath to SAT.

The script brute‑forces both problems for small instances and checks that
`reduce.reduce` produces a SAT instance whose answer matches the original
Hamiltonian Path answer.

It also validates that the reduction respects the problem validation
rules (i.e., the returned instance is a valid SAT instance).

The script prints a JSON object with the verification result, the number
of tests run and the number passed.  It is intended to be executed directly
by the evaluation harness.
"""

from __future__ import annotations

import json
import itertools
import sys

import problems  # type: ignore
import reduce as reduction  # type: ignore


def hamiltonian_path_bruteforce(instance: dict) -> bool:
    """Return True iff the given graph has a Hamiltonian path.

    The instance follows the format defined in ``problems.HamiltonianPath``.
    """
    n = instance["n"]
    edges = set(frozenset(e) for e in instance["edges"])

    # Edge cases defined in the problem statement.
    if n == 0:
        return False
    if n == 1:
        return True
    if n == 2:
        return frozenset([0, 1]) in edges

    # For n >= 3, check all permutations.
    for perm in itertools.permutations(range(n)):
        ok = True
        for a, b in zip(perm, perm[1:]):
            if frozenset([a, b]) not in edges:
                ok = False
                break
        if ok:
            return True
    return False


def sat_bruteforce(instance: dict) -> bool:
    """Return True iff the given CNF formula is satisfiable.

    The instance follows the format defined in ``problems.Sat``.
    """
    m = instance["num_vars"]
    clauses = instance["clauses"]

    # Edge case: any empty clause makes the formula unsatisfiable.
    if any(len(c) == 0 for c in clauses):
        return False
    # No clauses -> trivially satisfiable.
    if not clauses:
        return True

    for bits in range(1 << m):
        # bits i corresponds to variable i+1 (True if bit set).
        assignment = [(bits >> i) & 1 == 1 for i in range(m)]
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


def generate_all_graphs(max_n: int) -> list[dict]:
    """Generate all simple undirected graphs with vertices 0..n-1 for n <= max_n.

    For each n we enumerate all subsets of possible edges (i < j).
    """
    instances: list[dict] = []
    for n in range(max_n + 1):
        vertices = list(range(n))
        possible_edges = [(i, j) for i in vertices for j in vertices if i < j]
        for mask in range(1 << len(possible_edges)):
            edges = []
            for idx, (u, v) in enumerate(possible_edges):
                if (mask >> idx) & 1:
                    edges.append([u, v])
            instances.append({"n": n, "edges": edges})
    return instances


def main() -> None:
    # Generate all graphs up to n=4 (reasonable number of instances).
    max_n = 4
    graphs = generate_all_graphs(max_n)
    tests_run = 0
    tests_passed = 0

    for g in graphs:
        # Validate input instance.
        problems.HamiltonianPath.validate(g)
        hp_answer = hamiltonian_path_bruteforce(g)
        sat_instance = reduction.reduce(g)
        # Validate output instance.
        problems.Sat.validate(sat_instance)
        sat_answer = sat_bruteforce(sat_instance)
        tests_run += 1
        if hp_answer == sat_answer:
            tests_passed += 1
        else:
            print("Mismatch found:", json.dumps({"graph": g, "hp": hp_answer, "sat": sat_answer}), file=sys.stderr)
            break

    verified = tests_run == tests_passed
    result = {"verified": verified, "tests_run": tests_run, "tests_passed": tests_passed}
    print(json.dumps(result))

if __name__ == "__main__":
    main()
