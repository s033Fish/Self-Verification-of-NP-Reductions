"""Brute-force solvers and tests comparing SAT answers with their reductions."""

import itertools
import random

import problems
from reduce import reduce


def sat_solve(instance):
    """Brute force SAT over all assignments of variables 1..num_vars."""
    m = instance["num_vars"]
    clauses = instance["clauses"]
    for bits in itertools.product([False, True], repeat=m):
        # bits[v-1] is value of variable v
        ok = True
        for clause in clauses:
            if not any(
                (bits[abs(lit) - 1] if lit > 0 else not bits[abs(lit) - 1])
                for lit in clause
            ):
                ok = False
                break
        if ok:
            return True
    return False


def clique_solve(instance):
    """Brute force Clique: is there a clique of size >= k?"""
    n = instance["n"]
    k = instance["k"]
    if k <= 0:
        return True
    if k > n:
        return False
    adj = [[False] * n for _ in range(n)]
    for u, v in instance["edges"]:
        adj[u][v] = True
        adj[v][u] = True
    for size in range(k, n + 1):
        for subset in itertools.combinations(range(n), size):
            if all(adj[u][v] for u, v in itertools.combinations(subset, 2)):
                return True
    return False


def random_sat_instance(rng, max_vars=4, max_clauses=5, max_len=3):
    m = rng.randint(0, max_vars)
    num_clauses = rng.randint(0, max_clauses)
    clauses = []
    for _ in range(num_clauses):
        length = rng.randint(0, max_len)
        clause = []
        for _ in range(length):
            v = rng.randint(1, m) if m > 0 else 1
            if m == 0:
                # no variables: only empty clauses are valid
                break
            clause.append(v if rng.random() < 0.5 else -v)
        clauses.append(clause)
    return {"num_vars": m, "clauses": clauses}


def main():
    rng = random.Random(12345)
    tests_run = 0
    tests_passed = 0

    # Deterministic edge cases
    fixed = [
        {"num_vars": 0, "clauses": []},
        {"num_vars": 0, "clauses": [[]]},
        {"num_vars": 1, "clauses": []},
        {"num_vars": 1, "clauses": [[1]]},
        {"num_vars": 1, "clauses": [[-1]]},
        {"num_vars": 1, "clauses": [[1], [-1]]},
        {"num_vars": 2, "clauses": [[1, 2], [-1, -2]]},
        {"num_vars": 2, "clauses": [[1, 2], [-1, -2], [1, -2]]},
        {"num_vars": 3, "clauses": [[1, 1, 2], [-1, -1, 3], [-2, -3]]},
        {"num_vars": 2, "clauses": [[1, -1], [2, -2]]},
        {"num_vars": 3, "clauses": [[1], [2], [3], [-1, -2, -3]]},
    ]
    cases = list(fixed)
    for _ in range(2000):
        cases.append(random_sat_instance(rng))

    for inst in cases:
        problems.Sat.validate(inst)
        red = reduce(inst)
        problems.Clique.validate(red)
        expected = sat_solve(inst)
        got = clique_solve(red)
        tests_run += 1
        if expected == got:
            tests_passed += 1
        else:
            print("MISMATCH", inst, "->", red, "expected", expected, "got", got)

    print(f"tests_run={tests_run} tests_passed={tests_passed}")
    assert tests_run == tests_passed, "some tests failed"
    return tests_run, tests_passed


if __name__ == "__main__":
    main()
