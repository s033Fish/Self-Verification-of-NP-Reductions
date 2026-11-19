"""Brute-force solvers for both problems plus tests for the reduction."""

from __future__ import annotations

import itertools
import random

from problems import HamiltonianPath, Sat
from reduce import reduce


# ---------------------------------------------------------------- solvers

def solve_hamiltonian_path(instance: dict) -> bool:
    """Brute force: try every permutation of vertices as the path order."""
    n = instance["n"]
    if n == 0:
        return False
    if n == 1:
        return True
    edges = {frozenset(e) for e in instance["edges"]}
    for perm in itertools.permutations(range(n)):
        if all(frozenset((perm[i], perm[i + 1])) in edges for i in range(n - 1)):
            return True
    return False


def solve_sat(instance: dict) -> bool:
    """Exact DPLL SAT solver (unit propagation + branching)."""
    m = instance["num_vars"]
    clauses = [set(c) for c in instance["clauses"]]

    def dpll(clauses, assignment):
        # Simplify with current assignment.
        new_clauses = []
        for clause in clauses:
            sat = False
            rest = set()
            for lit in clause:
                var = abs(lit)
                if var in assignment:
                    if assignment[var] == (lit > 0):
                        sat = True
                        break
                else:
                    rest.add(lit)
            if sat:
                continue
            if not rest:
                return False
            new_clauses.append(rest)
        clauses = new_clauses
        if not clauses:
            return True
        # Unit propagation.
        for clause in clauses:
            if len(clause) == 1:
                lit = next(iter(clause))
                var = abs(lit)
                val = lit > 0
                if var in assignment and assignment[var] != val:
                    return False
                assignment = dict(assignment)
                assignment[var] = val
                return dpll(clauses, assignment)
        # Choose a variable.
        var = abs(next(iter(clauses[0])))
        for val in (True, False):
            assignment = dict(assignment)
            assignment[var] = val
            if dpll(clauses, assignment):
                return True
        return False

    return dpll(clauses, {})


# ---------------------------------------------------------------- helpers

def all_graphs(n: int):
    """All undirected simple graphs on n labelled vertices."""
    pairs = [(u, v) for u in range(n) for v in range(u + 1, n)]
    for mask in range(1 << len(pairs)):
        edges = [list(p) for k, p in enumerate(pairs) if mask >> k & 1]
        yield {"n": n, "edges": edges}


def check(instance: dict) -> bool:
    """Validate, reduce, validate, and compare answers."""
    HamiltonianPath.validate(instance)
    reduced = reduce(instance)
    Sat.validate(reduced)
    src = solve_hamiltonian_path(instance)
    tgt = solve_sat(reduced)
    assert src == tgt, (instance, reduced, src, tgt)
    return src


# ---------------------------------------------------------------- tests

def main() -> None:
    tests_run = 0
    tests_passed = 0

    def run(name: str, fn) -> None:
        nonlocal tests_run, tests_passed
        tests_run += 1
        try:
            fn()
        except AssertionError as exc:
            print(f"FAIL {name}: {exc}")
        else:
            tests_passed += 1
            print(f"pass {name}")

    # Exhaustive over all graphs with n = 0..5.
    def exhaustive() -> None:
        for n in range(0, 6):
            for g in all_graphs(n):
                check(g)

    run("exhaustive n=0..5 (all graphs)", exhaustive)

    # Random sample of n = 6 graphs (all 2^15 would be too slow to solve).
    def sample6() -> None:
        rng = random.Random(999)
        for _ in range(2000):
            pairs = [(u, v) for u in range(6) for v in range(u + 1, 6)]
            edges = [list(e) for e in pairs if rng.random() < rng.random()]
            check({"n": 6, "edges": edges})

    run("random sample n=6", sample6)

    # Random larger sparse/dense graphs.
    def random_graphs() -> None:
        rng = random.Random(12345)
        for _ in range(300):
            n = rng.randint(0, 9)
            pairs = [(u, v) for u in range(n) for v in range(u + 1, n)]
            p = rng.random()
            edges = [list(e) for e in pairs if rng.random() < p]
            check({"n": n, "edges": edges})

    run("random graphs n=0..9", random_graphs)

    # Hand-picked edge cases.
    def edge_cases() -> None:
        assert check({"n": 0, "edges": []}) is False
        assert check({"n": 1, "edges": []}) is True
        assert check({"n": 2, "edges": []}) is False
        assert check({"n": 2, "edges": [[0, 1]]}) is True
        # Path graph 0-1-2-3.
        assert check({"n": 4, "edges": [[0, 1], [1, 2], [2, 3]]}) is True
        # Star with 4 leaves has no Hamiltonian path.
        assert check({"n": 5, "edges": [[0, 1], [0, 2], [0, 3], [0, 4]]}) is False
        # Complete graph always yes for n >= 1.
        for n in range(1, 9):
            edges = [[u, v] for u in range(n) for v in range(u + 1, n)]
            assert check({"n": n, "edges": edges}) is True

    run("hand-picked edge cases", edge_cases)

    # Verify the reduction output format on a sample.
    def format_check() -> None:
        out = reduce({"n": 3, "edges": [[0, 1], [1, 2]]})
        assert set(out) == {"num_vars", "clauses"}
        assert out["num_vars"] == 9
        assert all(isinstance(c, list) for c in out["clauses"])

    run("output format", format_check)

    print(f"\ntests_run={tests_run} tests_passed={tests_passed}")
    assert tests_run == tests_passed


if __name__ == "__main__":
    main()
