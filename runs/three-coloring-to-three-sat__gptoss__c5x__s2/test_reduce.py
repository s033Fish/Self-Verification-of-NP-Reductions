"""Independent tests for reduce.py: 3-Coloring -> 3-SAT.

We implement our own brute-force solvers for both problems (from the
definitions in problems.py) and compare answers on many small instances.
"""

from __future__ import annotations

import itertools
import random

from problems import ThreeColoring, ThreeSat
from reduce import reduce


# ----------------------------------------------------------------------
# Brute-force 3-coloring solver
# ----------------------------------------------------------------------

def solve_three_coloring(n: int, edges) -> bool:
    """True iff the graph is 3-colourable.  Brute force over 3^n colourings."""
    adj = [[] for _ in range(n)]
    for u, v in edges:
        adj[u].append(v)
        adj[v].append(u)
    for colouring in itertools.product(range(3), repeat=n):
        ok = True
        for u in range(n):
            for v in adj[u]:
                if u < v and colouring[u] == colouring[v]:
                    ok = False
                    break
            if not ok:
                break
        if ok:
            return True
    return False


# ----------------------------------------------------------------------
# Brute-force 3-SAT solver (DPLL with unit propagation)
# ----------------------------------------------------------------------

def solve_three_sat(num_vars: int, clauses) -> bool:
    clauses = [tuple(c) for c in clauses]

    def dpll(assignment):
        # unit propagation
        while True:
            unit = None
            for cl in clauses:
                satisfied = False
                unassigned = []
                for lit in cl:
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
                    return None  # conflict
                if len(unassigned) == 1:
                    unit = unassigned[0]
                    break
            if unit is None:
                break
            assignment[abs(unit)] = (unit > 0)

        # all clauses satisfied?
        if all(
            any(abs(lit) in assignment and assignment[abs(lit)] == (lit > 0)
                for lit in cl)
            for cl in clauses
        ):
            return assignment

        # choose an unassigned variable
        var = None
        for cl in clauses:
            for lit in cl:
                if abs(lit) not in assignment:
                    var = abs(lit)
                    break
            if var is not None:
                break
        if var is None:
            return None

        for val in (True, False):
            a2 = dict(assignment)
            a2[var] = val
            res = dpll(a2)
            if res is not None:
                return res
        return None

    return dpll({}) is not None


# ----------------------------------------------------------------------
# Test harness
# ----------------------------------------------------------------------

tests_run = 0
tests_passed = 0
failures = []


def check(n: int, edges) -> None:
    global tests_run, tests_passed
    tests_run += 1
    src = {"n": n, "edges": [list(e) for e in edges]}

    # source must be valid
    ThreeColoring.validate(src)
    expected = solve_three_coloring(n, edges)

    red = reduce(src)

    # target must be valid
    ThreeSat.validate(red)

    got = solve_three_sat(red["num_vars"], red["clauses"])

    if got == expected:
        tests_passed += 1
    else:
        failures.append((n, edges, expected, got, red))


def all_graphs(n: int):
    possible = [(u, v) for u in range(n) for v in range(u + 1, n)]
    for mask in range(1 << len(possible)):
        edges = [possible[i] for i in range(len(possible)) if (mask >> i) & 1]
        yield edges


def main() -> None:
    # Exhaustive over all graphs with n = 0..5 vertices.
    for n in range(0, 6):
        for edges in all_graphs(n):
            check(n, edges)

    # Random larger graphs.
    rng = random.Random(12345)
    for _ in range(300):
        n = rng.randint(6, 8)
        p = rng.random()
        edges = [(u, v) for u in range(n) for v in range(u + 1, n)
                 if rng.random() < p]
        check(n, edges)

    # Specific edge cases.
    check(0, [])
    check(1, [])
    check(3, [(0, 1), (1, 2), (0, 2)])          # K3 yes
    check(4, [(u, v) for u in range(4) for v in range(u + 1, 4)])  # K4 no
    check(4, [(0, 1), (1, 2), (2, 3)])          # path yes
    check(5, [(u, v) for u in range(5) for v in range(u + 1, 5)])  # K5 no
    check(6, [(0, 1), (2, 3), (4, 5)])          # matching yes
    # odd cycle C5 is not 3-colourable? C5 IS 3-colourable (odd cycle needs 3).
    check(5, [(0, 1), (1, 2), (2, 3), (3, 4), (4, 0)])  # C5 yes

    print(f"tests_run={tests_run} tests_passed={tests_passed}")
    if failures:
        print("FAILURES:")
        for f in failures[:10]:
            print(f)
    else:
        print("ALL PASSED")


if __name__ == "__main__":
    main()
