"""Independent tests for reduce.py (Hamiltonian Path -> SAT).

We implement our own brute-force solvers for both problems from the
definitions in problems.py, then compare answers on many small instances.
"""

from __future__ import annotations

import itertools
import json
import random

from problems import HamiltonianPath, Sat
from reduce import reduce


# ----------------------------------------------------------------------
# Brute-force solvers (written from the problem definitions)
# ----------------------------------------------------------------------

def solve_hamiltonian_path(instance) -> bool:
    """Yes iff there is a path visiting every vertex exactly once."""
    HamiltonianPath.validate(instance)
    n = instance["n"]
    edges = {frozenset(e) for e in instance["edges"]}

    if n == 0:
        return False
    if n == 1:
        return True

    # Try every ordering of the vertices as a candidate path.
    for perm in itertools.permutations(range(n)):
        ok = True
        for i in range(n - 1):
            if frozenset((perm[i], perm[i + 1])) not in edges:
                ok = False
                break
        if ok:
            return True
    return False


def solve_sat_bruteforce(instance) -> bool:
    """Yes iff some assignment satisfies every clause. Exhaustive search."""
    Sat.validate(instance)
    m = instance["num_vars"]
    clauses = instance["clauses"]

    for bits in range(1 << m):
        assignment = {}
        for v in range(1, m + 1):
            assignment[v] = bool((bits >> (v - 1)) & 1)
        satisfied = True
        for clause in clauses:
            if not any(
                (lit > 0 and assignment[abs(lit)]) or
                (lit < 0 and not assignment[abs(lit)])
                for lit in clause
            ):
                satisfied = False
                break
        if satisfied:
            return True
    return False


def solve_sat_dpll(instance) -> bool:
    """Exact DPLL SAT solver used when brute force is too large."""
    Sat.validate(instance)
    m = instance["num_vars"]
    clauses = [frozenset(c) for c in instance["clauses"]]

    def dpll(clauses, assignment):
        # Simplify clauses under the current assignment.
        simplified = []
        for clause in clauses:
            new_clause = set()
            sat = False
            for lit in clause:
                v = abs(lit)
                if v in assignment:
                    if assignment[v] == (lit > 0):
                        sat = True
                        break
                else:
                    new_clause.add(lit)
            if sat:
                continue
            if not new_clause:
                return False  # empty clause -> conflict
            simplified.append(frozenset(new_clause))

        if not simplified:
            return True  # all clauses satisfied

        # Unit propagation.
        units = [next(iter(c)) for c in simplified if len(c) == 1]
        if units:
            new_assignment = dict(assignment)
            for lit in units:
                v = abs(lit)
                val = lit > 0
                if v in new_assignment and new_assignment[v] != val:
                    return False
                new_assignment[v] = val
            return dpll(simplified, new_assignment)

        # Branch on the most frequent literal.
        counts = {}
        for c in simplified:
            for lit in c:
                counts[lit] = counts.get(lit, 0) + 1
        lit = max(counts, key=counts.get)
        v = abs(lit)
        for val in (lit > 0, lit < 0):
            new_assignment = dict(assignment)
            new_assignment[v] = val
            if dpll(simplified, new_assignment):
                return True
        return False

    return dpll(clauses, {})


def solve_sat(instance) -> bool:
    Sat.validate(instance)
    if instance["num_vars"] <= 20:
        return solve_sat_bruteforce(instance)
    return solve_sat_dpll(instance)


# ----------------------------------------------------------------------
# Instance generation
# ----------------------------------------------------------------------

def all_graphs(n):
    """All undirected simple graphs on n labelled vertices."""
    pairs = list(itertools.combinations(range(n), 2))
    for mask in range(1 << len(pairs)):
        edges = [list(p) for k, p in enumerate(pairs) if (mask >> k) & 1]
        yield {"n": n, "edges": edges}


def random_graph(n, p, rng):
    edges = []
    for u, v in itertools.combinations(range(n), 2):
        if rng.random() < p:
            edges.append([u, v])
    return {"n": n, "edges": edges}


# ----------------------------------------------------------------------
# Test driver
# ----------------------------------------------------------------------

def main():
    tests_run = 0
    tests_passed = 0
    failures = []

    def check(instance, label):
        nonlocal tests_run, tests_passed
        tests_run += 1
        try:
            expected = solve_hamiltonian_path(instance)
            reduced = reduce(instance)
            got = solve_sat(reduced)
            if expected == got:
                tests_passed += 1
            else:
                failures.append((label, instance, expected, got, reduced))
        except Exception as exc:  # noqa: BLE001
            failures.append((label, instance, "EXCEPTION", repr(exc), None))

    # Exhaustive: all graphs on 0..4 vertices.
    for n in range(0, 5):
        for g in all_graphs(n):
            check(g, f"exhaustive n={n}")

    # Random graphs on 5..7 vertices.
    rng = random.Random(12345)
    for n in range(5, 8):
        for _ in range(300):
            p = rng.choice([0.1, 0.2, 0.3, 0.5, 0.7, 0.9])
            check(random_graph(n, p, rng), f"random n={n} p={p}")

    # Specific structured cases: paths, cycles, complete graphs, empty graphs.
    for n in range(1, 9):
        check({"n": n, "edges": []}, f"empty n={n}")
        complete = [[u, v] for u, v in itertools.combinations(range(n), 2)]
        check({"n": n, "edges": complete}, f"complete n={n}")
        path = [[i, i + 1] for i in range(n - 1)]
        check({"n": n, "edges": path}, f"path n={n}")
        if n >= 3:
            cycle = path + [[0, n - 1]]
            check({"n": n, "edges": cycle}, f"cycle n={n}")

    # Edge cases explicitly named in the definitions.
    check({"n": 0, "edges": []}, "n=0")
    check({"n": 1, "edges": []}, "n=1")
    check({"n": 2, "edges": []}, "n=2 no edge")
    check({"n": 2, "edges": [[0, 1]]}, "n=2 with edge")
    check({"n": 2, "edges": [[1, 0]]}, "n=2 reversed edge")

    print(f"tests_run={tests_run} tests_passed={tests_passed} failures={len(failures)}")
    for f in failures[:20]:
        print("FAIL:", f[0], f[1], "expected", f[2], "got", f[3])

    verified = len(failures) == 0 and tests_run > 0
    with open("verdict.json", "w") as fh:
        json.dump(
            {"verified": verified, "tests_run": tests_run, "tests_passed": tests_passed},
            fh,
        )
    print("verdict:", {"verified": verified, "tests_run": tests_run, "tests_passed": tests_passed})


if __name__ == "__main__":
    main()
