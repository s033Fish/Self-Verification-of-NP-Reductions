"""Brute-force solvers and tests comparing Hamiltonian Path with its reduction."""

from __future__ import annotations

import itertools
import random

from problems import HamiltonianPath, HamiltonianCycle
from reduce import reduce


# ---------------------------------------------------------------------------
# Brute-force solvers written from the definitions in problems.py

def ham_path_bruteforce(instance) -> bool:
    n = instance["n"]
    edges = instance["edges"]
    if n == 0:
        return False
    if n == 1:
        return True
    adj = [set() for _ in range(n)]
    for u, v in edges:
        adj[u].add(v)
        adj[v].add(u)

    def dfs(v, visited):
        if len(visited) == n:
            return True
        for w in adj[v]:
            if w not in visited:
                visited.add(w)
                if dfs(w, visited):
                    return True
                visited.remove(w)
        return False

    for start in range(n):
        if dfs(start, {start}):
            return True
    return False


def ham_cycle_bruteforce(instance) -> bool:
    n = instance["n"]
    edges = instance["edges"]
    if n <= 2:
        return False
    adj = [set() for _ in range(n)]
    for u, v in edges:
        adj[u].add(v)
        adj[v].add(u)
    # Fix vertex 0 first to cut permutations by symmetry.
    for perm in itertools.permutations(range(1, n)):
        order = (0,) + perm
        ok = True
        for i in range(n):
            if order[(i + 1) % n] not in adj[order[i]]:
                ok = False
                break
        if ok:
            return True
    return False


# ---------------------------------------------------------------------------
# Tests

def all_graphs(n):
    possible = [(u, v) for u in range(n) for v in range(u + 1, n)]
    for mask in range(1 << len(possible)):
        edges = [list(possible[i]) for i in range(len(possible)) if mask >> i & 1]
        yield {"n": n, "edges": edges}


def check(instance, results):
    src = ham_path_bruteforce(instance)
    red = reduce(instance)
    # Both instances must be valid according to problems.py.
    HamiltonianPath.validate(instance)
    HamiltonianCycle.validate(red)
    tgt = ham_cycle_bruteforce(red)
    results["tests_run"] += 1
    if src == tgt:
        results["tests_passed"] += 1
    else:
        results["failures"].append((instance, red, src, tgt))


def main():
    results = {"tests_run": 0, "tests_passed": 0, "failures": []}

    # Exhaustive over all graphs with n = 0..5.
    for n in range(0, 6):
        for instance in all_graphs(n):
            check(instance, results)

    # Random larger graphs.
    rng = random.Random(12345)
    for _ in range(2000):
        n = rng.randint(6, 8)
        possible = [(u, v) for u in range(n) for v in range(u + 1, n)]
        edges = [list(e) for e in possible if rng.random() < rng.choice([0.2, 0.4, 0.6, 0.8])]
        check({"n": n, "edges": edges}, results)

    # Hand-picked edge cases.
    for instance in [
        {"n": 0, "edges": []},
        {"n": 1, "edges": []},
        {"n": 2, "edges": []},
        {"n": 2, "edges": [[0, 1]]},
        {"n": 3, "edges": [[0, 1], [1, 2]]},
        {"n": 3, "edges": [[0, 1], [1, 2], [0, 2]]},
    ]:
        check(instance, results)

    print(f"tests_run={results['tests_run']} tests_passed={results['tests_passed']}")
    for failure in results["failures"][:5]:
        print("FAILURE:", failure)
    assert not results["failures"], "some tests failed"

    import json
    with open("verdict.json", "w") as fh:
        json.dump(
            {
                "verified": results["tests_run"] == results["tests_passed"],
                "tests_run": results["tests_run"],
                "tests_passed": results["tests_passed"],
            },
            fh,
        )
    print("wrote verdict.json")


if __name__ == "__main__":
    main()
