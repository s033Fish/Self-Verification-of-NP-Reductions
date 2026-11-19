"""Tests for the Vertex Cover -> SAT reduction in reduce.py.

Contains independent brute-force solvers for both problems, written from
the definitions in problems.py, and compares answers on many small
instances (exhaustive for tiny graphs, random for slightly larger ones).
"""

from __future__ import annotations

import itertools
import random

from problems import VertexCover, Sat
from reduce import reduce


# ----------------------------------------------------------------------
# Brute-force solvers


def solve_vertex_cover(instance) -> bool:
    """True iff some vertex set of size <= k covers every edge."""
    n = instance["n"]
    edges = instance["edges"]
    k = instance["k"]
    if k < 0:
        return False
    if k >= n:
        return True
    for size in range(0, k + 1):
        for chosen in itertools.combinations(range(n), size):
            chosen = set(chosen)
            if all(u in chosen or v in chosen for u, v in edges):
                return True
    return False


def solve_sat_dpll(instance) -> bool:
    """DPLL satisfiability solver for CNF formulas."""
    num_vars = instance["num_vars"]
    clauses = [list(c) for c in instance["clauses"]]

    # Empty clause anywhere -> unsatisfiable.
    if any(len(c) == 0 for c in clauses):
        return False

    def simplify(clauses, assignment):
        """Return simplified clauses or None if a clause became empty."""
        result = []
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
                return None
            result.append(new_clause)
        return result

    def unit_propagate(clauses, assignment):
        changed = True
        while changed:
            changed = False
            for clause in clauses:
                if len(clause) == 1:
                    lit = clause[0]
                    var = abs(lit)
                    val = lit > 0
                    if var in assignment:
                        if assignment[var] != val:
                            return None, assignment
                    else:
                        assignment[var] = val
                        changed = True
            clauses = simplify(clauses, assignment)
            if clauses is None:
                return None, assignment
        return clauses, assignment

    def dpll(clauses, assignment):
        clauses, assignment = unit_propagate(clauses, assignment)
        if clauses is None:
            return False
        if not clauses:
            return True
        # Choose a variable from the first clause.
        var = abs(clauses[0][0])
        for val in (True, False):
            new_assignment = dict(assignment)
            new_assignment[var] = val
            if dpll(clauses, new_assignment):
                return True
        return False

    return dpll(clauses, {})


def solve_sat_bruteforce(instance) -> bool:
    """Try every assignment (only for small num_vars)."""
    num_vars = instance["num_vars"]
    clauses = instance["clauses"]
    for bits in itertools.product((False, True), repeat=num_vars):
        assignment = {i + 1: bits[i] for i in range(num_vars)}
        ok = True
        for clause in clauses:
            if not any((lit > 0) == assignment[abs(lit)] for lit in clause):
                ok = False
                break
        if ok:
            return True
    return False


# ----------------------------------------------------------------------
# Helpers


def all_graphs(n):
    """Yield every simple undirected graph on n vertices as an edge list."""
    pairs = [(u, v) for u in range(n) for v in range(u + 1, n)]
    for mask in range(1 << len(pairs)):
        edges = [list(pairs[i]) for i in range(len(pairs)) if (mask >> i) & 1]
        yield edges


def check_instance(instance, counter):
    VertexCover.validate(instance)
    expected = solve_vertex_cover(instance)
    target = reduce(instance)
    Sat.validate(target)
    got = solve_sat_dpll(target)
    # Cross-check the DPLL solver against brute force when feasible.
    if target["num_vars"] <= 14:
        got_bf = solve_sat_bruteforce(target)
        assert got == got_bf, (instance, target, got, got_bf)
    counter[0] += 1
    if got != expected:
        counter[1] += 1
        print("MISMATCH", instance, "expected", expected, "got", got, target)
    return got == expected


def main():
    counter = [0, 0]  # [tests_run, failures]

    # Exhaustive: all graphs on 0..4 vertices, all relevant k.
    for n in range(0, 5):
        for edges in all_graphs(n):
            for k in range(-2, n + 3):
                check_instance({"n": n, "edges": edges, "k": k}, counter)

    # Exhaustive on n=5 with a smaller set of k values (all 1024 graphs).
    for edges in all_graphs(5):
        for k in (-1, 0, 1, 2, 3, 5, 6):
            check_instance({"n": 5, "edges": edges, "k": k}, counter)

    # Random larger instances.
    rng = random.Random(12345)
    for _ in range(400):
        n = rng.randint(0, 7)
        pairs = [(u, v) for u in range(n) for v in range(u + 1, n)]
        edges = [list(p) for p in pairs if rng.random() < 0.5]
        k = rng.randint(-1, n + 1)
        check_instance({"n": n, "edges": edges, "k": k}, counter)

    # Explicit edge cases.
    check_instance({"n": 0, "edges": [], "k": -1}, counter)
    check_instance({"n": 0, "edges": [], "k": 0}, counter)
    check_instance({"n": 3, "edges": [], "k": 0}, counter)
    check_instance({"n": 3, "edges": [[0, 1], [1, 2], [0, 2]], "k": 1}, counter)
    check_instance({"n": 3, "edges": [[0, 1], [1, 2], [0, 2]], "k": 2}, counter)

    print(f"tests_run={counter[0]} failures={counter[1]}")
    assert counter[1] == 0, "some tests failed"
    return counter[0]


if __name__ == "__main__":
    main()
