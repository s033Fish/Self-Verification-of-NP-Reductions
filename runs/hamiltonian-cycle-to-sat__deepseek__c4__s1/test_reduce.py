"""Solvers and tests for the Hamiltonian Cycle -> SAT reduction."""

from __future__ import annotations

import itertools
import random

from problems import HamiltonianCycle, Sat
from reduce import reduce


# ---------------------------------------------------------------- solvers

def solve_hamiltonian(instance: dict) -> bool:
    """Brute force: fix vertex 0 as start, permute the rest."""
    n = instance["n"]
    edges = instance["edges"]
    if n <= 2:
        return False
    adj = [[False] * n for _ in range(n)]
    for u, v in edges:
        adj[u][v] = True
        adj[v][u] = True
    for perm in itertools.permutations(range(1, n)):
        tour = (0,) + perm
        if all(adj[tour[i]][tour[(i + 1) % n]] for i in range(n)):
            return True
    return False


def solve_sat(instance: dict) -> bool:
    """DPLL-style backtracking SAT solver (complete)."""
    m = instance["num_vars"]
    clauses = [list(c) for c in instance["clauses"]]

    def simplify(clauses, var, value):
        new = []
        for clause in clauses:
            if (var if value else -var) in clause:
                continue  # clause satisfied
            reduced = [lit for lit in clause if lit != (-var if value else var)]
            new.append(reduced)
        return new

    def dpll(clauses):
        # Unit propagation / empty clause detection.
        while True:
            if any(len(c) == 0 for c in clauses):
                return False
            if not clauses:
                return True
            unit = None
            for c in clauses:
                if len(c) == 1:
                    unit = c[0]
                    break
            if unit is None:
                break
            clauses = simplify(clauses, abs(unit), unit > 0)
        # Choose a variable from the first clause.
        var = abs(clauses[0][0])
        return dpll(simplify(clauses, var, True)) or dpll(simplify(clauses, var, False))

    return dpll(clauses)


# ----------------------------------------------------------------- tests

def all_graphs(n: int):
    pairs = list(itertools.combinations(range(n), 2))
    for mask in range(1 << len(pairs)):
        edges = [list(p) for i, p in enumerate(pairs) if mask >> i & 1]
        yield {"n": n, "edges": edges}


def check(instance: dict) -> None:
    HamiltonianCycle.validate(instance)
    reduced = reduce(instance)
    Sat.validate(reduced)
    src = solve_hamiltonian(instance)
    tgt = solve_sat(reduced)
    assert src == tgt, f"MISMATCH src={src} tgt={tgt} instance={instance} reduced={reduced}"


def main() -> None:
    tests_run = 0
    tests_passed = 0

    # Exhaustive over all graphs for n = 0..5.
    for n in range(0, 6):
        for instance in all_graphs(n):
            tests_run += 1
            check(instance)
            tests_passed += 1

    # Random larger graphs.
    rng = random.Random(12345)
    for _ in range(400):
        n = rng.randint(3, 9)
        pairs = list(itertools.combinations(range(n), 2))
        p = rng.choice([0.15, 0.3, 0.5, 0.75, 1.0])
        edges = [list(pair) for pair in pairs if rng.random() < p]
        instance = {"n": n, "edges": edges}
        tests_run += 1
        check(instance)
        tests_passed += 1

    # Explicit edge cases.
    edge_cases = [
        {"n": 0, "edges": []},
        {"n": 1, "edges": []},
        {"n": 2, "edges": [[0, 1]]},
        {"n": 3, "edges": [[0, 1], [1, 2], [0, 2]]},                  # triangle -> yes
        {"n": 3, "edges": [[0, 1], [1, 2]]},                           # path -> no
        {"n": 4, "edges": [[0, 1], [1, 2], [2, 3], [3, 0]]},           # square -> yes
        {"n": 4, "edges": [[0, 1], [1, 2], [2, 3]]},                   # path -> no
        {"n": 5, "edges": [[0, 1], [1, 2], [2, 3], [3, 4], [4, 0]]},   # 5-cycle -> yes
        {"n": 6, "edges": [[i, (i + 1) % 6] for i in range(6)]},       # 6-cycle -> yes
    ]
    for instance in edge_cases:
        tests_run += 1
        check(instance)
        tests_passed += 1

    print(f"tests_run={tests_run} tests_passed={tests_passed}")
    assert tests_run == tests_passed

    with open("verdict.json", "w") as f:
        f.write('{"verified": true, "tests_run": %d, "tests_passed": %d}\n' % (tests_run, tests_passed))


if __name__ == "__main__":
    main()
