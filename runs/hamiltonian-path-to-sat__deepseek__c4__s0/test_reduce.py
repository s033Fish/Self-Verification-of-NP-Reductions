"""Tests for the Hamiltonian Path -> SAT reduction.

Contains brute-force / DPLL solvers for both problems written from the
definitions in problems.py, plus exhaustive and randomized comparisons.
"""

from __future__ import annotations

import itertools
import json
import random

import problems
import reduce as reduce_mod


# ----------------------------------------------------------------------
# Solvers written from the problem definitions

def solve_hamiltonian_path(instance: dict) -> bool:
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
    for perm in itertools.permutations(range(n)):
        if all(adj[perm[i]][perm[i + 1]] for i in range(n - 1)):
            return True
    return False


def solve_sat(instance: dict) -> bool:
    """DPLL over the CNF, handling empty clauses and repeated literals."""
    num_vars = instance["num_vars"]
    clauses = [list(c) for c in instance["clauses"]]
    if any(len(c) == 0 for c in clauses):
        return False
    return _dpll(clauses, {})


def _dpll(clauses, assign):
    # Simplify clauses under the current assignment.
    simplified = []
    for clause in clauses:
        sat = False
        rest = []
        for lit in clause:
            var = abs(lit)
            val = assign.get(var)
            if val is None:
                rest.append(lit)
            elif (lit > 0) == val:
                sat = True
                break
        if sat:
            continue
        if not rest:
            return False
        simplified.append(rest)
    if not simplified:
        return True
    # Unit propagation.
    for clause in simplified:
        if len(clause) == 1:
            lit = clause[0]
            var = abs(lit)
            val = lit > 0
            if var in assign:
                if assign[var] != val:
                    return False
                continue
            new_assign = dict(assign)
            new_assign[var] = val
            return _dpll(simplified, new_assign)
    # Choose the variable occurring most often.
    counts = {}
    for clause in simplified:
        for lit in clause:
            counts[abs(lit)] = counts.get(abs(lit), 0) + 1
    var = max(counts, key=counts.get)
    for val in (True, False):
        new_assign = dict(assign)
        new_assign[var] = val
        if _dpll(simplified, new_assign):
            return True
    return False


# ----------------------------------------------------------------------
# Helpers

def all_graphs(n: int):
    pairs = [(u, v) for u in range(n) for v in range(u + 1, n)]
    for mask in range(1 << len(pairs)):
        edges = [list(pairs[k]) for k in range(len(pairs)) if mask & (1 << k)]
        yield {"n": n, "edges": edges}


def check(instance: dict, stats: dict) -> None:
    problems.HamiltonianPath.validate(instance)
    out = reduce_mod.reduce(instance)
    problems.Sat.validate(out)
    expected = solve_hamiltonian_path(instance)
    got = solve_sat(out)
    stats["run"] += 1
    assert expected == got, (
        f"MISMATCH on {instance}: hp={expected}, sat={got}, reduction={out}"
    )
    stats["passed"] += 1


def main() -> None:
    stats = {"run": 0, "passed": 0}

    # Exhaustive over all graphs for small n.
    for n in range(0, 6):
        for instance in all_graphs(n):
            check(instance, stats)

    # Random larger graphs.
    rng = random.Random(12345)
    for _ in range(600):
        n = rng.randint(0, 9)
        pairs = [(u, v) for u in range(n) for v in range(u + 1, n)]
        p = rng.choice([0.15, 0.3, 0.5, 0.8])
        edges = [list(pr) for pr in pairs if rng.random() < p]
        check({"n": n, "edges": edges}, stats)

    # Structured cases: empty, path, complete, cycle.
    for n in range(0, 10):
        check({"n": n, "edges": []}, stats)
        check({"n": n, "edges": [[i, i + 1] for i in range(n - 1)]}, stats)
        check(
            {"n": n, "edges": [[u, v] for u in range(n) for v in range(u + 1, n)]},
            stats,
        )
        if n >= 3:
            check({"n": n, "edges": [[i, (i + 1) % n] for i in range(n)]}, stats)

    # Edge cases explicitly required by the docstrings.
    assert solve_hamiltonian_path({"n": 0, "edges": []}) is False
    assert solve_hamiltonian_path({"n": 1, "edges": []}) is True
    assert solve_hamiltonian_path({"n": 2, "edges": []}) is False
    assert solve_hamiltonian_path({"n": 2, "edges": [[0, 1]]}) is True
    assert solve_sat({"num_vars": 0, "clauses": []}) is True
    assert solve_sat({"num_vars": 0, "clauses": [[]]}) is False

    print(f"tests_run={stats['run']} tests_passed={stats['passed']}")
    assert stats["run"] == stats["passed"]

    with open("verdict.json", "w") as fh:
        json.dump(
            {"verified": True, "tests_run": stats["run"], "tests_passed": stats["passed"]},
            fh,
        )
    print("verdict.json written")


if __name__ == "__main__":
    main()
