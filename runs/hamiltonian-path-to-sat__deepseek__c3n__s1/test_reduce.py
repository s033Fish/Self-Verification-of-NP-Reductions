"""Tests for the Hamiltonian Path -> SAT reduction in reduce.py.

Includes exact solvers for both problems (written from the problem
definitions) and compares their answers on many small source instances.
"""

from __future__ import annotations

import itertools
import random

from problems import HamiltonianPath, Sat
from reduce import reduce


# ----------------------------------------------------------------------
# Exact solvers

def hp_solve(instance: dict) -> bool:
    """Brute force Hamiltonian Path (undirected, any endpoints)."""
    n = instance["n"]
    edges = {frozenset(e) for e in instance["edges"]}
    if n == 0:
        return False
    if n == 1:
        return True
    for perm in itertools.permutations(range(n)):
        if all(frozenset((perm[i], perm[i + 1])) in edges for i in range(n - 1)):
            return True
    return False


def sat_solve(instance: dict) -> bool:
    """Exact CNF satisfiability via DPLL with unit propagation.

    This is an independent exact solver (not the reduction) used to check
    the reduction's answer.  Variables are 1..num_vars.
    """
    m = instance["num_vars"]
    clauses = [list(c) for c in instance["clauses"]]

    def simplify(clauses, assignment):
        # assignment: dict var -> bool.  Returns (new_clauses, ok).
        new_clauses = []
        for clause in clauses:
            satisfied = False
            remaining = []
            for lit in clause:
                var = abs(lit)
                if var in assignment:
                    if (lit > 0) == assignment[var]:
                        satisfied = True
                        break
                else:
                    remaining.append(lit)
            if satisfied:
                continue
            new_clauses.append(remaining)
        return new_clauses

    def dpll(clauses, assignment):
        clauses = simplify(clauses, assignment)
        # Empty clause -> conflict.
        if any(len(c) == 0 for c in clauses):
            return None
        # All clauses satisfied.
        if not clauses:
            return dict(assignment)
        # Unit propagation.
        unit = None
        for c in clauses:
            if len(c) == 1:
                unit = c[0]
                break
        if unit is not None:
            var = abs(unit)
            val = unit > 0
            if var in assignment and assignment[var] != val:
                return None
            new_assignment = dict(assignment)
            new_assignment[var] = val
            return dpll(clauses, new_assignment)
        # Pure literal elimination.
        polarity = {}
        for c in clauses:
            for lit in c:
                var = abs(lit)
                polarity.setdefault(var, set()).add(lit > 0)
        pure = None
        for var, pols in polarity.items():
            if len(pols) == 1:
                pure = (var, next(iter(pols)))
                break
        if pure is not None:
            new_assignment = dict(assignment)
            new_assignment[pure[0]] = pure[1]
            return dpll(clauses, new_assignment)
        # Branch on the variable occurring most often.
        counts = {}
        for c in clauses:
            for lit in c:
                counts[abs(lit)] = counts.get(abs(lit), 0) + 1
        var = max(counts, key=counts.get)
        for val in (True, False):
            new_assignment = dict(assignment)
            new_assignment[var] = val
            result = dpll(clauses, new_assignment)
            if result is not None:
                return result
        return None

    # Variables not appearing at all are free; DPLL handles them.
    return dpll(clauses, {}) is not None


# ----------------------------------------------------------------------
# Instance generation

def all_graphs(n: int):
    """Yield every undirected simple graph on n vertices."""
    pairs = list(itertools.combinations(range(n), 2))
    for mask in range(1 << len(pairs)):
        edges = [list(pairs[i]) for i in range(len(pairs)) if (mask >> i) & 1]
        yield {"n": n, "edges": edges}


def random_graph(n: int, p: float, rng: random.Random) -> dict:
    edges = []
    for u, v in itertools.combinations(range(n), 2):
        if rng.random() < p:
            edges.append([u, v])
    return {"n": n, "edges": edges}


# ----------------------------------------------------------------------
# Tests

def main() -> None:
    tests_run = 0
    tests_passed = 0

    def check(instance: dict) -> None:
        nonlocal tests_run, tests_passed
        tests_run += 1
        # Both instances must validate against the official validators.
        HamiltonianPath.validate(instance)
        reduced = reduce(instance)
        Sat.validate(reduced)
        expected = hp_solve(instance)
        got = sat_solve(reduced)
        assert expected == got, (
            f"mismatch on {instance}: expected {expected}, got {got}, "
            f"reduced={reduced}"
        )
        tests_passed += 1

    # Exhaustive over all graphs with up to 5 vertices.
    for n in range(0, 6):
        for graph in all_graphs(n):
            check(graph)

    # Random larger instances.
    rng = random.Random(12345)
    for _ in range(400):
        n = rng.randint(0, 7)
        p = rng.choice([0.0, 0.15, 0.3, 0.5, 0.8, 1.0])
        check(random_graph(n, p, rng))

    # Explicit edge cases.
    check({"n": 0, "edges": []})
    check({"n": 1, "edges": []})
    check({"n": 2, "edges": []})
    check({"n": 2, "edges": [[0, 1]]})
    check({"n": 3, "edges": [[0, 1], [1, 2]]})
    check({"n": 3, "edges": [[0, 1]]})
    check({"n": 4, "edges": [[0, 1], [1, 2], [2, 3]]})
    check({"n": 4, "edges": [[0, 1], [2, 3]]})

    # n = 0 must map to an unsatisfiable formula.
    assert sat_solve(reduce({"n": 0, "edges": []})) is False
    tests_run += 1
    tests_passed += 1

    print(f"tests_run={tests_run} tests_passed={tests_passed}")
    assert tests_run == tests_passed


if __name__ == "__main__":
    main()
