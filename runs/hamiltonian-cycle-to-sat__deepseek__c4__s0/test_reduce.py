"""Brute-force solvers and randomized tests for the HC -> SAT reduction."""

import itertools
import json
import random

from problems import HamiltonianCycle, Sat
from reduce import reduce


# ----------------------------------------------------------------------
# Solvers written directly from the problem definitions.

def solve_hamiltonian(instance: dict) -> bool:
    n = instance["n"]
    if n <= 2:
        return False
    adj = [[False] * n for _ in range(n)]
    for u, v in instance["edges"]:
        adj[u][v] = True
        adj[v][u] = True
    start = 0
    rest = list(range(1, n))
    for perm in itertools.permutations(rest):
        order = (start,) + perm
        if all(adj[order[k]][order[(k + 1) % n]] for k in range(n)):
            return True
    return False


def solve_sat_brute(instance: dict) -> bool:
    m = instance["num_vars"]
    clauses = instance["clauses"]
    for bits in itertools.product([False, True], repeat=m):
        good = True
        for clause in clauses:
            if not any((lit > 0) == bits[abs(lit) - 1] for lit in clause):
                good = False
                break
        if good:
            return True
    return False


def solve_sat_dpll(instance: dict) -> bool:
    """Simple DPLL with unit propagation; returns True iff satisfiable."""
    clauses = [set(c) for c in instance["clauses"]]
    assignment = {}

    def simplify(clauses, assignment):
        out = []
        for clause in clauses:
            new = set()
            sat = False
            for lit in clause:
                var = abs(lit)
                if var in assignment:
                    if assignment[var] == (lit > 0):
                        sat = True
                        break
                else:
                    new.add(lit)
            if sat:
                continue
            if not new:
                return None  # conflict
            out.append(new)
        return out

    def dpll(clauses, assignment):
        clauses = simplify(clauses, assignment)
        if clauses is None:
            return False
        if not clauses:
            return True
        # unit propagation
        changed = True
        while changed:
            changed = False
            for clause in clauses:
                if len(clause) == 1:
                    lit = next(iter(clause))
                    var = abs(lit)
                    val = lit > 0
                    if var in assignment and assignment[var] != val:
                        return False
                    if var not in assignment:
                        assignment[var] = val
                        changed = True
            clauses = simplify(clauses, assignment)
            if clauses is None:
                return False
            if not clauses:
                return True
        # choose a variable
        var = abs(next(iter(clauses[0])))
        for val in (True, False):
            new_assign = dict(assignment)
            new_assign[var] = val
            if dpll(clauses, new_assign):
                return True
        return False

    return dpll(clauses, assignment)


def solve_sat(instance: dict) -> bool:
    # Cross-check the two solvers on small formulas.
    if instance["num_vars"] <= 12:
        a = solve_sat_brute(instance)
        b = solve_sat_dpll(instance)
        assert a == b, (instance, a, b)
        return a
    return solve_sat_dpll(instance)


# ----------------------------------------------------------------------
# Tests

def all_graphs(n):
    pairs = [(u, v) for u in range(n) for v in range(u + 1, n)]
    for mask in range(1 << len(pairs)):
        edges = [list(p) for k, p in enumerate(pairs) if mask >> k & 1]
        yield {"n": n, "edges": edges}


def check(instance, stats):
    HamiltonianCycle.validate(instance)
    reduced = reduce(instance)
    Sat.validate(reduced)
    a = solve_hamiltonian(instance)
    b = solve_sat(reduced)
    stats["run"] += 1
    if a == b:
        stats["passed"] += 1
    else:
        stats["failures"].append((instance, reduced, a, b))
    return a == b


def main():
    stats = {"run": 0, "passed": 0, "failures": []}

    # Exhaustive over all graphs with n = 0..5.
    for n in range(0, 6):
        for g in all_graphs(n):
            check(g, stats)

    # Random larger graphs.
    rng = random.Random(12345)
    for _ in range(500):
        n = rng.randint(3, 9)
        pairs = [(u, v) for u in range(n) for v in range(u + 1, n)]
        p = rng.choice([0.15, 0.3, 0.5, 0.7, 0.9])
        edges = [list(q) for q in pairs if rng.random() < p]
        check({"n": n, "edges": edges}, stats)

    # Explicit edge cases.
    assert solve_hamiltonian({"n": 0, "edges": []}) is False
    assert solve_hamiltonian({"n": 1, "edges": []}) is False
    assert solve_hamiltonian({"n": 2, "edges": [[0, 1]]}) is False
    assert solve_hamiltonian({"n": 3, "edges": [[0, 1], [1, 2], [0, 2]]}) is True
    assert solve_hamiltonian({"n": 3, "edges": [[0, 1], [1, 2]]}) is False
    for n in (0, 1, 2):
        r = reduce({"n": n, "edges": []})
        Sat.validate(r)
        assert solve_sat(r) is False

    print("tests run:", stats["run"], "passed:", stats["passed"])
    for inst, red, a, b in stats["failures"][:5]:
        print("FAIL", inst, "hc=", a, "sat=", b)
    assert not stats["failures"], "some tests failed"

    with open("verdict.json", "w") as f:
        json.dump(
            {"verified": True, "tests_run": stats["run"], "tests_passed": stats["passed"]},
            f,
        )
    print("verdict written")


if __name__ == "__main__":
    main()
