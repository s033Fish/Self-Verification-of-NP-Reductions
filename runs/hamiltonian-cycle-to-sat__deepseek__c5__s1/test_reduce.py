"""Independent tests for reduce.py: Hamiltonian Cycle -> SAT.

We implement our own exact solvers from the problem definitions in
problems.py (no solvers are provided there) and compare the answer of
each small source instance with the answer of its reduction.
"""

from __future__ import annotations

import itertools
import random

import problems
from problems import HamiltonianCycle, Sat
from reduce import reduce


# ----------------------------------------------------------------------
# Brute-force solver for Hamiltonian Cycle (SOURCE)
# ----------------------------------------------------------------------

def brute_hamiltonian(instance: dict) -> bool:
    """Exact solver: does the undirected graph have a Hamiltonian cycle?"""
    n = instance["n"]
    edges = instance["edges"]
    if n < 3:
        return False
    adj = [[False] * n for _ in range(n)]
    for u, v in edges:
        adj[u][v] = True
        adj[v][u] = True
    # Fix vertex 0 at the front to cut rotations; try all orderings of 1..n-1.
    for perm in itertools.permutations(range(1, n)):
        order = (0,) + perm
        ok = True
        for i in range(n):
            a = order[i]
            b = order[(i + 1) % n]
            if not adj[a][b]:
                ok = False
                break
        if ok:
            return True
    return False


# ----------------------------------------------------------------------
# Exact solver for SAT (TARGET): DPLL with unit propagation
# ----------------------------------------------------------------------

def dpll_sat(instance: dict) -> bool:
    """Exact CNF satisfiability via DPLL with unit propagation."""
    num_vars = instance["num_vars"]
    clauses = [tuple(c) for c in instance["clauses"]]

    # A clause with both v and -v is a tautology -> drop it.
    simplified = []
    for clause in clauses:
        lits = set(clause)
        if any(-l in lits for l in lits):
            continue
        simplified.append(lits)
    clauses = simplified

    def solve(clauses, assignment):
        # Unit propagation / simplify.
        while True:
            new_clauses = []
            unit = None
            for clause in clauses:
                # Evaluate clause under assignment.
                remaining = set()
                satisfied = False
                for lit in clause:
                    var = abs(lit)
                    val = assignment.get(var)
                    if val is None:
                        remaining.add(lit)
                    elif (lit > 0) == val:
                        satisfied = True
                        break
                if satisfied:
                    continue
                if not remaining:
                    return False  # empty clause -> conflict
                if len(remaining) == 1:
                    unit = next(iter(remaining))
                    break
                new_clauses.append(remaining)
            if unit is None:
                clauses = new_clauses
                break
            var = abs(unit)
            val = unit > 0
            if var in assignment:
                if assignment[var] != val:
                    return False
            else:
                assignment = dict(assignment)
                assignment[var] = val
            # Re-run simplification with new assignment.
            clauses = new_clauses if False else clauses
            # Rebuild from scratch each unit step for simplicity.
            clauses = _simplify(original_clauses, assignment)
            if clauses is None:
                return False
            if not clauses:
                return True
            # loop again to look for units

        if not clauses:
            return True
        # Branch on a variable appearing in the first clause.
        lit = next(iter(clauses[0]))
        var = abs(lit)
        for val in (True, False):
            new_assign = dict(assignment)
            new_assign[var] = val
            res = _simplify(original_clauses, new_assign)
            if res is not None and solve(res, new_assign):
                return True
        return False

    def _simplify(clauses, assignment):
        """Return simplified clause list, or None on conflict."""
        out = []
        for clause in clauses:
            remaining = set()
            satisfied = False
            for lit in clause:
                var = abs(lit)
                val = assignment.get(var)
                if val is None:
                    remaining.add(lit)
                elif (lit > 0) == val:
                    satisfied = True
                    break
            if satisfied:
                continue
            if not remaining:
                return None
            out.append(remaining)
        return out

    original_clauses = clauses
    return solve(clauses, {})


def solve_source(instance: dict) -> bool:
    return brute_hamiltonian(instance)


def solve_target(instance: dict) -> bool:
    return dpll_sat(instance)


# ----------------------------------------------------------------------
# Helpers
# ----------------------------------------------------------------------

def all_graphs(n: int):
    """All simple undirected graphs on n labelled vertices."""
    possible = [(u, v) for u in range(n) for v in range(u + 1, n)]
    for mask in range(1 << len(possible)):
        edges = [list(possible[i]) for i in range(len(possible)) if mask & (1 << i)]
        yield {"n": n, "edges": edges}


def random_graph(n: int, p: float, rng: random.Random) -> dict:
    edges = []
    for u in range(n):
        for v in range(u + 1, n):
            if rng.random() < p:
                edges.append([u, v])
    return {"n": n, "edges": edges}


TESTS_RUN = 0
TESTS_PASSED = 0


def check(instance: dict) -> None:
    global TESTS_RUN, TESTS_PASSED
    TESTS_RUN += 1
    # Validate the source instance and the produced target instance.
    HamiltonianCycle.validate(instance)
    out = reduce(instance)
    Sat.validate(out)
    expected = solve_source(instance)
    got = solve_target(out)
    if expected == got:
        TESTS_PASSED += 1
    else:
        raise AssertionError(
            f"MISMATCH on {instance!r}: source={expected}, reduced={got}, out={out!r}"
        )


def main() -> None:
    # Exhaustive over all graphs for n = 0..4.
    for n in range(0, 6):
        for g in all_graphs(n):
            check(g)

    # Random graphs for larger n (still exact via DPLL).
    rng = random.Random(12345)
    for n in range(5, 9):
        for _ in range(60):
            check(random_graph(n, rng.choice([0.2, 0.4, 0.6, 0.8, 1.0]), rng))

    # Explicit edge cases.
    check({"n": 0, "edges": []})
    check({"n": 1, "edges": []})
    check({"n": 2, "edges": [[0, 1]]})
    check({"n": 3, "edges": [[0, 1], [1, 2], [2, 0]]})   # triangle: yes
    check({"n": 3, "edges": [[0, 1], [1, 2]]})           # path: no
    check({"n": 4, "edges": [[0, 1], [1, 2], [2, 3], [3, 0]]})  # 4-cycle: yes
    check({"n": 4, "edges": [[0, 1], [1, 2], [2, 3]]})   # path: no
    # Complete graphs are always Hamiltonian for n >= 3.
    for n in range(3, 9):
        complete = {"n": n, "edges": [[u, v] for u in range(n) for v in range(u + 1, n)]}
        check(complete)
    # Star graphs (n >= 4) are not Hamiltonian.
    for n in range(4, 9):
        star = {"n": n, "edges": [[0, v] for v in range(1, n)]}
        check(star)

    print(f"tests_run={TESTS_RUN} tests_passed={TESTS_PASSED}")
    assert TESTS_RUN == TESTS_PASSED


if __name__ == "__main__":
    main()
