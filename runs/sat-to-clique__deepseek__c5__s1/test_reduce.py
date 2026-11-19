"""Independent tests for reduce.py: SAT -> Clique.

We implement brute-force solvers for both problems straight from the
definitions in problems.py, then compare answers on many small source
instances and their reductions.  Every produced target instance is also
validated with problems.py's validators, and every source instance with
Sat.validate.
"""

from __future__ import annotations

import itertools
import random

from problems import Sat, Clique
from reduce import reduce


# ----------------------------------------------------------------------
# Brute-force solvers written from the problem definitions.

def sat_solve(instance: dict) -> bool:
    """True iff some assignment satisfies every clause."""
    m = instance["num_vars"]
    clauses = instance["clauses"]
    for mask in range(1 << m):
        # variable v (1..m) is true iff bit (v-1) of mask is set
        ok = True
        for clause in clauses:
            clause_sat = False
            for lit in clause:
                var = abs(lit)
                value = (mask >> (var - 1)) & 1
                if (lit > 0 and value == 1) or (lit < 0 and value == 0):
                    clause_sat = True
                    break
            if not clause_sat:
                ok = False
                break
        if ok:
            return True
    return False


def clique_solve(instance: dict) -> bool:
    """True iff the graph has a clique of size >= k."""
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
    for comb in itertools.combinations(range(n), k):
        if all(adj[a][b] for a, b in itertools.combinations(comb, 2)):
            return True
    return False


# ----------------------------------------------------------------------
# Instance generation.

def all_clauses(num_vars: int, max_len: int):
    """All clauses (as tuples) over literals +-1..+-num_vars, length 0..max_len."""
    literals = [s * v for v in range(1, num_vars + 1) for s in (1, -1)]
    clauses = [()]
    for length in range(1, max_len + 1):
        clauses.extend(itertools.product(literals, repeat=length))
    return clauses


def exhaustive_instances():
    """Every SAT instance with m in 0..2, <=3 clauses of length <=2."""
    for m in range(0, 3):
        clauses = all_clauses(m, 2)
        for r in range(0, 4):
            for combo in itertools.combinations_with_replacement(clauses, r):
                yield {"num_vars": m, "clauses": [list(c) for c in combo]}


def random_instances(count: int, seed: int = 12345):
    rng = random.Random(seed)
    for _ in range(count):
        m = rng.randint(0, 4)
        nclauses = rng.randint(0, 6)
        clauses = []
        for _ in range(nclauses):
            length = rng.randint(0, 3)
            clause = [rng.choice([1, -1]) * rng.randint(1, m) for _ in range(length)] if m else []
            clauses.append(clause)
        yield {"num_vars": m, "clauses": clauses}


def edge_case_instances():
    return [
        {"num_vars": 0, "clauses": []},                      # no clauses -> yes
        {"num_vars": 0, "clauses": [[]]},                    # empty clause -> no
        {"num_vars": 3, "clauses": [[1], []]},               # empty clause -> no
        {"num_vars": 3, "clauses": [[1, -1]]},               # tautology -> yes
        {"num_vars": 3, "clauses": [[1], [-1]]},             # unsat -> no
        {"num_vars": 3, "clauses": [[1, 1, 1]]},             # repeated literal -> yes
        {"num_vars": 3, "clauses": [[1], [1], [1]]},         # duplicate clauses -> yes
        {"num_vars": 1, "clauses": [[1], [-1], [1, -1]]},    # unsat
        {"num_vars": 2, "clauses": [[1, 2], [-1, 2], [1, -2], [-1, -2]]},  # unsat
        {"num_vars": 2, "clauses": [[1, 2], [-1, 2], [1, -2]]},            # sat
        {"num_vars": 5, "clauses": []},                      # unused vars, no clauses -> yes
    ]


# ----------------------------------------------------------------------
# Test driver.

def main() -> int:
    tests_run = 0
    tests_passed = 0
    failures = []

    def check(instance: dict):
        nonlocal tests_run, tests_passed
        tests_run += 1
        Sat.validate(instance)
        expected = sat_solve(instance)
        target = reduce(instance)
        Clique.validate(target)
        got = clique_solve(target)
        if got == expected:
            tests_passed += 1
        else:
            failures.append((instance, expected, target, got))

    for inst in exhaustive_instances():
        check(inst)
    for inst in edge_case_instances():
        check(inst)
    for inst in random_instances(4000):
        check(inst)

    print(f"tests_run={tests_run} tests_passed={tests_passed}")
    if failures:
        print("FAILURES:")
        for inst, expected, target, got in failures[:10]:
            print("  source:", inst)
            print("  expected:", expected, "target:", target, "got:", got)
    return 0 if not failures else 1


if __name__ == "__main__":
    raise SystemExit(main())
