"""Independent verification of reduce.py (SAT -> Independent Set).

We implement our own brute-force solvers directly from the definitions in
problems.py and compare them against the reduction on many small instances,
including exhaustive enumeration of all small formulas.
"""

import itertools
import random

from problems import Sat, IndependentSet
from reduce import reduce


# ----------------------------------------------------------------------
# Brute-force solvers (written from the problem definitions)

def sat_solve(instance):
    """Return True iff the CNF formula is satisfiable (brute force)."""
    Sat.validate(instance)
    m = instance["num_vars"]
    clauses = instance["clauses"]
    for bits in itertools.product([False, True], repeat=m):
        # variable v (1..m) -> bits[v-1]
        ok = True
        for clause in clauses:
            if not any((bits[abs(lit) - 1] if lit > 0 else not bits[abs(lit) - 1])
                       for lit in clause):
                ok = False
                break
        if ok:
            return True
    return False


def is_solve(instance):
    """Return True iff the graph has an independent set of size >= k."""
    IndependentSet.validate(instance)
    n = instance["n"]
    edges = instance["edges"]
    k = instance["k"]
    if k <= 0:
        return True
    if k > n:
        return False
    adj = [set() for _ in range(n)]
    for u, v in edges:
        adj[u].add(v)
        adj[v].add(u)
    for size in range(k, n + 1):
        for subset in itertools.combinations(range(n), size):
            s = set(subset)
            if all(not (adj[u] & s) for u in s):
                return True
    return False


# ----------------------------------------------------------------------
# Test generation

def all_sat_instances(max_vars, max_clauses, max_clause_len):
    """Yield a broad family of small SAT instances."""
    for m in range(0, max_vars + 1):
        literals = [l for v in range(1, m + 1) for l in (v, -v)]
        # all possible clauses up to max_clause_len
        possible = []
        for length in range(0, max_clause_len + 1):
            possible.extend(itertools.combinations_with_replacement(literals, length))
        for num_clauses in range(0, max_clauses + 1):
            for clauses in itertools.combinations_with_replacement(possible, num_clauses):
                yield {"num_vars": m, "clauses": [list(c) for c in clauses]}


def random_sat_instance(rng, max_vars=4, max_clauses=5, max_clause_len=4):
    m = rng.randint(0, max_vars)
    literals = [l for v in range(1, m + 1) for l in (v, -v)]
    nclauses = rng.randint(0, max_clauses)
    clauses = []
    for _ in range(nclauses):
        length = rng.randint(0, max_clause_len)
        clauses.append([rng.choice(literals) for _ in range(length)] if literals else [])
    return {"num_vars": m, "clauses": clauses}


# ----------------------------------------------------------------------
# Runner

def main():
    tests_run = 0
    tests_passed = 0
    failures = []

    def check(inst):
        nonlocal tests_run, tests_passed
        tests_run += 1
        expected = sat_solve(inst)
        red = reduce(inst)
        IndependentSet.validate(red)
        got = is_solve(red)
        if got == expected:
            tests_passed += 1
        else:
            failures.append((inst, red, expected, got))

    # Exhaustive small enumeration
    for inst in all_sat_instances(max_vars=3, max_clauses=3, max_clause_len=3):
        check(inst)

    # Random instances
    rng = random.Random(12345)
    for _ in range(4000):
        check(random_sat_instance(rng))

    # Targeted edge cases
    edge_cases = [
        {"num_vars": 0, "clauses": []},
        {"num_vars": 0, "clauses": [[]]},
        {"num_vars": 1, "clauses": []},
        {"num_vars": 1, "clauses": [[]]},
        {"num_vars": 1, "clauses": [[1]]},
        {"num_vars": 1, "clauses": [[-1]]},
        {"num_vars": 1, "clauses": [[1], [-1]]},
        {"num_vars": 1, "clauses": [[1, -1]]},
        {"num_vars": 1, "clauses": [[1, 1]]},
        {"num_vars": 2, "clauses": [[1, 2], [-1, -2]]},
        {"num_vars": 2, "clauses": [[1], [-1], [2], [-2]]},
        {"num_vars": 3, "clauses": [[1, 2, 3], [-1, -2, -3], [1, -2]]},
        {"num_vars": 3, "clauses": [[1, 2], [2, 3], [-1], [-3]]},
    ]
    for inst in edge_cases:
        check(inst)

    print(f"tests_run={tests_run} tests_passed={tests_passed}")
    if failures:
        print(f"FAILURES: {len(failures)}")
        for inst, red, expected, got in failures[:10]:
            print("  inst:", inst)
            print("  red :", red)
            print(f"  expected={expected} got={got}")
    else:
        print("All tests passed.")

    return tests_run, tests_passed, len(failures)


if __name__ == "__main__":
    main()
