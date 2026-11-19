"""Independent verification of reduce.py.

We implement brute-force solvers for Hamiltonian Path and Hamiltonian
Cycle directly from the definitions in problems.py, then exhaustively
compare source answers with the answers of their reductions on all
small graphs.
"""

from itertools import combinations, permutations

from problems import HamiltonianPath, HamiltonianCycle
from reduce import reduce


# ----------------------------------------------------------------------
# Brute-force solvers (written from the problem definitions).

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
    # Try every starting vertex, DFS over simple paths.
    for start in range(n):
        stack = [(start, 1 << start)]
        while stack:
            v, visited = stack.pop()
            if bin(visited).count("1") == n:
                return True
            for w in adj[v]:
                if not (visited >> w) & 1:
                    stack.append((w, visited | (1 << w)))
    return False


def solve_hamiltonian_cycle(instance):
    """Return True iff the graph has a Hamiltonian cycle."""
    n = instance["n"]
    edges = instance["edges"]
    if n <= 2:
        return False
    adj = _adj(n, edges)
    start = 0
    stack = [(start, 1 << start)]
    while stack:
        v, visited = stack.pop()
        if bin(visited).count("1") == n:
            if start in adj[v]:
                return True
            continue
        for w in adj[v]:
            if not (visited >> w) & 1:
                stack.append((w, visited | (1 << w)))
    return False


# ----------------------------------------------------------------------
# Instance enumeration.

def all_graphs(n):
    """Yield every undirected simple graph on n labelled vertices."""
    possible = list(combinations(range(n), 2))
    for mask in range(1 << len(possible)):
        edges = [list(possible[i]) for i in range(len(possible)) if (mask >> i) & 1]
        yield {"n": n, "edges": edges}


def main():
    tests_run = 0
    tests_passed = 0
    failures = []

    max_n = 6
    for n in range(0, max_n + 1):
        for inst in all_graphs(n):
            tests_run += 1
            HamiltonianPath.validate(inst)
            src = solve_hamiltonian_path(inst)
            out = reduce(inst)
            # The reduction must produce a valid target instance.
            HamiltonianCycle.validate(out)
            tgt = solve_hamiltonian_cycle(out)
            if src == tgt:
                tests_passed += 1
            else:
                failures.append((inst, src, out, tgt))

    # Also test some larger random-ish structured graphs for sanity.
    import random
    random.seed(12345)
    for _ in range(3000):
        n = random.randint(0, 9)
        possible = list(combinations(range(n), 2))
        edges = [list(e) for e in possible if random.random() < 0.4]
        inst = {"n": n, "edges": edges}
        tests_run += 1
        HamiltonianPath.validate(inst)
        src = solve_hamiltonian_path(inst)
        out = reduce(inst)
        HamiltonianCycle.validate(out)
        tgt = solve_hamiltonian_cycle(out)
        if src == tgt:
            tests_passed += 1
        else:
            failures.append((inst, src, out, tgt))

    print(f"tests_run={tests_run} tests_passed={tests_passed}")
    if failures:
        print("FAILURES:")
        for f in failures[:10]:
            print(f)
    else:
        print("All reductions matched the source answers.")

    return tests_run, tests_passed, len(failures)


if __name__ == "__main__":
    main()
