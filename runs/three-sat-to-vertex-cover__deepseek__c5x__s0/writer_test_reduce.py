"""Tests comparing brute-force 3-SAT and Vertex Cover answers under reduce()."""

from __future__ import annotations

import itertools
import random

from problems import ThreeSat, VertexCover
from reduce import reduce


# ----------------------------------------------------------------------
# Brute-force solvers written from the problem definitions.
# ----------------------------------------------------------------------

def sat_solve(instance):
    """Brute force 3-SAT: try every assignment of variables 1..m."""
    m = instance["num_vars"]
    clauses = instance["clauses"]
    for bits in itertools.product([False, True], repeat=m):
        assignment = {v: bits[v - 1] for v in range(1, m + 1)}
        if all(
            any(
                (lit > 0 and assignment[abs(lit)]) or
                (lit < 0 and not assignment[abs(lit)])
                for lit in clause
            )
            for clause in clauses
        ):
            return True
    return False


def min_vertex_cover_size(n, edges):
    """Exact minimum vertex cover size by branching on an uncovered edge."""
    edge_list = [tuple(e) for e in edges]
    best = [n]

    def rec(remaining, chosen):
        if chosen >= best[0]:
            return
        if not remaining:
            best[0] = chosen
            return
        u, v = remaining[0]
        rec([e for e in remaining if u not in e], chosen + 1)
        rec([e for e in remaining if v not in e], chosen + 1)

    rec(edge_list, 0)
    return best[0]


def vc_solve(instance):
    """Brute force Vertex Cover: yes iff min cover size <= k."""
    k = instance["k"]
    if k < 0:
        return False
    return min_vertex_cover_size(instance["n"], instance["edges"]) <= k


# ----------------------------------------------------------------------
# Instance generation
# ----------------------------------------------------------------------

def random_formula(rng, m, max_clauses):
    clauses = []
    if m >= 3:
        for _ in range(rng.randint(0, max_clauses)):
            variables = rng.sample(range(1, m + 1), 3)
            clause = [v if rng.random() < 0.5 else -v for v in variables]
            clauses.append(clause)
    return {"num_vars": m, "clauses": clauses}


def all_formulas_m3():
    """Every formula over 3 variables with up to 2 clauses (with repeats)."""
    literals = [1, -1, 2, -2, 3, -3]
    possible = []
    for perm in itertools.permutations(literals, 3):
        if len({abs(x) for x in perm}) == 3:
            possible.append(list(perm))
    # canonicalize by variable order to avoid pure permutations
    canon = []
    seen = set()
    for cl in possible:
        key = tuple(sorted(cl, key=abs))
        if key not in seen:
            seen.add(key)
            canon.append(list(key))
    formulas = [{"num_vars": 3, "clauses": []}]
    for cl in canon:
        formulas.append({"num_vars": 3, "clauses": [cl]})
    for c1 in canon:
        for c2 in canon:
            formulas.append({"num_vars": 3, "clauses": [list(c1), list(c2)]})
    return formulas


# ----------------------------------------------------------------------
# Test driver
# ----------------------------------------------------------------------

def main():
    rng = random.Random(12345)
    tests = []

    # Edge cases: no clauses for m = 0..4.
    for m in range(0, 5):
        tests.append({"num_vars": m, "clauses": []})

    # Exhaustive-ish small formulas over 3 variables.
    tests.extend(all_formulas_m3())

    # Random formulas for m = 3..5.
    for _ in range(400):
        m = rng.randint(3, 5)
        tests.append(random_formula(rng, m, 4))

    # A few with many duplicate clauses.
    for _ in range(40):
        m = rng.randint(3, 5)
        base = random_formula(rng, m, 1)
        if base["clauses"]:
            base["clauses"] = base["clauses"] * rng.randint(2, 4)
        tests.append(base)

    tests_run = 0
    tests_passed = 0
    for inst in tests:
        tests_run += 1
        ThreeSat.validate(inst)
        reduced = reduce(inst)
        VertexCover.validate(reduced)
        expected = sat_solve(inst)
        got = vc_solve(reduced)
        if expected != got:
            print("FAIL", inst, "->", reduced, "expected", expected, "got", got)
            continue
        tests_passed += 1

    print(f"tests_run={tests_run} tests_passed={tests_passed}")
    return tests_run, tests_passed


if __name__ == "__main__":
    main()
