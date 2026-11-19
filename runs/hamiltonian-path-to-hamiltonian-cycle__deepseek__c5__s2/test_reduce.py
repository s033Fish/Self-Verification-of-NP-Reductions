"""Independent brute-force solvers and tests for reduce.py.

SOURCE = HamiltonianPath, TARGET = HamiltonianCycle (undirected simple graphs).

The solvers below are written directly from the problem definitions in
problems.py (no solvers are provided there).  The tests compare the source
answer with the answer to reduce(instance) on:
  * every simple graph on 0..6 vertices (exhaustive),
  * the documented edge cases,
  * many random graphs on up to 9 vertices,
  * a polynomial-output-size sanity check.
"""

from __future__ import annotations

import itertools
import random
import sys

from problems import HamiltonianPath, HamiltonianCycle
from reduce import reduce


# ----------------------------------------------------------------------
# Brute-force solvers written directly from the problem definitions.
# ----------------------------------------------------------------------

def _adj(n, edges):
    adj = [set() for _ in range(n)]
    for u, v in edges:
        adj[u].add(v)
        adj[v].add(u)
    return adj


def solve_hamiltonian_path(instance):
    """Return True iff the graph has a Hamiltonian path (any endpoints)."""
    n = instance["n"]
    edges = instance["edges"]
    if n == 0:
        return False
    if n == 1:
        return True
    adj = _adj(n, edges)
    for perm in itertools.permutations(range(n)):
        if all(perm[i + 1] in adj[perm[i]] for i in range(n - 1)):
            return True
    return False


def solve_hamiltonian_cycle(instance):
    """Return True iff the graph has a Hamiltonian cycle."""
    n = instance["n"]
    edges = instance["edges"]
    if n <= 2:
        return False
    adj = _adj(n, edges)
    for perm in itertools.permutations(range(1, n)):
        cycle = (0,) + perm
        if all(cycle[(i + 1) % n] in adj[cycle[i]] for i in range(n)):
            return True
    return False


# ----------------------------------------------------------------------
# Test harness
# ----------------------------------------------------------------------

def all_graphs(n):
    """Yield every simple undirected graph on vertices 0..n-1."""
    pairs = list(itertools.combinations(range(n), 2))
    m = len(pairs)
    for mask in range(1 << m):
        edges = [list(pairs[i]) for i in range(m) if (mask >> i) & 1]
        yield {"n": n, "edges": edges}


def check(inst, failures):
    """Validate + solve source, reduce, validate + solve target; compare."""
    HamiltonianPath.validate(inst)
    source_ans = solve_hamiltonian_path(inst)
    red = reduce(inst)
    HamiltonianCycle.validate(red)
    target_ans = solve_hamiltonian_cycle(red)
    if source_ans != target_ans:
        failures.append((inst, source_ans, red, target_ans))
    return source_ans == target_ans


def main():
    tests_run = 0
    tests_passed = 0
    failures = []

    max_n = int(sys.argv[1]) if len(sys.argv) > 1 else 6

    # 1. Exhaustive over all graphs on 0..max_n vertices.
    for n in range(0, max_n + 1):
        for inst in all_graphs(n):
            tests_run += 1
            if check(inst, failures):
                tests_passed += 1

    # 2. Documented edge cases.
    edge_cases = [
        {"n": 0, "edges": []},
        {"n": 1, "edges": []},
        {"n": 2, "edges": []},
        {"n": 2, "edges": [[0, 1]]},
        {"n": 3, "edges": [[0, 1], [1, 2]]},
        {"n": 3, "edges": [[0, 1], [1, 2], [0, 2]]},
    ]
    for inst in edge_cases:
        tests_run += 1
        if check(inst, failures):
            tests_passed += 1

    # 3. Random graphs on up to 9 vertices (brute force is factorial).
    random.seed(12345)
    for _ in range(400):
        n = random.randint(0, 9)
        pairs = list(itertools.combinations(range(n), 2))
        p = random.choice([0.2, 0.4, 0.6, 0.8])
        edges = [list(pr) for pr in pairs if random.random() < p]
        inst = {"n": n, "edges": edges}
        tests_run += 1
        if check(inst, failures):
            tests_passed += 1

    # 4. Polynomial-output-size sanity check (output linear in input size).
    for n in (10, 100, 1000):
        inst = {"n": n, "edges": [[i, i + 1] for i in range(n - 1)]}
        red = reduce(inst)
        HamiltonianCycle.validate(red)
        tests_run += 1
        if red["n"] == n + 1 and len(red["edges"]) == (n - 1) + n:
            tests_passed += 1
        else:
            failures.append((inst, "size", red, None))

    print(f"tests_run={tests_run} tests_passed={tests_passed}")
    if failures:
        print(f"FAILURES: {len(failures)}")
        for f in failures[:20]:
            print("  ", f)
    else:
        print("ALL TESTS PASSED")

    return tests_run, tests_passed, failures


if __name__ == "__main__":
    main()
