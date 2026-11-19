"""Brute-force solvers and tests for the SAT -> Clique reduction."""

import itertools
import random

from problems import Sat, Clique
from reduce import reduce


# ----------------------------------------------------------------------
# Brute-force solvers written from the problem definitions.

def sat_solve(instance):
    num_vars = instance["num_vars"]
    clauses = instance["clauses"]
    for bits in itertools.product([False, True], repeat=num_vars):
        # bits[v-1] is the value of variable v
        if all(any((lit > 0) == bits[abs(lit) - 1] for lit in clause)
               for clause in clauses):
            return True
    return False


def clique_solve(instance):
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
# Instance generation

def random_sat(rng, max_vars=4, max_clauses=5, max_len=3):
    m = rng.randint(0, max_vars)
    clauses = []
    for _ in range(rng.randint(0, max_clauses)):
        length = rng.randint(0, max_len)
        clause = []
        for _ in range(length):
            if m == 0:
                break
            v = rng.randint(1, m)
            clause.append(v if rng.random() < 0.5 else -v)
        clauses.append(clause)
    return {"num_vars": m, "clauses": clauses}


def main():
    rng = random.Random(12345)
    tests_run = 0
    tests_passed = 0

    # Deterministic edge cases.
    edge_cases = [
        {"num_vars": 0, "clauses": []},                 # no clauses: yes
        {"num_vars": 0, "clauses": [[]]},               # empty clause: no
        {"num_vars": 1, "clauses": []},                 # yes
        {"num_vars": 1, "clauses": [[1]]},              # yes
        {"num_vars": 1, "clauses": [[-1]]},             # yes
        {"num_vars": 1, "clauses": [[1], [-1]]},        # no
        {"num_vars": 1, "clauses": [[1, -1]]},          # yes
        {"num_vars": 2, "clauses": [[1, 2], [-1, -2]]}, # yes
        {"num_vars": 2, "clauses": [[1], [1]]},         # yes (dup clause)
        {"num_vars": 2, "clauses": [[1, 1], [-1]]},     # no
        {"num_vars": 3, "clauses": [[1], [-1], [2]]},   # no
        {"num_vars": 3, "clauses": [[1, 2, 3], [-1], [-2], [-3]]},  # no
        {"num_vars": 3, "clauses": [[1, 2], [-1, 3], [-3]]},        # yes
        {"num_vars": 2, "clauses": [[1], [], [2]]},     # no (empty clause)
    ]

    instances = list(edge_cases)
    for _ in range(2000):
        instances.append(random_sat(rng))

    for inst in instances:
        Sat.validate(inst)
        out = reduce(inst)
        Clique.validate(out)
        expected = sat_solve(inst)
        got = clique_solve(out)
        tests_run += 1
        if expected == got:
            tests_passed += 1
        else:
            print("MISMATCH")
            print("  input   :", inst)
            print("  expected:", expected)
            print("  output  :", out)
            print("  got     :", got)
            raise SystemExit(1)

    print(f"tests_run={tests_run} tests_passed={tests_passed}")
    assert tests_passed == tests_run
    return tests_run, tests_passed


if __name__ == "__main__":
    main()
