"""Tests comparing exact solvers on small Hamiltonian Cycle instances against
the SAT instances produced by reduce()."""

import itertools
import random

from reduce import reduce


# ----------------------------------------------------------------------
# Brute-force solvers (straight from the problem definitions)

def hc_solve(instance):
    """Brute force Hamiltonian Cycle solver. True iff a Hamiltonian cycle exists."""
    n = instance["n"]
    edges = instance["edges"]
    if n <= 2:
        return False
    adj = set()
    for u, v in edges:
        adj.add((u, v))
        adj.add((v, u))
    rest = list(range(1, n))
    for perm in itertools.permutations(rest):
        order = (0,) + perm
        if all((order[i], order[(i + 1) % n]) in adj for i in range(n)):
            return True
    return False


def sat_solve_brute(instance):
    """Brute force SAT solver over all assignments."""
    m = instance["num_vars"]
    clauses = instance["clauses"]
    for bits in itertools.product([False, True], repeat=m):
        good = True
        for clause in clauses:
            if not any((bits[abs(l) - 1] if l > 0 else not bits[abs(l) - 1])
                       for l in clause):
                good = False
                break
        if good:
            return True
    return False


def sat_solve_dpll(instance):
    """Exact DPLL SAT solver (used where brute force is infeasible)."""
    m = instance["num_vars"]
    clauses = [frozenset(c) for c in instance["clauses"]]

    def dpll(clauses, assignment):
        # Unit propagation / simplification
        clauses = [set(c) for c in clauses]
        assignment = dict(assignment)
        while True:
            # Remove satisfied clauses, drop false literals
            new_clauses = []
            unit = None
            for c in clauses:
                if any(lit in assignment and assignment[lit] for lit in c):
                    continue
                remaining = [lit for lit in c
                             if not (lit in assignment and not assignment[lit])]
                if not remaining:
                    return False  # empty clause -> conflict
                if len(remaining) == 1:
                    unit = remaining[0]
                new_clauses.append(set(remaining))
            clauses = new_clauses
            if unit is None:
                break
            assignment[unit] = True
            assignment[-unit] = False
        if not clauses:
            return True
        # Choose a literal
        lit = next(iter(clauses[0]))
        for val in (True, False):
            a = dict(assignment)
            a[lit] = val
            a[-lit] = not val
            if dpll(clauses, a):
                return True
        return False

    return dpll(clauses, {})


# ----------------------------------------------------------------------
# Instance generators

def random_graph(n, p, rng):
    edges = []
    for u in range(n):
        for v in range(u + 1, n):
            if rng.random() < p:
                edges.append([u, v])
    return {"n": n, "edges": edges}


def all_graphs(n):
    pairs = [(u, v) for u in range(n) for v in range(u + 1, n)]
    for mask in range(1 << len(pairs)):
        edges = [list(pairs[i]) for i in range(len(pairs)) if (mask >> i) & 1]
        yield {"n": n, "edges": edges}


# ----------------------------------------------------------------------
# Tests

def main():
    tests_run = 0
    tests_passed = 0

    def check(instance, solver):
        nonlocal tests_run, tests_passed
        tests_run += 1
        expected = hc_solve(instance)
        reduced = reduce(instance)
        got = solver(reduced)
        assert got == expected, (
            f"MISMATCH on {instance}: hc={expected}, sat={got}, reduced={reduced}"
        )
        tests_passed += 1

    # Cross-check the two SAT solvers agree on tiny instances.
    for n in (3, 4):
        for g in all_graphs(n):
            r = reduce(g)
            assert sat_solve_brute(r) == sat_solve_dpll(r), f"solver mismatch {g}"

    # Edge cases n = 0, 1, 2 (all no)
    for n in range(0, 3):
        check({"n": n, "edges": []}, sat_solve_brute)

    # Exhaustive over all graphs for n = 3, 4 (brute force SAT)
    for n in (3, 4):
        for g in all_graphs(n):
            check(g, sat_solve_brute)

    # Random graphs for n = 5, 6 (DPLL)
    rng = random.Random(12345)
    for n in (5, 6):
        for _ in range(400):
            p = rng.choice([0.0, 0.1, 0.2, 0.3, 0.5, 0.8, 1.0])
            check(random_graph(n, p, rng), sat_solve_dpll)

    # Complete graphs and cycles for larger n (must be yes)
    for n in range(3, 10):
        complete = {"n": n, "edges": [[u, v] for u in range(n) for v in range(u + 1, n)]}
        check(complete, sat_solve_dpll)
        cycle = {"n": n, "edges": [[i, (i + 1) % n] for i in range(n)]}
        check(cycle, sat_solve_dpll)

    # Paths (no cycle) for larger n (must be no)
    for n in range(3, 10):
        path = {"n": n, "edges": [[i, i + 1] for i in range(n - 1)]}
        check(path, sat_solve_dpll)

    # Star graphs (no Hamiltonian cycle for n >= 4)
    for n in range(4, 10):
        star = {"n": n, "edges": [[0, i] for i in range(1, n)]}
        check(star, sat_solve_dpll)

    # Validate reduced instances against problems.py validation
    from problems import Sat
    for n in (0, 1, 2, 3, 5, 7):
        g = random_graph(n, 0.5, random.Random(n))
        Sat.validate(reduce(g))

    print(f"tests_run={tests_run} tests_passed={tests_passed}")
    assert tests_run == tests_passed
    return tests_run, tests_passed


if __name__ == "__main__":
    main()
