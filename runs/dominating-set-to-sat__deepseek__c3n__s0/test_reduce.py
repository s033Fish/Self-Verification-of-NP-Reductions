"""Brute-force solvers and tests for the Dominating Set -> SAT reduction."""

from __future__ import annotations

import itertools
import random

import problems
from reduce import reduce


# --------------------------------------------------------------------------
# Solvers written from the problem definitions.
# --------------------------------------------------------------------------

def solve_dominating_set(instance) -> bool:
    n = instance["n"]
    edges = instance["edges"]
    k = instance["k"]

    if k < 0:
        return False
    if n == 0:
        return True
    if k >= n:
        return True

    adj = [set() for _ in range(n)]
    for u, v in edges:
        adj[u].add(v)
        adj[v].add(u)

    def dominates(D) -> bool:
        D = set(D)
        for v in range(n):
            if v in D:
                continue
            if not (adj[v] & D):
                return False
        return True

    for size in range(0, k + 1):
        for combo in itertools.combinations(range(n), size):
            if dominates(combo):
                return True
    return False


def solve_sat_bruteforce(instance) -> bool:
    """Exhaustive truth-table check (only for tiny formulas)."""
    m = instance["num_vars"]
    clauses = instance["clauses"]

    for clause in clauses:
        if len(clause) == 0:
            return False

    for bits in itertools.product([False, True], repeat=m):
        assignment = {v: bits[v - 1] for v in range(1, m + 1)}
        ok = True
        for clause in clauses:
            if not any(
                (lit > 0 and assignment[lit]) or (lit < 0 and not assignment[-lit])
                for lit in clause
            ):
                ok = False
                break
        if ok:
            return True
    return False


def solve_sat_dpll(instance) -> bool:
    """Exact DPLL solver with unit propagation; used for larger formulas."""
    m = instance["num_vars"]
    clauses = [tuple(c) for c in instance["clauses"]]

    for clause in clauses:
        if len(clause) == 0:
            return False

    def simplify(clauses, var, value):
        true_lit = var if value else -var
        false_lit = -true_lit
        new_clauses = []
        for clause in clauses:
            if true_lit in clause:
                continue
            reduced = tuple(l for l in clause if l != false_lit)
            new_clauses.append(reduced)
        return new_clauses

    def dpll(clauses):
        clauses = [c for c in clauses]
        # unit propagation
        changed = True
        while changed:
            changed = False
            for clause in clauses:
                if len(clause) == 0:
                    return False
                if len(clause) == 1:
                    lit = clause[0]
                    var, value = abs(lit), lit > 0
                    clauses = simplify(clauses, var, value)
                    changed = True
                    break
        if not clauses:
            return True
        # choose a variable from the first clause
        lit = clauses[0][0]
        var = abs(lit)
        for value in (True, False):
            if dpll(simplify(clauses, var, value)):
                return True
        return False

    return dpll(clauses)


def solve_sat(instance) -> bool:
    m = instance["num_vars"]
    if m <= 16:
        return solve_sat_bruteforce(instance)
    return solve_sat_dpll(instance)


# --------------------------------------------------------------------------
# Instance generators.
# --------------------------------------------------------------------------

def random_graph(n, rng, p=0.35):
    edges = []
    for u in range(n):
        for v in range(u + 1, n):
            if rng.random() < p:
                edges.append([u, v])
    return edges


def random_source_instances(count, rng):
    instances = []
    # Explicit edge cases.
    instances.append({"n": 0, "edges": [], "k": 0})
    instances.append({"n": 0, "edges": [], "k": -1})
    instances.append({"n": 1, "edges": [], "k": 0})
    instances.append({"n": 1, "edges": [], "k": -3})
    instances.append({"n": 3, "edges": [], "k": 2})   # isolated vertices
    instances.append({"n": 3, "edges": [[0, 1], [1, 2]], "k": 0})
    instances.append({"n": 4, "edges": [[0, 1], [2, 3]], "k": 2})
    instances.append({"n": 4, "edges": [[0, 1], [1, 2], [2, 3], [3, 0]], "k": 5})
    instances.append({"n": 5, "edges": [[0, 1], [1, 2], [2, 3], [3, 4], [4, 0]], "k": 2})
    instances.append({"n": 6, "edges": [[0, 1], [1, 2], [2, 3], [3, 4], [4, 5]], "k": 3})

    while len(instances) < count:
        n = rng.randint(0, 5)
        edges = random_graph(n, rng)
        k = rng.randint(-2, n + 2)
        instances.append({"n": n, "edges": edges, "k": k})
    return instances


# --------------------------------------------------------------------------
# Tests.
# --------------------------------------------------------------------------

def run_tests():
    rng = random.Random(12345)
    tests_run = 0
    tests_passed = 0
    failures = []

    instances = random_source_instances(400, rng)

    for idx, inst in enumerate(instances):
        problems.SOURCE.validate(inst)

        expected = solve_dominating_set(inst)
        reduced = reduce(inst)

        try:
            problems.TARGET.validate(reduced)
        except problems.InvalidInstance as exc:
            failures.append((idx, inst, reduced, f"invalid target: {exc}"))
            tests_run += 1
            continue

        got = solve_sat(reduced)

        tests_run += 1
        if got == expected:
            tests_passed += 1
        else:
            failures.append((idx, inst, reduced, f"expected {expected}, got {got}"))

    # Determinism check.
    for inst in instances[:50]:
        tests_run += 1
        if reduce(inst) == reduce(inst):
            tests_passed += 1
        else:
            failures.append((-1, inst, None, "non-deterministic reduction"))

    print(f"tests_run={tests_run} tests_passed={tests_passed}")
    for failure in failures[:10]:
        print("FAILURE:", failure)

    return tests_run, tests_passed, failures


if __name__ == "__main__":
    run, passed, fails = run_tests()
    assert not fails, f"{len(fails)} failures"
    print("ALL TESTS PASSED")
