"""Independent tests for reduce.py (Dominating Set -> SAT).

Contains brute-force solvers written from the problem definitions in
problems.py, plus tests comparing solver answers on small source instances
with the answers on their reductions.
"""

import itertools
import random
import time

from problems import DominatingSet, Sat
from reduce import reduce


# ----------------------------------------------------------------------
# Brute-force solvers (written independently from the definitions)

def brute_dominating(instance):
    """Return True iff the graph has a dominating set of size <= k."""
    n = instance["n"]
    edges = instance["edges"]
    k = instance["k"]
    if k < 0:
        return False
    if n == 0:
        return True
    adj = [set() for _ in range(n)]
    for u, v in edges:
        adj[u].add(v)
        adj[v].add(u)
    for size in range(0, min(k, n) + 1):
        for subset in itertools.combinations(range(n), size):
            S = set(subset)
            if all(v in S or (adj[v] & S) for v in range(n)):
                return True
    return False


def brute_sat(instance):
    """Return True iff some assignment satisfies every clause."""
    m = instance["num_vars"]
    clauses = instance["clauses"]
    for clause in clauses:
        if len(clause) == 0:
            return False
    for bits in itertools.product([False, True], repeat=m):
        ok = True
        for clause in clauses:
            sat = False
            for lit in clause:
                val = bits[abs(lit) - 1]
                if lit < 0:
                    val = not val
                if val:
                    sat = True
                    break
            if not sat:
                ok = False
                break
        if ok:
            return True
    return False


# ----------------------------------------------------------------------
# Instance generators

def all_graphs(n):
    """All simple graphs on n labelled vertices (as edge lists)."""
    possible = list(itertools.combinations(range(n), 2))
    for mask in range(1 << len(possible)):
        edges = [list(e) for i, e in enumerate(possible) if (mask >> i) & 1]
        yield {"n": n, "edges": edges}


def random_instance(rng, max_n=7):
    n = rng.randint(0, max_n)
    edges = []
    for u in range(n):
        for v in range(u + 1, n):
            if rng.random() < 0.4:
                edges.append([u, v])
    k = rng.randint(-2, n + 2)
    return {"n": n, "edges": edges, "k": k}


# ----------------------------------------------------------------------
# Tests

def main():
    tests_run = 0
    tests_passed = 0
    failures = []

    def check(inst, tag):
        nonlocal tests_run, tests_passed
        tests_run += 1
        try:
            DominatingSet.validate(inst)
        except Exception as exc:  # noqa: BLE001
            failures.append((tag, "source invalid", inst, repr(exc)))
            return
        red = reduce(inst)
        # reduced instance must be a valid Sat instance
        try:
            Sat.validate(red)
        except Exception as exc:  # noqa: BLE001
            failures.append((tag, "reduced invalid", inst, repr(exc)))
            return
        want = brute_dominating(inst)
        got = brute_sat(red)
        if want != got:
            failures.append((tag, "mismatch", inst, red, want, got))
            return
        tests_passed += 1

    # 1) Exhaustive: all graphs on 0..4 vertices, all k in -2..n+2
    for n in range(0, 5):
        for g in all_graphs(n):
            for k in range(-2, n + 3):
                inst = {"n": g["n"], "edges": g["edges"], "k": k}
                check(inst, f"exhaustive n={n} k={k}")

    # 2) Random small instances
    rng = random.Random(12345)
    for _ in range(3000):
        check(random_instance(rng), "random")

    # 3) Specific edge cases
    edge_cases = [
        {"n": 0, "edges": [], "k": 0},
        {"n": 0, "edges": [], "k": 5},
        {"n": 0, "edges": [], "k": -1},
        {"n": 1, "edges": [], "k": 0},
        {"n": 1, "edges": [], "k": -1},
        {"n": 3, "edges": [], "k": 2},
        {"n": 3, "edges": [], "k": 3},
        {"n": 3, "edges": [], "k": 1},
        {"n": 4, "edges": [[0, 1], [1, 2], [2, 3], [3, 0]], "k": 2},
        {"n": 4, "edges": [[0, 1], [1, 2], [2, 3], [3, 0]], "k": 1},
        {"n": 5, "edges": [[0, 1], [1, 2], [2, 3], [3, 4]], "k": 2},
    ]
    for inst in edge_cases:
        check(inst, "edge-case")

    print(f"correctness tests_run={tests_run} tests_passed={tests_passed}")
    if failures:
        print("FAILURES:")
        for f in failures[:10]:
            print("  ", f)

    # 4) Polynomial-time / output-size check (not a pass/fail correctness test)
    print("\nOutput-size growth of the cardinality encoding (n, k=floor(n/2)):")
    sizes = []
    for n in (14, 16, 18, 20):
        k = n // 2
        inst = {"n": n, "edges": [], "k": k}
        t0 = time.time()
        red = reduce(inst)
        dt = time.time() - t0
        nclauses = len(red["clauses"])
        sizes.append((n, k, nclauses, dt))
        print(f"  n={n:3d} k={k:3d}  clauses={nclauses:8d}  time={dt:.4f}s")
    # C(n, floor(n/2)) grows exponentially; show the ratio doubling-ish
    print("  clause-count ratios between consecutive n:",
          [round(sizes[i + 1][2] / sizes[i][2], 2) for i in range(len(sizes) - 1)])

    return tests_run, tests_passed, failures


if __name__ == "__main__":
    tests_run, tests_passed, failures = main()
    print(f"\nTOTAL tests_run={tests_run} tests_passed={tests_passed} failures={len(failures)}")
