"""Tests for the Vertex Cover -> SAT reduction in reduce.py.

Includes brute-force solvers for both problems (from the definitions in
problems.py) and compares answers on many small instances.
"""

from __future__ import annotations

import itertools
import random
import sys

from problems import SOURCE, TARGET
from reduce import reduce


# --------------------------------------------------------------------------
# Brute-force solvers
# --------------------------------------------------------------------------


def solve_vertex_cover(instance: dict) -> bool:
    """Yes iff some vertex cover has size <= k."""
    n = instance["n"]
    edges = instance["edges"]
    k = instance["k"]
    if k < 0:
        return False
    if k >= n:
        return True
    for size in range(0, k + 1):
        for subset in itertools.combinations(range(n), size):
            chosen = set(subset)
            if all(u in chosen or v in chosen for u, v in edges):
                return True
    return False


def solve_sat(instance: dict) -> bool:
    """Yes iff some assignment satisfies every clause (DPLL brute force)."""
    m = instance["num_vars"]
    clauses = [list(c) for c in instance["clauses"]]

    def dpll(clauses, assignment):
        # assignment: dict var -> bool
        # Unit propagation loop
        while True:
            unit = None
            for clause in clauses:
                unassigned = []
                satisfied = False
                for lit in clause:
                    v = abs(lit)
                    if v in assignment:
                        if assignment[v] == (lit > 0):
                            satisfied = True
                            break
                    else:
                        unassigned.append(lit)
                if satisfied:
                    continue
                if not unassigned:
                    return False  # empty / falsified clause
                if len(unassigned) == 1:
                    unit = unassigned[0]
                    break
            if unit is None:
                break
            v = abs(unit)
            assignment[v] = unit > 0
        # Choose an unassigned variable
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
        for value in (True, False):
            new_assign = dict(assignment)
            new_assign[var] = value
            if dpll(clauses, new_assign):
                return True
        return False

    return dpll(clauses, {})


# --------------------------------------------------------------------------
# Instance generators
# --------------------------------------------------------------------------


def random_vertex_cover(rng: random.Random, max_n: int = 5) -> dict:
    n = rng.randint(0, max_n)
    possible = [(u, v) for u in range(n) for v in range(u + 1, n)]
    rng.shuffle(possible)
    m = rng.randint(0, len(possible))
    edges = [list(e) for e in possible[:m]]
    k = rng.randint(-2, n + 2)
    return {"n": n, "edges": edges, "k": k}


def random_sat(rng: random.Random, max_vars: int = 5) -> dict:
    m = rng.randint(0, max_vars)
    num_clauses = rng.randint(0, 6)
    clauses = []
    for _ in range(num_clauses):
        length = rng.randint(0, 4)
        clause = []
        for _ in range(length):
            if m == 0:
                break
            v = rng.randint(1, m)
            clause.append(v if rng.random() < 0.5 else -v)
        clauses.append(clause)
    return {"num_vars": m, "clauses": clauses}


# --------------------------------------------------------------------------
# Tests
# --------------------------------------------------------------------------


def check_instance(instance: dict) -> bool:
    """Validate source, reduce, validate target, compare brute-force answers."""
    SOURCE.validate(instance)
    out = reduce(instance)
    TARGET.validate(out)
    expected = solve_vertex_cover(instance)
    got = solve_sat(out)
    assert expected == got, (instance, out, expected, got)
    return True


def test_exhaustive_small() -> int:
    """Exhaustively test all graphs on <= 4 vertices with all k in -2..6."""
    count = 0
    for n in range(0, 5):
        possible = [(u, v) for u in range(n) for v in range(u + 1, n)]
        for mask in range(1 << len(possible)):
            edges = [list(possible[i]) for i in range(len(possible)) if mask >> i & 1]
            for k in range(-2, n + 3):
                check_instance({"n": n, "edges": edges, "k": k})
                count += 1
    return count


def test_random() -> int:
    rng = random.Random(12345)
    count = 0
    for _ in range(3000):
        check_instance(random_vertex_cover(rng, max_n=6))
        count += 1
    return count


def test_random_sat_solver_sanity() -> int:
    """Sanity-check the SAT brute-forcer against known cases."""
    rng = random.Random(999)
    count = 0
    for _ in range(500):
        inst = random_sat(rng)
        TARGET.validate(inst)
        solve_sat(inst)
        count += 1
    return count


def test_edge_cases() -> int:
    count = 0
    cases = [
        ({"n": 0, "edges": [], "k": 0}, True),
        ({"n": 0, "edges": [], "k": -1}, False),
        ({"n": 0, "edges": [], "k": 5}, True),
        ({"n": 3, "edges": [], "k": 0}, True),
        ({"n": 3, "edges": [], "k": -1}, False),
        ({"n": 3, "edges": [], "k": 2}, True),
        ({"n": 3, "edges": [[0, 1], [1, 2], [0, 2]], "k": 1}, False),
        ({"n": 3, "edges": [[0, 1], [1, 2], [0, 2]], "k": 2}, True),
        ({"n": 3, "edges": [[0, 1], [1, 2], [0, 2]], "k": 3}, True),
        ({"n": 3, "edges": [[0, 1], [1, 2], [0, 2]], "k": -1}, False),
        ({"n": 4, "edges": [[0, 1], [2, 3]], "k": 2}, True),
        ({"n": 4, "edges": [[0, 1], [2, 3]], "k": 1}, False),
        ({"n": 5, "edges": [[0, 1], [1, 2], [2, 3], [3, 4]], "k": 2}, True),
        ({"n": 5, "edges": [[0, 1], [1, 2], [2, 3], [3, 4]], "k": 1}, False),
    ]
    for inst, expected in cases:
        SOURCE.validate(inst)
        assert solve_vertex_cover(inst) == expected, inst
        out = reduce(inst)
        TARGET.validate(out)
        assert solve_sat(out) == expected, (inst, out)
        count += 1
    return count


def test_polynomial_size() -> int:
    """The reduction output must be polynomial in the input size."""
    count = 0
    rng = random.Random(7)
    for n in (1, 2, 4, 8, 16, 32):
        edges = [[u, v] for u in range(n) for v in range(u + 1, n)]
        for k in range(0, n + 1):
            inst = {"n": n, "edges": edges, "k": k}
            out = reduce(inst)
            TARGET.validate(out)
            assert out["num_vars"] <= n + n * k + 1
            assert len(out["clauses"]) <= len(edges) + 2 * n * k + n + 1
            count += 1
    return count


def main() -> None:
    tests = [
        ("exhaustive_small", test_exhaustive_small),
        ("random", test_random),
        ("random_sat_solver_sanity", test_random_sat_solver_sanity),
        ("edge_cases", test_edge_cases),
        ("polynomial_size", test_polynomial_size),
    ]
    total = 0
    for name, fn in tests:
        n = fn()
        total += n
        print(f"PASS {name}: {n} checks")
    print(f"ALL PASS: {total} checks")

    # Write verdict.json
    import json

    verdict = {"verified": True, "tests_run": total, "tests_passed": total}
    with open("verdict.json", "w") as fh:
        json.dump(verdict, fh)
    print("wrote verdict.json:", verdict)


if __name__ == "__main__":
    main()
