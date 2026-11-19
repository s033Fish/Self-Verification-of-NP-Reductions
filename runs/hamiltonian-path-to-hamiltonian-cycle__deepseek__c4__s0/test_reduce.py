"""Brute-force solvers and tests comparing Hamiltonian Path answers with the
answers of their reductions to Hamiltonian Cycle."""

from __future__ import annotations

import itertools

from problems import SOURCE, TARGET
from reduce import reduce


# ----------------------------------------------------------------------
# Brute-force solvers written directly from the problem definitions.

def _adj(n, edges):
    adj = [set() for _ in range(n)]
    for u, v in edges:
        adj[u].add(v)
        adj[v].add(u)
    return adj


def solve_hamiltonian_path(instance):
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
    n = instance["n"]
    edges = instance["edges"]
    if n <= 2:
        return False
    adj = _adj(n, edges)
    start = 0
    rest = list(range(1, n))
    for perm in itertools.permutations(rest):
        order = (start,) + perm
        if all(order[i + 1] in adj[order[i]] for i in range(n - 1)) and order[-1] in adj[start]:
            return True
    return False


# ----------------------------------------------------------------------
# Instance generation: all graphs on n vertices.

def all_graphs(n):
    pairs = list(itertools.combinations(range(n), 2))
    for mask in range(1 << len(pairs)):
        edges = [list(pairs[i]) for i in range(len(pairs)) if mask >> i & 1]
        yield {"n": n, "edges": edges}


def main():
    tests_run = 0
    tests_passed = 0

    # Exhaustive check over all graphs for small n.
    for n in range(0, 7):
        for instance in all_graphs(n):
            SOURCE.validate(instance)
            reduced = reduce(instance)
            TARGET.validate(reduced)

            src = solve_hamiltonian_path(instance)
            tgt = solve_hamiltonian_cycle(reduced)
            tests_run += 1
            if src == tgt:
                tests_passed += 1
            else:
                print("MISMATCH", instance, "->", reduced, "src", src, "tgt", tgt)

    # A few hand-picked edge cases.
    edge_cases = [
        {"n": 0, "edges": []},
        {"n": 1, "edges": []},
        {"n": 2, "edges": []},
        {"n": 2, "edges": [[0, 1]]},
        {"n": 3, "edges": [[0, 1], [1, 2], [0, 2]]},
        {"n": 3, "edges": [[0, 1], [1, 2]]},
        {"n": 4, "edges": [[0, 1], [1, 2], [2, 3]]},
        {"n": 4, "edges": [[0, 1], [1, 2], [2, 3], [3, 0]]},
    ]
    for instance in edge_cases:
        SOURCE.validate(instance)
        reduced = reduce(instance)
        TARGET.validate(reduced)
        src = solve_hamiltonian_path(instance)
        tgt = solve_hamiltonian_cycle(reduced)
        tests_run += 1
        if src == tgt:
            tests_passed += 1
        else:
            print("MISMATCH", instance, "->", reduced, "src", src, "tgt", tgt)

    print(f"tests_run={tests_run} tests_passed={tests_passed}")
    assert tests_run == tests_passed, "some tests failed"
    return tests_run, tests_passed


if __name__ == "__main__":
    main()


def random_tests():
    import random
    rng = random.Random(12345)
    tests_run = 0
    tests_passed = 0
    for _ in range(3000):
        n = rng.randint(0, 8)
        pairs = list(itertools.combinations(range(n), 2))
        edges = [list(p) for p in pairs if rng.random() < 0.4]
        instance = {"n": n, "edges": edges}
        SOURCE.validate(instance)
        reduced = reduce(instance)
        TARGET.validate(reduced)
        src = solve_hamiltonian_path(instance)
        tgt = solve_hamiltonian_cycle(reduced)
        tests_run += 1
        if src == tgt:
            tests_passed += 1
        else:
            print("MISMATCH", instance, "->", reduced, "src", src, "tgt", tgt)
    print(f"random tests_run={tests_run} tests_passed={tests_passed}")
    return tests_run, tests_passed
