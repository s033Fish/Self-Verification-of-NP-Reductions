"""Independent verification of reduce.py for HamiltonianPath -> HamiltonianCycle.

We implement brute-force solvers directly from the problem definitions in
problems.py (which provides only validate()), enumerate all small source
instances, apply reduce(), and compare the answers.
"""

from __future__ import annotations

import itertools
import json

from problems import HamiltonianPath, HamiltonianCycle, InvalidInstance
from reduce import reduce


# ----------------------------------------------------------------------
# Brute-force solvers written from the docstrings.

def ham_path(n: int, edges: list[list[int]]) -> bool:
    """True iff the undirected graph has a Hamiltonian path (any endpoints)."""
    if n == 0:
        return False
    if n == 1:
        return True
    adj = [[False] * n for _ in range(n)]
    for u, v in edges:
        adj[u][v] = adj[v][u] = True
    # Try every ordering of all n vertices as a candidate path.
    for perm in itertools.permutations(range(n)):
        if all(adj[perm[i]][perm[i + 1]] for i in range(n - 1)):
            return True
    return False


def ham_cycle(n: int, edges: list[list[int]]) -> bool:
    """True iff the undirected graph has a Hamiltonian cycle."""
    if n <= 2:
        return False
    adj = [[False] * n for _ in range(n)]
    for u, v in edges:
        adj[u][v] = adj[v][u] = True
    # Fix vertex 0 first to avoid counting rotations; try all orderings of
    # the remaining vertices and require the closing edge back to 0.
    rest = list(range(1, n))
    for perm in itertools.permutations(rest):
        cyc = (0,) + perm
        if all(adj[cyc[i]][cyc[i + 1]] for i in range(n - 1)) and adj[cyc[-1]][0]:
            return True
    return False


# ----------------------------------------------------------------------
# Instance generation: every simple graph on n vertices.

def all_graphs(n: int):
    pairs = [(u, v) for u in range(n) for v in range(u + 1, n)]
    for mask in range(1 << len(pairs)):
        edges = [list(pairs[i]) for i in range(len(pairs)) if mask >> i & 1]
        yield {"n": n, "edges": edges}


def main() -> int:
    tests_run = 0
    tests_passed = 0
    failures = []

    max_n = 5
    for n in range(0, max_n + 1):
        for instance in all_graphs(n):
            # Source instance must be valid.
            HamiltonianPath.validate(instance)
            src = ham_path(instance["n"], instance["edges"])

            target = reduce(instance)

            # The reduction output must be a valid target instance.
            try:
                HamiltonianCycle.validate(target)
                valid = True
            except InvalidInstance as exc:
                valid = False
                failures.append((instance, target, f"invalid target: {exc}"))

            if valid:
                tgt = ham_cycle(target["n"], target["edges"])
                tests_run += 1
                if src == tgt:
                    tests_passed += 1
                else:
                    failures.append((instance, target, f"src={src} tgt={tgt}"))

    # A few extra structured cases (paths, cycles, stars, complete graphs).
    extra = []
    for n in range(1, 8):
        extra.append({"n": n, "edges": [[i, i + 1] for i in range(n - 1)]})
        extra.append({"n": n, "edges": [[i, (i + 1) % n] for i in range(n)] if n >= 3 else []})
        extra.append({"n": n, "edges": [[0, v] for v in range(1, n)]})
        extra.append({"n": n, "edges": [[u, v] for u in range(n) for v in range(u + 1, n)]})
    for instance in extra:
        HamiltonianPath.validate(instance)
        src = ham_path(instance["n"], instance["edges"])
        target = reduce(instance)
        HamiltonianCycle.validate(target)
        tgt = ham_cycle(target["n"], target["edges"])
        tests_run += 1
        if src == tgt:
            tests_passed += 1
        else:
            failures.append((instance, target, f"src={src} tgt={tgt}"))

    print(f"tests_run={tests_run} tests_passed={tests_passed}")
    if failures:
        print("FAILURES:")
        for f in failures[:20]:
            print(f)
    else:
        print("All tests passed.")

    with open("verdict.json", "w") as fh:
        json.dump(
            {
                "verified": len(failures) == 0,
                "tests_run": tests_run,
                "tests_passed": tests_passed,
            },
            fh,
        )
    return 0 if not failures else 1


if __name__ == "__main__":
    raise SystemExit(main())
