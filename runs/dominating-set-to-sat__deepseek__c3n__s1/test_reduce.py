"""Tests for the Dominating Set -> SAT reduction in reduce.py.

Contains exact solvers for both problems (from the definitions in
problems.py) and compares their answers on many small source instances.
The SAT solver is a straightforward DPLL search (unit propagation +
branching), which is exact but avoids enumerating 2^num_vars assignments
when many auxiliary variables are present.
"""

from __future__ import annotations

import itertools
import random

import problems
from reduce import reduce


# ----------------------------------------------------------------------
# Exact solvers

def brute_dominating_set(instance: dict) -> bool:
    """True iff the graph has a dominating set of size <= k."""
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

    vertices = list(range(n))
    for size in range(0, k + 1):
        for subset in itertools.combinations(vertices, size):
            chosen = set(subset)
            dominated = set(chosen)
            for v in chosen:
                dominated |= adj[v]
            if len(dominated) == n:
                return True
    return False


def brute_sat(instance: dict) -> bool:
    """Exact DPLL solver: True iff some assignment satisfies every clause."""
    m = instance["num_vars"]
    clauses = [tuple(c) for c in instance["clauses"]]

    def dpll(clauses, assignment):
        # Unit propagation.
        while True:
            unit = None
            for clause in clauses:
                unassigned = []
                satisfied = False
                for lit in clause:
                    var = abs(lit)
                    val = assignment.get(var)
                    if val is None:
                        unassigned.append(lit)
                    elif (lit > 0) == val:
                        satisfied = True
                        break
                if satisfied:
                    continue
                if not unassigned:
                    return False  # empty / falsified clause
                if len(unassigned) == 1:
                    unit = unassigned[0]
                    break
            if unit is None:
                break
            var = abs(unit)
            val = unit > 0
            if var in assignment and assignment[var] != val:
                return False
            assignment = dict(assignment)
            assignment[var] = val

        # Choose an unassigned variable.
        var = None
        for clause in clauses:
            for lit in clause:
                if abs(lit) not in assignment:
                    var = abs(lit)
                    break
            if var is not None:
                break
        if var is None:
            return True  # all clauses satisfied

        for val in (True, False):
            new_assignment = dict(assignment)
            new_assignment[var] = val
            if dpll(clauses, new_assignment):
                return True
        return False

    return dpll(clauses, {})


# ----------------------------------------------------------------------
# Instance generators

def random_ds_instance(rng: random.Random) -> dict:
    n = rng.randint(0, 8)
    all_edges = [(u, v) for u in range(n) for v in range(u + 1, n)]
    rng.shuffle(all_edges)
    edges = [list(e) for e in all_edges[: rng.randint(0, len(all_edges))]]
    k = rng.randint(-2, n + 2)
    return {"n": n, "edges": edges, "k": k}


def all_small_ds_instances():
    """Exhaustive small instances: all graphs on <= 4 vertices, k in -1..5."""
    for n in range(0, 5):
        all_edges = [(u, v) for u in range(n) for v in range(u + 1, n)]
        for mask in range(1 << len(all_edges)):
            edges = [list(all_edges[i]) for i in range(len(all_edges)) if mask >> i & 1]
            for k in range(-1, 6):
                yield {"n": n, "edges": edges, "k": k}


def main() -> None:
    tests_run = 0
    tests_passed = 0

    def check(instance: dict) -> None:
        nonlocal tests_run, tests_passed
        tests_run += 1
        problems.DominatingSet.validate(instance)
        target = reduce(instance)
        problems.Sat.validate(target)
        expected = brute_dominating_set(instance)
        got = brute_sat(target)
        assert expected == got, (
            f"mismatch: source={instance} expected={expected} got={got} "
            f"target={target}"
        )
        tests_passed += 1

    # Exhaustive small instances.
    for instance in all_small_ds_instances():
        check(instance)

    # Random larger instances.
    rng = random.Random(12345)
    for _ in range(400):
        check(random_ds_instance(rng))

    # Hand-picked edge cases.
    edge_cases = [
        {"n": 0, "edges": [], "k": 0},
        {"n": 0, "edges": [], "k": 5},
        {"n": 0, "edges": [], "k": -1},
        {"n": 1, "edges": [], "k": 0},
        {"n": 1, "edges": [], "k": 1},
        {"n": 1, "edges": [], "k": -1},
        {"n": 3, "edges": [], "k": 2},          # 3 isolated vertices
        {"n": 3, "edges": [], "k": 3},
        {"n": 4, "edges": [[0, 1], [2, 3]], "k": 2},
        {"n": 4, "edges": [[0, 1], [2, 3]], "k": 1},
        {"n": 5, "edges": [[0, 1], [1, 2], [2, 3], [3, 4]], "k": 2},
        {"n": 5, "edges": [[0, 1], [1, 2], [2, 3], [3, 4]], "k": 1},
        {"n": 6, "edges": [[0, 1], [2, 3], [4, 5]], "k": 3},
        {"n": 6, "edges": [[0, 1], [2, 3], [4, 5]], "k": 2},
        {"n": 4, "edges": [[0, 1], [1, 2], [2, 3], [3, 0]], "k": 1},
        {"n": 4, "edges": [[0, 1], [1, 2], [2, 3], [3, 0]], "k": 2},
        {"n": 7, "edges": [[0, 1], [1, 2], [2, 3], [3, 4], [4, 5], [5, 6], [6, 0]], "k": 3},
    ]
    for instance in edge_cases:
        check(instance)

    # Structural sanity: k >= n always yes, k < 0 always no.
    for n in range(0, 6):
        inst = {"n": n, "edges": [], "k": n}
        assert brute_dominating_set(inst) is True
        assert brute_sat(reduce(inst)) is True
        inst = {"n": n, "edges": [], "k": -1}
        assert brute_dominating_set(inst) is False
        assert brute_sat(reduce(inst)) is False

    print(f"tests_run={tests_run} tests_passed={tests_passed}")
    assert tests_run == tests_passed


if __name__ == "__main__":
    main()
