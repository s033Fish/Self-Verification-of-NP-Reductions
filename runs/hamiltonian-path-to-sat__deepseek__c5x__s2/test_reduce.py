"""Test the reduction from HamiltonianPath to SAT.

The script implements naive (exponential‑time) solvers for both source and
target problems and checks that for every small graph the answer of the
reduced SAT instance matches the answer of the original Hamiltonian‑Path
instance.

If all checks pass we write a ``verdict.json`` file with ``verified: true``;
otherwise ``verified`` is false.  The file also records how many tests were
run and how many passed.
"""

from __future__ import annotations

import itertools
import json
import sys

# Import the problem definitions and the reduction implementation.
from problems import HamiltonianPath, Sat
from reduce import reduce as reduce_instance


def hamiltonian_path_bruteforce(instance: dict) -> bool:
    """Return True iff the given graph has a Hamiltonian path.

    The implementation follows the exact specification in the docstring of
    :class:`HamiltonianPath`.  It enumerates all permutations of the vertex set
    and checks whether each consecutive pair is an edge.  Edge cases for ``n``
    equal to 0, 1 or 2 are handled explicitly to match the specification.
    """
    n = instance["n"]
    edges = instance["edges"]
    # Edge cases defined in the problem statement.
    if n == 0:
        return False
    if n == 1:
        return True
    if n == 2:
        return [0, 1] in edges or [1, 0] in edges

    # Build adjacency set for O(1) look‑ups.
    adj = {i: set() for i in range(n)}
    for u, v in edges:
        adj[u].add(v)
        adj[v].add(u)

    for perm in itertools.permutations(range(n)):
        ok = True
        for a, b in zip(perm, perm[1:]):
            if b not in adj[a]:
                ok = False
                break
        if ok:
            return True
    return False


def sat_bruteforce(instance: dict) -> bool:
    """Return True iff the CNF formula is satisfiable.

    The function tries every assignment of the ``num_vars`` variables (up to
    2^m possibilities) and checks each clause for a true literal.
    """
    m = instance["num_vars"]
    clauses = instance["clauses"]
    # An empty clause makes the formula unsatisfiable.
    if any(len(c) == 0 for c in clauses):
        return False
    # No clauses -> trivially satisfiable.
    if not clauses:
        return True

    for bits in range(1 << m):
        assignment = [(bits >> i) & 1 == 1 for i in range(m)]
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


def generate_all_graphs(max_n: int = 4):
    """Yield all valid HamiltonianPath instances for n in ``0..max_n``.

    For each ``n`` we iterate over every subset of the possible undirected
    edges ``(u, v)`` with ``u < v``.  The generated instance respects the
    validation rules defined in ``problems.py``.
    """
    for n in range(max_n + 1):
        vertices = list(range(n))
        possible_edges = [(u, v) for u in vertices for v in vertices if u < v]
        for mask in range(1 << len(possible_edges)):
            edges = []
            for i, (u, v) in enumerate(possible_edges):
                if mask & (1 << i):
                    edges.append([u, v])
            instance = {"n": n, "edges": edges}
            # Validation should never fail for generated instances.
            HamiltonianPath.validate(instance)
            yield instance


def main() -> None:
    total = 0
    passed = 0
    for instance in generate_all_graphs(max_n=4):
        total += 1
        hp_ans = hamiltonian_path_bruteforce(instance)
        sat_instance = reduce_instance(instance)
        # Validate the reduced instance according to the Sat problem.
        Sat.validate(sat_instance)
        sat_ans = sat_bruteforce(sat_instance)
        if hp_ans == sat_ans:
            passed += 1
        else:
            print("Mismatch found!", file=sys.stderr)
            print("Graph instance:", instance, file=sys.stderr)
            print("Hamiltonian answer:", hp_ans, file=sys.stderr)
            print("Reduced SAT instance:", sat_instance, file=sys.stderr)
            print("SAT answer:", sat_ans, file=sys.stderr)
            break

    verdict = {
        "verified": passed == total,
        "tests_run": total,
        "tests_passed": passed,
    }
    with open("verdict.json", "w", encoding="utf-8") as f:
        json.dump(verdict, f, indent=2)
    print(json.dumps(verdict, indent=2))

if __name__ == "__main__":
    main()
