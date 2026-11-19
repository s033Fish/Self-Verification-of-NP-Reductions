"""Independent tests for reduce.py: 3-Coloring -> SAT.

We implement our own solvers for both problems from the definitions in
problems.py, then compare the answer of every small source instance with
the answer of its reduction.

The 3-colouring solver is a straightforward brute force over all 3^n
colourings.  The SAT solver is an exact DPLL search with unit propagation
(written here, no external solver is used); it is exact, so it agrees with
the definition.
"""

from __future__ import annotations

import itertools
import random

from problems import ThreeColoring, Sat
from reduce import reduce


# ----------------------------------------------------------------------
# Solvers (written from the problem definitions).

def solve_three_coloring(instance) -> bool:
    """Yes iff the graph is 3-colourable (brute force over 3^n)."""
    n = instance["n"]
    edges = instance["edges"]
    for colouring in itertools.product(range(3), repeat=n):
        if all(colouring[u] != colouring[v] for u, v in edges):
            return True
    return False


def solve_sat(instance) -> bool:
    """Yes iff some assignment satisfies every clause (exact DPLL)."""
    num_vars = instance["num_vars"]
    clauses = [tuple(clause) for clause in instance["clauses"]]

    def dpll(clauses, assignment):
        # Unit propagation / simplification.
        clauses = [list(c) for c in clauses]
        assignment = dict(assignment)
        changed = True
        while changed:
            changed = False
            new_clauses = []
            for clause in clauses:
                # Evaluate the clause under the current assignment.
                unassigned = []
                satisfied = False
                for lit in clause:
                    val = assignment.get(abs(lit))
                    if val is None:
                        unassigned.append(lit)
                    elif val == (lit > 0):
                        satisfied = True
                        break
                if satisfied:
                    continue
                if not unassigned:
                    return False  # empty clause -> unsatisfiable
                if len(unassigned) == 1:
                    lit = unassigned[0]
                    var = abs(lit)
                    value = lit > 0
                    if var in assignment and assignment[var] != value:
                        return False
                    if var not in assignment:
                        assignment[var] = value
                        changed = True
                        continue
                new_clauses.append(unassigned)
            clauses = new_clauses
        if not clauses:
            return True
        # Choose a variable to branch on.
        var = abs(clauses[0][0])
        for value in (True, False):
            new_assignment = dict(assignment)
            new_assignment[var] = value
            if dpll(clauses, new_assignment):
                return True
        return False

    return dpll(clauses, {})


# ----------------------------------------------------------------------
# Instance generators.

def all_graphs(n):
    """All simple graphs on vertices 0..n-1."""
    pairs = [(u, v) for u in range(n) for v in range(u + 1, n)]
    for mask in range(1 << len(pairs)):
        edges = [list(pairs[i]) for i in range(len(pairs)) if mask >> i & 1]
        yield {"n": n, "edges": edges}


def random_graph(rng, max_n=7, p=0.5):
    n = rng.randint(0, max_n)
    edges = []
    for u in range(n):
        for v in range(u + 1, n):
            if rng.random() < p:
                edges.append([u, v])
    return {"n": n, "edges": edges}


def main():
    tests_run = 0
    tests_passed = 0
    failures = []

    def check(instance):
        nonlocal tests_run, tests_passed
        tests_run += 1
        expected = solve_three_coloring(instance)
        reduced = reduce(instance)
        # The reduction must produce a valid target instance.
        Sat.validate(reduced)
        got = solve_sat(reduced)
        if got == expected:
            tests_passed += 1
        else:
            failures.append((instance, expected, reduced, got))

    # Exhaustive: all graphs with up to 5 vertices.
    for n in range(0, 6):
        for g in all_graphs(n):
            check(g)

    # Random graphs with more vertices.
    rng = random.Random(12345)
    for _ in range(2000):
        check(random_graph(rng, max_n=9, p=rng.choice([0.15, 0.3, 0.5, 0.8])))

    # Explicit edge cases from the definitions.
    check({"n": 0, "edges": []})                         # yes
    check({"n": 3, "edges": [[0, 1], [1, 2], [0, 2]]})   # triangle, yes
    check({"n": 4, "edges": [[0, 1], [0, 2], [0, 3],
                             [1, 2], [1, 3], [2, 3]]})   # K4, no
    check({"n": 4, "edges": []})                         # yes
    # Odd cycle needs 3 colours: yes. Even cycle: yes.
    check({"n": 5, "edges": [[0, 1], [1, 2], [2, 3], [3, 4], [4, 0]]})
    # K5: no.
    check({"n": 5, "edges": [[u, v] for u in range(5) for v in range(u + 1, 5)]})

    print(f"tests_run={tests_run} tests_passed={tests_passed}")
    if failures:
        print("FAILURES:")
        for inst, exp, red, got in failures[:5]:
            print(" instance:", inst, "expected", exp, "got", got)
            print(" reduced:", red)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
