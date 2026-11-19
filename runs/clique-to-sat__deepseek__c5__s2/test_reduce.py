"""Independent tests for reduce.py: Clique -> SAT.

problems.py provides only validate(); it has no solvers.  We therefore write
our own brute-force solvers for both problems from the definitions, then
compare the answer of many small source instances with the answer of their
reduction.  A small DPLL solver is also included so that reductions with more
variables than plain brute force can handle are still checked.
"""

from __future__ import annotations

import itertools
import random

import problems
import reduce as reduce_mod


# ----------------------------------------------------------------------
# Brute-force solvers (written from the docstrings, independent of reduce.py)
# ----------------------------------------------------------------------

def clique_bruteforce(instance: dict) -> bool:
    """Yes iff the graph has a clique of AT LEAST k vertices."""
    n = instance["n"]
    edges = instance["edges"]
    k = instance["k"]

    if k <= 0:
        return True
    if k > n:
        return False

    adj = [[False] * n for _ in range(n)]
    for u, v in edges:
        adj[u][v] = True
        adj[v][u] = True

    for size in range(k, n + 1):
        for subset in itertools.combinations(range(n), size):
            if all(adj[a][b] for a, b in itertools.combinations(subset, 2)):
                return True
    return False


def sat_bruteforce(instance: dict) -> bool:
    """Yes iff some assignment satisfies every clause."""
    m = instance["num_vars"]
    clauses = instance["clauses"]

    for bits in itertools.product([False, True], repeat=m):
        satisfied = True
        for clause in clauses:
            if not any(
                (lit > 0 and bits[lit - 1]) or (lit < 0 and not bits[-lit - 1])
                for lit in clause
            ):
                satisfied = False
                break
        if satisfied:
            return True
    return False


def sat_dpll(instance: dict) -> bool:
    """A simple DPLL solver, used for larger reduced formulas."""
    clauses = [list(c) for c in instance["clauses"]]

    def simplify(clauses, assign):
        out = []
        for c in clauses:
            new = []
            sat = False
            for lit in c:
                val = assign.get(abs(lit))
                if val is None:
                    new.append(lit)
                elif (lit > 0) == val:
                    sat = True
                    break
            if sat:
                continue
            if not new:
                return None
            out.append(new)
        return out

    def solve(clauses, assign):
        clauses = simplify(clauses, assign)
        if clauses is None:
            return False
        if not clauses:
            return True
        changed = True
        while changed:
            changed = False
            for c in clauses:
                if len(c) == 1:
                    lit = c[0]
                    v = abs(lit)
                    if v in assign:
                        continue
                    assign = dict(assign)
                    assign[v] = lit > 0
                    clauses = simplify(clauses, {v: lit > 0})
                    if clauses is None:
                        return False
                    changed = True
                    break
        if not clauses:
            return True
        v = abs(clauses[0][0])
        for val in (True, False):
            a = dict(assign)
            a[v] = val
            if solve(clauses, a):
                return True
        return False

    return solve(clauses, {})


# ----------------------------------------------------------------------
# Instance generation
# ----------------------------------------------------------------------

def all_graphs(n: int):
    """All simple graphs on n vertices (edges as sorted pairs)."""
    pairs = list(itertools.combinations(range(n), 2))
    for mask in range(1 << len(pairs)):
        edges = [list(p) for idx, p in enumerate(pairs) if mask >> idx & 1]
        yield {"n": n, "edges": edges}


def random_graph(n: int, p: float, rng: random.Random) -> dict:
    edges = []
    for u, v in itertools.combinations(range(n), 2):
        if rng.random() < p:
            edges.append([u, v])
    return {"n": n, "edges": edges}


MAX_SAT_VARS = 16


def source_instances():
    """Deterministic exhaustive small instances plus random ones."""
    rng = random.Random(12345)
    instances = []

    # Exhaustive over all graphs for n = 0..4, all k in a wide range.
    for n in range(0, 5):
        for g in all_graphs(n):
            for k in range(-2, n + 3):
                instances.append({"n": n, "edges": g["edges"], "k": k})

    # Random larger graphs, keeping the reduced formula small enough for the
    # plain brute-force SAT solver.
    for _ in range(600):
        n = rng.randint(0, 8)
        g = random_graph(n, rng.random(), rng)
        choices = [-2, -1, 0, n + 1, n + 2]
        for k in range(1, n + 1):
            if k * n <= MAX_SAT_VARS:
                choices.append(k)
        instances.append({"n": n, "edges": g["edges"], "k": rng.choice(choices)})

    return instances


def larger_instances():
    """Random instances whose reductions are checked with DPLL."""
    rng = random.Random(999)
    instances = []
    for _ in range(300):
        n = rng.randint(0, 12)
        g = random_graph(n, rng.random(), rng)
        instances.append({"n": n, "edges": g["edges"], "k": rng.randint(-2, n + 2)})
    instances += [
        {"n": 0, "edges": [], "k": 0},
        {"n": 0, "edges": [], "k": -5},
        {"n": 0, "edges": [], "k": 1},
        {"n": 1, "edges": [], "k": 1},
        {"n": 1, "edges": [], "k": 2},
        {"n": 5, "edges": [], "k": 1},
        {"n": 5, "edges": [], "k": 2},
        {"n": 5, "edges": [[0, 1], [1, 2], [2, 3], [3, 4], [0, 4]], "k": 3},
    ]
    return instances


# ----------------------------------------------------------------------
# Tests
# ----------------------------------------------------------------------

def check(inst, sat_solver, failures):
    """Validate, reduce, and compare one instance; return True on pass."""
    try:
        problems.Clique.validate(inst)
    except Exception as exc:  # noqa: BLE001
        failures.append(("source invalid", inst, repr(exc)))
        return False

    reduced = reduce_mod.reduce(inst)

    try:
        problems.Sat.validate(reduced)
    except Exception as exc:  # noqa: BLE001
        failures.append(("reduced invalid", inst, repr(exc)))
        return False

    expected = clique_bruteforce(inst)
    got = sat_solver(reduced)
    if expected != got:
        failures.append(("answer mismatch", inst, (expected, got, reduced)))
        return False
    return True


def main() -> int:
    tests_run = 0
    tests_passed = 0
    failures = []

    for inst in source_instances():
        tests_run += 1
        if check(inst, sat_bruteforce, failures):
            tests_passed += 1

    for inst in larger_instances():
        tests_run += 1
        if check(inst, sat_dpll, failures):
            tests_passed += 1

    print(f"tests_run={tests_run} tests_passed={tests_passed}")
    if failures:
        print(f"FAILURES: {len(failures)}")
        for kind, inst, detail in failures[:20]:
            print("  ", kind, inst, detail)
    else:
        print("ALL TESTS PASSED")

    return 0 if not failures else 1


if __name__ == "__main__":
    raise SystemExit(main())
