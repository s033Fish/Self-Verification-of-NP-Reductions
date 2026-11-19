"""Automated tests for the Hamiltonian Cycle → SAT reduction.

The script enumerates all undirected simple graphs with up to 4 vertices,
computes the answer to the Hamiltonian Cycle problem using a brute‑force
search, reduces the instance to SAT via ``reduce.reduce`` and checks that
the SAT solver (also brute‑force) yields the same answer.  It records the
number of tests executed and how many passed, writing the result to
``verdict.json`` as required by the task description.

The implementation is deliberately straightforward – performance is not a
concern because the search space is tiny (at most 2⁶ = 64 graphs for n=4).
"""

from __future__ import annotations

import itertools
import json
import sys
from typing import List, Tuple

from reduce import reduce as reduce_instance
from problems import HamiltonianCycle, Sat


def hamiltonian_solver(instance: dict) -> bool:
    """Brute‑force Hamiltonian‑cycle decision.

    Returns ``True`` iff the undirected graph described by ``instance``
    contains a Hamiltonian cycle.
    """
    n: int = instance["n"]
    edges: List[Tuple[int, int]] = [tuple(e) for e in instance["edges"]]
    # Edge lookup set for O(1) adjacency checks.
    adj = {frozenset(e) for e in edges}

    # Edge cases defined in the problem statement.
    if n <= 2:
        return False
    if n == 3:
        # Only a triangle is a Hamiltonian cycle.
        return len(edges) == 3 and all(frozenset({i, j}) in adj for i, j in [(0, 1), (1, 2), (2, 0)])

    # For larger n try every permutation of vertices as a cycle.
    for perm in itertools.permutations(range(n)):
        # Check consecutive edges including wrap‑around.
        ok = True
        for i in range(n):
            u = perm[i]
            v = perm[(i + 1) % n]
            if frozenset({u, v}) not in adj:
                ok = False
                break
        if ok:
            return True
    return False


def sat_solver(instance: dict) -> bool:
    """Brute‑force SAT solver for CNF formulas.

    ``instance`` follows the format defined by :class:`Sat` – a dict with
    ``num_vars`` and ``clauses``.  The solver enumerates all possible
    assignments (0/1) to the variables and checks whether every clause has
    at least one true literal.
    """
    m: int = instance["num_vars"]
    clauses: List[List[int]] = instance["clauses"]

    # Edge case: an empty clause makes the formula unsatisfiable.
    for clause in clauses:
        if len(clause) == 0:
            return False
    # Edge case: no clauses → trivially satisfiable.
    if not clauses:
        return True

    # Enumerate all 2^m assignments.
    for bits in range(1 << m):
        # assignment[i] is True iff variable i+1 is true.
        assignment = [(bits >> i) & 1 == 1 for i in range(m)]
        satisfied = True
        for clause in clauses:
            clause_sat = False
            for lit in clause:
                var_index = abs(lit) - 1
                val = assignment[var_index]
                if (lit > 0 and val) or (lit < 0 and not val):
                    clause_sat = True
                    break
            if not clause_sat:
                satisfied = False
                break
        if satisfied:
            return True
    return False


def generate_graphs(max_n: int = 4) -> List[dict]:
    """Yield all simple undirected graphs with up to ``max_n`` vertices.

    The representation matches the expected input format for
    ``HamiltonianCycle.validate`` – a dict with ``n`` and ``edges`` where each
    edge is a two‑element list ``[u, v]`` with ``u < v``.
    """
    graphs: List[dict] = []
    for n in range(max_n + 1):
        vertices = list(range(n))
        possible_edges = [(u, v) for u in vertices for v in vertices if u < v]
        for r in range(len(possible_edges) + 1):
            for combo in itertools.combinations(possible_edges, r):
                # Validate ordering requirement (u < v) already satisfied.
                edges = [[u, v] for u, v in combo]
                graphs.append({"n": n, "edges": edges})
    return graphs


def main() -> None:
    tests_run = 0
    tests_passed = 0
    for instance in generate_graphs(4):
        # Validate the instance using the problem's validator – this also
        # catches any accidental malformed graph.
        try:
            HamiltonianCycle.validate(instance)
        except Exception as e:
            print(f"Invalid generated instance {instance}: {e}", file=sys.stderr)
            continue

        hc_answer = hamiltonian_solver(instance)
        sat_instance = reduce_instance(instance)
        # Validate the produced SAT instance.
        try:
            Sat.validate(sat_instance)
        except Exception as e:
            print(f"Reduction produced invalid SAT instance for {instance}: {e}", file=sys.stderr)
            continue
        sat_answer = sat_solver(sat_instance)
        tests_run += 1
        if hc_answer == sat_answer:
            tests_passed += 1
        else:
            print("Mismatch!", instance, "HC:", hc_answer, "SAT:", sat_answer, file=sys.stderr)

    verdict = {
        "verified": tests_run == tests_passed,
        "tests_run": tests_run,
        "tests_passed": tests_passed,
    }
    with open("verdict.json", "w", encoding="utf-8") as f:
        json.dump(verdict, f, indent=2)
    # Also print the verdict for visibility.
    print(json.dumps(verdict, indent=2))


if __name__ == "__main__":
    main()
