"""Tests for reduce.py: exact solvers + randomized/exhaustive comparison."""

from __future__ import annotations

import itertools
import random

from problems import Clique, Sat
from reduce import reduce


# ----------------------------------------------------------------------
# Clique solver (brute force over subsets of size k).

def solve_clique(instance) -> bool:
    """Yes iff graph has a clique of at least k vertices."""
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

    for combo in itertools.combinations(range(n), k):
        if all(adj[combo[a]][combo[b]] for a in range(k) for b in range(a + 1, k)):
            return True
    return False


# ----------------------------------------------------------------------
# SAT solvers: brute force (tiny formulas) and exact DPLL (all formulas).

def solve_sat_bruteforce(instance) -> bool:
    m = instance["num_vars"]
    clauses = instance["clauses"]
    if any(len(clause) == 0 for clause in clauses):
        return False
    for bits in itertools.product([False, True], repeat=m):
        assignment = {v + 1: bits[v] for v in range(m)}
        if all(
            any((lit > 0 and assignment[lit]) or (lit < 0 and not assignment[-lit])
                for lit in clause)
            for clause in clauses
        ):
            return True
    return False


def solve_sat(instance) -> bool:
    """Exact DPLL satisfiability solver."""
    m = instance["num_vars"]
    clauses = [list(c) for c in instance["clauses"]]

    def dpll(clauses, assignment):
        # Simplify with current assignment.
        simplified = []
        for clause in clauses:
            new_clause = []
            satisfied = False
            for lit in clause:
                var = abs(lit)
                if var in assignment:
                    if (lit > 0) == assignment[var]:
                        satisfied = True
                        break
                else:
                    new_clause.append(lit)
            if satisfied:
                continue
            if not new_clause:
                return False  # empty clause -> conflict
            simplified.append(new_clause)

        if not simplified:
            return True  # all clauses satisfied

        # Unit propagation.
        units = [c[0] for c in simplified if len(c) == 1]
        if units:
            assignment = dict(assignment)
            for lit in units:
                var = abs(lit)
                value = lit > 0
                if var in assignment and assignment[var] != value:
                    return False
                assignment[var] = value
            return dpll(simplified, assignment)

        # Choose a variable and branch.
        lit = simplified[0][0]
        var = abs(lit)
        for value in (True, False):
            new_assignment = dict(assignment)
            new_assignment[var] = value
            if dpll(simplified, new_assignment):
                return True
        return False

    return dpll(clauses, {})


# ----------------------------------------------------------------------
# Helpers.

def random_clique_instance(rng: random.Random, max_n: int = 6) -> dict:
    n = rng.randint(0, max_n)
    possible = [(u, v) for u in range(n) for v in range(u + 1, n)]
    rng.shuffle(possible)
    num_edges = rng.randint(0, len(possible))
    edges = [list(e) for e in possible[:num_edges]]
    k = rng.randint(-2, n + 2)
    return {"n": n, "edges": edges, "k": k}


def main() -> None:
    tests_run = 0
    tests_passed = 0

    def check(condition: bool, message: str) -> None:
        nonlocal tests_run, tests_passed
        tests_run += 1
        if condition:
            tests_passed += 1
        else:
            raise AssertionError(message)

    # --- Cross-check DPLL against brute force on tiny formulas ---------
    rng0 = random.Random(999)
    for _ in range(500):
        m = rng0.randint(0, 4)
        num_clauses = rng0.randint(0, 6)
        clauses = []
        for _ in range(num_clauses):
            length = rng0.randint(0, 3)
            clause = []
            for _ in range(length):
                v = rng0.randint(1, m) if m > 0 else 0
                if v == 0:
                    continue
                clause.append(v if rng0.random() < 0.5 else -v)
            clauses.append(clause)
        inst = {"num_vars": m, "clauses": clauses}
        Sat.validate(inst)
        check(solve_sat(inst) == solve_sat_bruteforce(inst),
              f"DPLL vs brute force disagree on {inst}")

    # --- Explicit edge cases -------------------------------------------
    check(solve_clique({"n": 0, "edges": [], "k": 0}) is True, "k<=0 yes")
    check(solve_clique({"n": 0, "edges": [], "k": -5}) is True, "k<0 yes")
    check(solve_clique({"n": 0, "edges": [], "k": 1}) is False, "k>n no")
    check(solve_clique({"n": 3, "edges": [], "k": 1}) is True, "k=1 yes if n>=1")
    check(solve_clique({"n": 3, "edges": [[0, 1], [1, 2]], "k": 3}) is False, "no triangle")
    check(solve_clique({"n": 3, "edges": [[0, 1], [1, 2], [0, 2]], "k": 3}) is True, "triangle")

    # --- Random comparison ---------------------------------------------
    rng = random.Random(12345)
    for _ in range(2000):
        inst = random_clique_instance(rng, max_n=6)
        Clique.validate(inst)
        out = reduce(inst)
        Sat.validate(out)
        expected = solve_clique(inst)
        got = solve_sat(out)
        check(expected == got,
              f"mismatch on {inst}: clique={expected} sat={got}")

    # --- Exhaustive over all graphs on n=0..5 and a range of k ----------
    for n in range(0, 6):
        possible = [(u, v) for u in range(n) for v in range(u + 1, n)]
        for mask in range(1 << len(possible)):
            edges = [list(possible[i]) for i in range(len(possible)) if mask >> i & 1]
            for k in range(-1, n + 2):
                inst = {"n": n, "edges": edges, "k": k}
                Clique.validate(inst)
                out = reduce(inst)
                Sat.validate(out)
                expected = solve_clique(inst)
                got = solve_sat(out)
                check(expected == got,
                      f"exhaustive mismatch on {inst}: clique={expected} sat={got}")

    print(f"tests_run={tests_run} tests_passed={tests_passed}")
    assert tests_run == tests_passed

    import json
    with open("verdict.json", "w") as fh:
        json.dump({"verified": True, "tests_run": tests_run,
                   "tests_passed": tests_passed}, fh)
    print("verdict.json written")


if __name__ == "__main__":
    main()
