"""Tests for the Clique -> SAT reduction, using brute-force solvers."""

from __future__ import annotations

import itertools
import random

from reduce import reduce


# ----------------------------------------------------------------------
# Solvers written from the problem definitions.

def clique_solve(instance: dict) -> bool:
    n = instance["n"]
    edges = instance["edges"]
    k = instance["k"]
    if k <= 0:
        return True
    if k > n:
        return False
    edge_set = set()
    for u, v in edges:
        edge_set.add((u, v))
        edge_set.add((v, u))
    for combo in itertools.combinations(range(n), k):
        if all((a, b) in edge_set for a, b in itertools.combinations(combo, 2)):
            return True
    return False


def sat_solve(instance: dict) -> bool:
    """Simple DPLL satisfiability check (exact)."""
    m = instance["num_vars"]
    clauses = [list(c) for c in instance["clauses"]]

    def dpll(clauses, assignment):
        # assignment: dict var -> bool
        clauses = [c for c in clauses]
        while True:
            # unit propagation
            unit = None
            for c in clauses:
                if len(c) == 0:
                    return False
                if len(c) == 1:
                    unit = c[0]
                    break
            if unit is None:
                break
            var = abs(unit)
            val = unit > 0
            assignment[var] = val
            new_clauses = []
            for c in clauses:
                if any((l > 0) == val and abs(l) == var for l in c):
                    continue  # satisfied
                reduced_c = [l for l in c if abs(l) != var]
                if len(reduced_c) == 0:
                    return False
                new_clauses.append(reduced_c)
            clauses = new_clauses

        if not clauses:
            return True
        # pure literal elimination
        # pick a variable
        var = abs(clauses[0][0])
        for val in (True, False):
            assignment[var] = val
            new_clauses = []
            ok = True
            for c in clauses:
                if any((l > 0) == val and abs(l) == var for l in c):
                    continue
                reduced_c = [l for l in c if abs(l) != var]
                if len(reduced_c) == 0:
                    ok = False
                    break
                new_clauses.append(reduced_c)
            if ok and dpll(new_clauses, dict(assignment)):
                return True
            assignment.pop(var, None)
        return False

    return dpll(clauses, {})


# ----------------------------------------------------------------------
# Instance helpers / generators.

def random_clique(rng: random.Random, max_n: int = 5) -> dict:
    n = rng.randint(0, max_n)
    all_pairs = list(itertools.combinations(range(n), 2))
    edges = [list(p) for p in all_pairs if rng.random() < 0.5]
    k = rng.randint(-2, n + 2)
    return {"n": n, "edges": edges, "k": k}


def edge_cases() -> list[dict]:
    cases = []
    cases.append({"n": 0, "edges": [], "k": 0})
    cases.append({"n": 0, "edges": [], "k": 1})
    cases.append({"n": 0, "edges": [], "k": -5})
    cases.append({"n": 1, "edges": [], "k": 1})
    cases.append({"n": 1, "edges": [], "k": 2})
    tri = [[0, 1], [1, 2], [0, 2]]
    cases.append({"n": 3, "edges": tri, "k": 3})
    cases.append({"n": 3, "edges": tri, "k": 4})
    cases.append({"n": 3, "edges": [[0, 1], [1, 2]], "k": 2})
    cases.append({"n": 3, "edges": [[0, 1], [1, 2]], "k": 3})
    k4 = [list(p) for p in itertools.combinations(range(4), 2)]
    cases.append({"n": 4, "edges": k4, "k": 4})
    cases.append({"n": 4, "edges": k4, "k": 5})
    cases.append({"n": 3, "edges": [[1, 0], [2, 1], [2, 0]], "k": 3})
    return cases


def main() -> int:
    tests_run = 0
    tests_passed = 0

    def check(inst: dict) -> None:
        nonlocal tests_run, tests_passed
        tests_run += 1
        expected = clique_solve(inst)
        reduced = reduce(inst)
        got = sat_solve(reduced)
        assert got == expected, (
            f"mismatch on {inst}: clique={expected}, sat={got}, reduced={reduced}"
        )
        tests_passed += 1

    for inst in edge_cases():
        check(inst)

    rng = random.Random(12345)
    for _ in range(500):
        check(random_clique(rng, max_n=6))

    # exhaustive: all graphs on n<=5 vertices with all k in range
    for n in range(0, 6):
        pairs = list(itertools.combinations(range(n), 2))
        for mask in range(1 << len(pairs)):
            edges = [list(pairs[i]) for i in range(len(pairs)) if mask >> i & 1]
            for k in range(-1, n + 2):
                check({"n": n, "edges": edges, "k": k})

    print(f"tests_run={tests_run} tests_passed={tests_passed}")
    return 0 if tests_run == tests_passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
