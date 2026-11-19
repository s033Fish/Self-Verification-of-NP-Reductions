"""Brute-force solvers + randomized/exhaustive tests for reduce.py."""

import itertools
import random

from problems import HamiltonianPath, Sat
from reduce import reduce


# ----------------------------------------------------------------------
# Brute-force solvers written directly from the problem definitions.

def hp_solve(instance):
    n = instance["n"]
    edges = instance["edges"]
    if n == 0:
        return False
    adj = [[False] * n for _ in range(n)]
    for u, v in edges:
        adj[u][v] = True
        adj[v][u] = True
    for perm in itertools.permutations(range(n)):
        if all(adj[perm[i]][perm[i + 1]] for i in range(n - 1)):
            return True
    return False


def sat_solve(instance):
    """DPLL with unit propagation (exact, from the SAT definition)."""
    m = instance["num_vars"]
    clauses = [frozenset(c) for c in instance["clauses"]]

    def dpll(clauses):
        # unit propagation
        while True:
            unit = None
            for c in clauses:
                if len(c) == 1:
                    unit = next(iter(c))
                    break
            if unit is None:
                break
            new = []
            for c in clauses:
                if unit in c:
                    continue
                if -unit in c:
                    c2 = c - {-unit}
                    if not c2:
                        return False
                    new.append(c2)
                else:
                    new.append(c)
            clauses = new
        if not clauses:
            return True
        if any(len(c) == 0 for c in clauses):
            return False
        # branch on a literal of the first clause
        lit = next(iter(clauses[0]))
        for val in (lit, -lit):
            new = []
            ok = True
            for c in clauses:
                if val in c:
                    continue
                if -val in c:
                    c2 = c - {-val}
                    if not c2:
                        ok = False
                        break
                    new.append(c2)
                else:
                    new.append(c)
            if ok and dpll(new):
                return True
        return False

    return dpll(clauses)


# ----------------------------------------------------------------------
# Instance generators.

def all_graphs(n):
    pairs = [(u, v) for u in range(n) for v in range(u + 1, n)]
    for mask in range(1 << len(pairs)):
        edges = [list(pairs[i]) for i in range(len(pairs)) if (mask >> i) & 1]
        yield {"n": n, "edges": edges}


def random_graph(rng, n):
    pairs = [(u, v) for u in range(n) for v in range(u + 1, n)]
    edges = [list(p) for p in pairs if rng.random() < 0.5]
    return {"n": n, "edges": edges}


def main():
    tests_run = 0
    tests_passed = 0
    failures = []

    def check(inst, tag):
        nonlocal tests_run, tests_passed
        tests_run += 1
        try:
            HamiltonianPath.validate(inst)
            out = reduce(inst)
            Sat.validate(out)
            a = hp_solve(inst)
            b = sat_solve(out)
            if a != b:
                failures.append((tag, inst, out, a, b))
            else:
                tests_passed += 1
        except Exception as exc:  # noqa: BLE001
            failures.append((tag, inst, repr(exc), None, None))

    # Exhaustive over all graphs with n = 0..4 (n=4 -> 64 graphs).
    for n in range(0, 5):
        for g in all_graphs(n):
            check(g, f"exhaustive n={n}")

    # Random graphs with n = 5..7.
    rng = random.Random(12345)
    for n, count in ((5, 120), (6, 80), (7, 50)):
        for _ in range(count):
            check(random_graph(rng, n), f"random n={n}")

    # A few structured cases.
    check({"n": 1, "edges": []}, "n=1")
    check({"n": 2, "edges": []}, "n=2 no edge")
    check({"n": 2, "edges": [[0, 1]]}, "n=2 edge")
    check({"n": 5, "edges": [[i, i + 1] for i in range(4)]}, "path n=5")
    check({"n": 6, "edges": [[i, (i + 1) % 6] for i in range(6)]}, "cycle n=6")
    check({"n": 5, "edges": []}, "empty n=5")

    print(f"tests_run={tests_run} tests_passed={tests_passed}")
    if failures:
        print("FAILURES:")
        for f in failures[:10]:
            print(f)
        return 1
    print("ALL TESTS PASSED")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
