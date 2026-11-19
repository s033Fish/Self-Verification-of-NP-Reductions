"""Brute-force/DPLL solvers for both problems plus tests of the reduction."""

from __future__ import annotations

import itertools
import random

from problems import HamiltonianCycle, Sat
from reduce import reduce


# ----------------------------------------------------------------------
# Solvers written from the problem definitions
# ----------------------------------------------------------------------

def solve_hamiltonian(instance: dict) -> bool:
    """True iff the graph has a Hamiltonian cycle (brute force)."""
    n = instance["n"]
    edges = instance["edges"]
    if n <= 2:
        return False
    edge_set = {frozenset((u, v)) for u, v in edges}
    # Fix vertex 0 as the start; try every ordering of the remaining n-1.
    for perm in itertools.permutations(range(1, n)):
        cycle = (0,) + perm
        ok = True
        for i in range(n):
            u = cycle[i]
            v = cycle[(i + 1) % n]
            if frozenset((u, v)) not in edge_set:
                ok = False
                break
        if ok:
            return True
    return False


def solve_sat(instance: dict) -> bool:
    """True iff the CNF formula is satisfiable (DPLL with unit propagation)."""
    m = instance["num_vars"]
    clauses = [tuple(c) for c in instance["clauses"]]

    def dpll(clauses, assignment):
        # assignment: dict var -> bool
        while True:
            # Simplify clauses under current assignment.
            simplified = []
            unit = None
            for clause in clauses:
                new_clause = []
                satisfied = False
                for lit in clause:
                    var = abs(lit)
                    if var in assignment:
                        val = assignment[var]
                        if (lit > 0) == val:
                            satisfied = True
                            break
                    else:
                        new_clause.append(lit)
                if satisfied:
                    continue
                if not new_clause:
                    return False  # empty clause
                if len(new_clause) == 1:
                    unit = new_clause[0]
                simplified.append(tuple(new_clause))
            if not simplified:
                return True
            if unit is not None:
                assignment = dict(assignment)
                assignment[abs(unit)] = unit > 0
                clauses = simplified
                continue
            # Choose a variable from the first clause.
            var = abs(simplified[0][0])
            for value in (True, False):
                new_assignment = dict(assignment)
                new_assignment[var] = value
                if dpll(simplified, new_assignment):
                    return True
            return False

    return dpll(clauses, {})


# ----------------------------------------------------------------------
# Tests
# ----------------------------------------------------------------------

TESTS_RUN = 0
TESTS_PASSED = 0


def check(instance: dict) -> None:
    global TESTS_RUN, TESTS_PASSED
    TESTS_RUN += 1
    HamiltonianCycle.validate(instance)
    reduced = reduce(instance)
    Sat.validate(reduced)
    expected = solve_hamiltonian(instance)
    got = solve_sat(reduced)
    assert expected == got, (
        f"mismatch on {instance}: hamiltonian={expected}, sat={got}, "
        f"reduced={reduced}"
    )
    TESTS_PASSED += 1


def all_graphs(n: int):
    pairs = [(u, v) for u in range(n) for v in range(u + 1, n)]
    for mask in range(1 << len(pairs)):
        edges = [list(p) for k, p in enumerate(pairs) if mask >> k & 1]
        yield {"n": n, "edges": edges}


def main() -> None:
    # Exhaustive over all graphs with n = 0..5.
    for n in range(0, 6):
        for g in all_graphs(n):
            check(g)

    # Random graphs with n = 6..8.
    rng = random.Random(12345)
    for _ in range(400):
        n = rng.randint(0, 8)
        pairs = [(u, v) for u in range(n) for v in range(u + 1, n)]
        edges = [list(p) for p in pairs if rng.random() < 0.5]
        check({"n": n, "edges": edges})

    # Hand-picked edge cases.
    check({"n": 0, "edges": []})
    check({"n": 1, "edges": []})
    check({"n": 2, "edges": [[0, 1]]})
    check({"n": 3, "edges": [[0, 1], [1, 2]]})          # path -> no
    check({"n": 3, "edges": [[0, 1], [1, 2], [0, 2]]})  # triangle -> yes
    check({"n": 4, "edges": [[0, 1], [1, 2], [2, 3], [3, 0]]})  # square -> yes
    check({"n": 4, "edges": [[0, 1], [1, 2], [2, 3]]})  # path -> no
    check({"n": 5, "edges": [[0, 1], [1, 2], [2, 3], [3, 4], [4, 0]]})  # pentagon -> yes

    # Polynomial-size sanity check: the reduction output must be small.
    big = {"n": 40, "edges": [[i, (i + 1) % 40] for i in range(40)]}
    out = reduce(big)
    Sat.validate(out)
    assert out["num_vars"] == 1600
    # Bound: n + n + 2*n*C(n,2) + n*(n*(n-1)) clauses ~ O(n^3)
    assert len(out["clauses"]) <= 2 * 40 + 2 * 40 * 780 + 40 * 1560

    print(f"tests_run={TESTS_RUN} tests_passed={TESTS_PASSED}")
    assert TESTS_RUN == TESTS_PASSED


if __name__ == "__main__":
    main()
