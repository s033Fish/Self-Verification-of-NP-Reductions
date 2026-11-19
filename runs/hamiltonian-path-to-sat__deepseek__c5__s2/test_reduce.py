"""Independent tests for reduce.py (Hamiltonian Path -> SAT).

We write our own solvers from the problem definitions and compare their
answers on many small source instances against the answers of the reduced
SAT instances.
"""

import itertools
import random

from problems import SOURCE, TARGET
from reduce import reduce


# ----------------------------------------------------------------------
# Brute-force solver for Hamiltonian Path (SOURCE)
# ----------------------------------------------------------------------

def ham_path_solver(instance):
    n = instance["n"]
    edges = instance["edges"]
    if n == 0:
        return False
    if n == 1:
        return True
    adj = [[False] * n for _ in range(n)]
    for u, v in edges:
        adj[u][v] = True
        adj[v][u] = True
    # try every permutation as the order of vertices on the path
    for perm in itertools.permutations(range(n)):
        if all(adj[perm[i]][perm[i + 1]] for i in range(n - 1)):
            return True
    return False


# ----------------------------------------------------------------------
# Exact backtracking solver for SAT (TARGET)
# ----------------------------------------------------------------------

def sat_solver(instance):
    m = instance["num_vars"]
    clauses = instance["clauses"]
    # An empty clause is unsatisfiable.
    if any(len(c) == 0 for c in clauses):
        return False
    assignment = {}  # var -> bool

    def clause_falsified(clause):
        # True iff every literal in the clause is currently false.
        for lit in clause:
            var = abs(lit)
            if var not in assignment:
                return False
            val = assignment[var]
            if (lit > 0 and val) or (lit < 0 and not val):
                return False
        return True

    def rec(var):
        if var > m:
            return True
        for val in (True, False):
            assignment[var] = val
            if not any(clause_falsified(c) for c in clauses):
                if rec(var + 1):
                    return True
            del assignment[var]
        return False

    return rec(1)


# ----------------------------------------------------------------------
# Instance generation
# ----------------------------------------------------------------------

def all_graphs(n):
    pairs = list(itertools.combinations(range(n), 2))
    for mask in range(1 << len(pairs)):
        edges = [list(pairs[i]) for i in range(len(pairs)) if (mask >> i) & 1]
        yield {"n": n, "edges": edges}


def random_graph(n, p, rng):
    edges = []
    for u, v in itertools.combinations(range(n), 2):
        if rng.random() < p:
            edges.append([u, v])
    return {"n": n, "edges": edges}


def main():
    rng = random.Random(12345)
    tests_run = 0
    tests_passed = 0
    failures = []

    def check(instance):
        nonlocal tests_run, tests_passed
        tests_run += 1
        # source must be valid
        SOURCE.validate(instance)
        expected = ham_path_solver(instance)
        reduced = reduce(instance)
        # target must be valid
        TARGET.validate(reduced)
        got = sat_solver(reduced)
        if got == expected:
            tests_passed += 1
        else:
            failures.append((instance, expected, reduced, got))

    # Exhaustive over all graphs for n = 0..4
    for n in range(0, 5):
        for g in all_graphs(n):
            check(g)

    # Random graphs for larger n
    for n in range(5, 9):
        for _ in range(60):
            check(random_graph(n, rng.choice([0.15, 0.3, 0.5, 0.8]), rng))

    # Some structured cases: complete graphs, empty graphs, paths, cycles
    for n in range(0, 9):
        check({"n": n, "edges": []})
        check({"n": n, "edges": [[u, v] for u, v in itertools.combinations(range(n), 2)]})
        check({"n": n, "edges": [[i, i + 1] for i in range(n - 1)]})
        if n >= 3:
            check({"n": n, "edges": [[i, (i + 1) % n] for i in range(n)]})

    print(f"tests_run={tests_run} tests_passed={tests_passed}")
    if failures:
        print(f"FAILURES: {len(failures)}")
        for inst, exp, red, got in failures[:5]:
            print("  instance:", inst)
            print("  expected:", exp, "got:", got)
            print("  reduced:", red)
    return tests_run, tests_passed, failures


if __name__ == "__main__":
    main()
