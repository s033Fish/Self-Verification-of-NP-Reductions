"""Brute-force / DPLL solvers + tests comparing them with the reduction."""

from __future__ import annotations

import itertools
import json
import random

from problems import HamiltonianPath, Sat
from reduce import reduce


# ----------------------------------------------------------------------
# Solvers written from the problem definitions
# ----------------------------------------------------------------------

def solve_hamiltonian_path(instance: dict) -> bool:
    n = instance["n"]
    edges = {frozenset((u, v)) for u, v in instance["edges"]}
    if n == 0:
        return False
    if n == 1:
        return True
    for perm in itertools.permutations(range(n)):
        if all(frozenset((perm[i], perm[i + 1])) in edges for i in range(n - 1)):
            return True
    return False


def solve_sat_bruteforce(instance: dict) -> bool:
    m = instance["num_vars"]
    clauses = instance["clauses"]
    for bits in itertools.product([False, True], repeat=m):
        if all(
            any(
                (bits[abs(lit) - 1] if lit > 0 else not bits[abs(lit) - 1])
                for lit in clause
            )
            for clause in clauses
        ):
            return True
    return False


def solve_sat_dpll(instance: dict) -> bool:
    """Simple DPLL satisfiability checker (complete)."""
    num_vars = instance["num_vars"]
    clauses = [list(c) for c in instance["clauses"]]

    def simplify(clauses, var, value):
        out = []
        for clause in clauses:
            if (var if value else -var) in clause:
                continue  # clause satisfied
            new_clause = [lit for lit in clause if lit != (-var if value else var)]
            out.append(new_clause)
        return out

    def dpll(clauses):
        # unit propagation
        while True:
            unit = None
            for clause in clauses:
                if len(clause) == 0:
                    return False
                if len(clause) == 1:
                    unit = clause[0]
                    break
            if unit is None:
                break
            clauses = simplify(clauses, abs(unit), unit > 0)
        if not clauses:
            return True
        # choose a literal
        var = abs(clauses[0][0])
        for value in (True, False):
            if dpll(simplify(clauses, var, value)):
                return True
        return False

    return dpll(clauses)


def solve_sat(instance: dict) -> bool:
    # brute force for tiny formulas, DPLL otherwise
    if instance["num_vars"] <= 12:
        return solve_sat_bruteforce(instance)
    return solve_sat_dpll(instance)


# ----------------------------------------------------------------------
# Instance generators
# ----------------------------------------------------------------------

def random_graph(rng: random.Random, n: int) -> dict:
    possible = [(u, v) for u in range(n) for v in range(u + 1, n)]
    edges = [list(e) for e in possible if rng.random() < 0.5]
    rng.shuffle(edges)
    for e in edges:
        if rng.random() < 0.3:
            e.reverse()
    return {"n": n, "edges": edges}


def all_graphs(n: int):
    possible = [(u, v) for u in range(n) for v in range(u + 1, n)]
    for mask in range(1 << len(possible)):
        edges = [list(possible[i]) for i in range(len(possible)) if mask >> i & 1]
        yield {"n": n, "edges": edges}


# ----------------------------------------------------------------------
# Tests
# ----------------------------------------------------------------------

def main() -> None:
    tests_run = 0
    tests_passed = 0

    def check(instance: dict) -> None:
        nonlocal tests_run, tests_passed
        tests_run += 1
        HamiltonianPath.validate(instance)
        reduced = reduce(instance)
        Sat.validate(reduced)
        src = solve_hamiltonian_path(instance)
        tgt = solve_sat(reduced)
        if src == tgt:
            tests_passed += 1
        else:
            print("MISMATCH", instance, "->", src, "vs", tgt)
            print("reduced:", reduced)

    # Exhaustive over all graphs with n = 0..4 (2^0+2^1+2^3+2^6+2^10 = 1099)
    for n in range(0, 5):
        for g in all_graphs(n):
            check(g)

    # Random graphs n up to 9 (brute force HP feasible; DPLL for SAT)
    rng = random.Random(12345)
    for _ in range(300):
        n = rng.randint(0, 9)
        check(random_graph(rng, n))

    # Denser random graphs, n up to 7
    for _ in range(200):
        n = rng.randint(0, 7)
        possible = [(u, v) for u in range(n) for v in range(u + 1, n)]
        edges = [list(e) for e in possible if rng.random() < 0.8]
        check({"n": n, "edges": edges})

    # Hand-picked edge cases
    check({"n": 0, "edges": []})
    check({"n": 1, "edges": []})
    check({"n": 2, "edges": []})
    check({"n": 2, "edges": [[0, 1]]})
    check({"n": 2, "edges": [[1, 0]]})
    check({"n": 3, "edges": [[0, 1], [1, 2]]})
    check({"n": 3, "edges": [[0, 1]]})
    check({"n": 4, "edges": [[0, 1], [1, 2], [2, 3], [3, 0]]})
    check({"n": 4, "edges": [[0, 1], [1, 2], [2, 3]]})
    check({"n": 5, "edges": [[0, 1], [1, 2], [2, 3], [3, 4]]})

    print(f"tests_run={tests_run} tests_passed={tests_passed}")
    assert tests_run == tests_passed, "some tests failed"

    with open("verdict.json", "w") as fh:
        json.dump(
            {"verified": tests_run == tests_passed,
             "tests_run": tests_run,
             "tests_passed": tests_passed},
            fh,
        )


if __name__ == "__main__":
    main()
