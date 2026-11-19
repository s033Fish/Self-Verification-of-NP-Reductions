"""Tests comparing brute-force 3-SAT / Clique solvers with the reduction."""

from __future__ import annotations

import itertools
import random

from problems import Clique, ThreeSat
from reduce import reduce


# ----------------------------------------------------------------------
# Brute-force solvers written from the problem definitions.

def solve_three_sat(instance: dict) -> bool:
    ThreeSat.validate(instance)
    num_vars = instance["num_vars"]
    clauses = instance["clauses"]
    for bits in itertools.product([False, True], repeat=num_vars):
        # variable v (1..num_vars) has value bits[v-1]
        if all(
            any((bits[abs(lit) - 1] if lit > 0 else not bits[abs(lit) - 1])
                for lit in clause)
            for clause in clauses
        ):
            return True
    return False


def solve_clique(instance: dict) -> bool:
    Clique.validate(instance)
    n = instance["n"]
    edges = instance["edges"]
    k = instance["k"]
    if k <= 0:
        return True
    if k > n:
        return False
    adj = [[False] * n for _ in range(n)]
    for u, v in edges:
        adj[u][v] = True
        adj[v][u] = True
    for combo in itertools.combinations(range(n), k):
        if all(adj[u][v] for u, v in itertools.combinations(combo, 2)):
            return True
    return False


# ----------------------------------------------------------------------
# Instance generators.

def random_three_sat(num_vars, num_clauses, rng):
    clauses = []
    for _ in range(num_clauses):
        vs = rng.sample(range(1, num_vars + 1), 3)
        clause = [v if rng.random() < 0.5 else -v for v in vs]
        clauses.append(clause)
    return {"num_vars": num_vars, "clauses": clauses}


def all_small_three_sat():
    """Exhaustive-ish enumeration of small instances."""
    instances = []
    # no clauses, various m (including m=0)
    for m in range(0, 4):
        instances.append({"num_vars": m, "clauses": []})
    # m=3, all possible clauses, subsets of size 0..3
    literals = [1, 2, 3, -1, -2, -3]
    all_clauses = []
    for combo in itertools.combinations(literals, 3):
        if len({abs(x) for x in combo}) == 3:
            all_clauses.append(list(combo))
    for size in range(0, 4):
        for chosen in itertools.combinations(all_clauses, size):
            instances.append({"num_vars": 3, "clauses": [list(c) for c in chosen]})
    # m=4 with a few random clause sets
    rng = random.Random(12345)
    for _ in range(300):
        m = rng.randint(3, 5)
        nc = rng.randint(0, 5)
        instances.append(random_three_sat(m, nc, rng))
    return instances


def main():
    tests_run = 0
    tests_passed = 0

    instances = all_small_three_sat()
    for inst in instances:
        tests_run += 1
        src_answer = solve_three_sat(inst)
        reduced = reduce(inst)
        # reduced instance must be valid
        Clique.validate(reduced)
        tgt_answer = solve_clique(reduced)
        if src_answer == tgt_answer:
            tests_passed += 1
        else:
            print("MISMATCH", inst, "->", reduced,
                  "src", src_answer, "tgt", tgt_answer)

    # Extra random larger instances.
    rng = random.Random(999)
    for _ in range(500):
        m = rng.randint(3, 7)
        nc = rng.randint(0, 8)
        inst = random_three_sat(m, nc, rng)
        tests_run += 1
        src_answer = solve_three_sat(inst)
        reduced = reduce(inst)
        Clique.validate(reduced)
        tgt_answer = solve_clique(reduced)
        if src_answer == tgt_answer:
            tests_passed += 1
        else:
            print("MISMATCH", inst, "->", reduced,
                  "src", src_answer, "tgt", tgt_answer)

    print(f"tests_run={tests_run} tests_passed={tests_passed}")
    return tests_run, tests_passed


if __name__ == "__main__":
    main()
