"""Independent solvers and tests for reduce.py (HamiltonianPath -> Sat)."""
from __future__ import annotations

import itertools
import random

from problems import HamiltonianPath, Sat
from reduce import reduce


# ---------------------------------------------------------------- solvers
def solve_hamiltonian_path(instance) -> bool:
    """Brute force: is there a path visiting every vertex exactly once?"""
    n = instance["n"]
    edges = instance["edges"]
    if n == 0:
        return False
    if n == 1:
        return True
    adj = [[False] * n for _ in range(n)]
    for u, v in edges:
        adj[u][v] = True
        adj[v][u] = True
    for perm in itertools.permutations(range(n)):
        if all(adj[perm[i]][perm[i + 1]] for i in range(n - 1)):
            return True
    return False


def solve_sat(instance) -> bool:
    """DPLL SAT solver with unit propagation and pure-literal elimination."""
    m = instance["num_vars"]
    clauses = [frozenset(c) for c in instance["clauses"]]

    def lit_true(lit, assignment):
        val = assignment.get(abs(lit))
        if val is None:
            return None
        return val if lit > 0 else (not val)

    def simplify(clauses, assignment):
        changed = True
        while changed:
            changed = False
            new_clauses = []
            for cl in clauses:
                sat = False
                rem = []
                for lit in cl:
                    t = lit_true(lit, assignment)
                    if t is True:
                        sat = True
                        break
                    if t is None:
                        rem.append(lit)
                if sat:
                    continue
                if not rem:
                    return None
                if len(rem) == 1:
                    lit = rem[0]
                    var = abs(lit)
                    val = lit > 0
                    if var in assignment:
                        if assignment[var] != val:
                            return None
                    else:
                        assignment[var] = val
                        changed = True
                    continue
                new_clauses.append(frozenset(rem))
            clauses = new_clauses
        return clauses, assignment

    def dpll(clauses, assignment):
        res = simplify(clauses, assignment)
        if res is None:
            return False
        clauses, assignment = res
        if not clauses:
            return True
        pos = set()
        neg = set()
        for cl in clauses:
            for lit in cl:
                (pos if lit > 0 else neg).add(abs(lit))
        for var in pos - neg:
            assignment[var] = True
        for var in neg - pos:
            assignment[var] = False
        res = simplify(clauses, assignment)
        if res is None:
            return False
        clauses, assignment = res
        if not clauses:
            return True
        var = abs(next(iter(next(iter(clauses)))))
        for val in (True, False):
            a2 = dict(assignment)
            a2[var] = val
            if dpll(clauses, a2):
                return True
        return False

    return dpll(clauses, {})


def hk_hamiltonian(instance) -> bool:
    """Exact Hamiltonian path via bitmask DP. O(n^2 2^n)."""
    n = instance["n"]
    if n == 0:
        return False
    if n == 1:
        return True
    adj = [0] * n
    for u, v in instance["edges"]:
        adj[u] |= 1 << v
        adj[v] |= 1 << u
    full = (1 << n) - 1
    dp = [0] * (1 << n)
    for v in range(n):
        dp[1 << v] |= 1 << v
    for mask in range(1 << n):
        ends = dp[mask]
        e = ends
        while e:
            v = (e & -e).bit_length() - 1
            e &= e - 1
            nxt = adj[v] & ~mask
            while nxt:
                w = (nxt & -nxt).bit_length() - 1
                nxt &= nxt - 1
                dp[mask | (1 << w)] |= 1 << w
    return dp[full] != 0



# ---------------------------------------------------------------- generators
def all_graphs(n):
    pairs = list(itertools.combinations(range(n), 2))
    for mask in range(1 << len(pairs)):
        edges = [list(p) for k, p in enumerate(pairs) if (mask >> k) & 1]
        yield {"n": n, "edges": edges}


def random_graph(n, p, rng):
    edges = [[u, v] for u, v in itertools.combinations(range(n), 2) if rng.random() < p]
    return {"n": n, "edges": edges}


# ---------------------------------------------------------------- tests
def main():
    rng = random.Random(12345)
    tests_run = 0
    tests_passed = 0
    failures = []

    def check(inst):
        nonlocal tests_run, tests_passed
        tests_run += 1
        HamiltonianPath.validate(inst)
        out = reduce(inst)
        Sat.validate(out)
        expected = solve_hamiltonian_path(inst)
        got = solve_sat(out)
        if expected == got:
            tests_passed += 1
        else:
            failures.append((inst, expected, got))

    # exhaustive over all graphs for n = 0..6
    for n in range(0, 6):
        for inst in all_graphs(n):
            check(inst)

    # random larger graphs
    for n in range(6, 9):
        for _ in range(60):
            p = rng.choice([0.0, 0.1, 0.2, 0.3, 0.5, 0.8, 1.0])
            check(random_graph(n, p, rng))

    # hand-picked edge cases
    for inst in [
        {"n": 0, "edges": []},
        {"n": 1, "edges": []},
        {"n": 2, "edges": []},
        {"n": 2, "edges": [[0, 1]]},
        {"n": 3, "edges": [[0, 1]]},
        {"n": 3, "edges": [[0, 1], [1, 2]]},
        {"n": 3, "edges": [[0, 1], [1, 2], [0, 2]]},
        {"n": 4, "edges": [[0, 1], [1, 2], [2, 3]]},
        {"n": 4, "edges": [[0, 1], [1, 2], [2, 3], [3, 0]]},
    ]:
        check(inst)

    # Held-Karp cross-check on larger random graphs
    for n in range(6, 10):
        for _ in range(40):
            p = rng.choice([0.05, 0.1, 0.15, 0.2, 0.3, 0.5, 0.7, 0.9, 1.0])
            inst = random_graph(n, p, rng)
            tests_run += 1
            HamiltonianPath.validate(inst)
            out = reduce(inst)
            Sat.validate(out)
            if hk_hamiltonian(inst) == solve_sat(out):
                tests_passed += 1
            else:
                failures.append((inst, hk_hamiltonian(inst), solve_sat(out)))

    # structured graphs
    for n in range(2, 10):
        structured = [
            {"n": n, "edges": [[i, i + 1] for i in range(n - 1)]},          # path
            {"n": n, "edges": [list(e) for e in itertools.combinations(range(n), 2)]},  # complete
            {"n": n, "edges": []},                                          # empty
            {"n": n, "edges": [[0, i] for i in range(1, n)]},               # star
        ]
        if n >= 3:
            structured.append({"n": n, "edges": [[i, (i + 1) % n] for i in range(n)]})  # cycle
            structured.append({"n": n, "edges": [[i, i + 1] for i in range(n - 1)][:-1]})  # path minus edge
        for inst in structured:
            tests_run += 1
            HamiltonianPath.validate(inst)
            out = reduce(inst)
            Sat.validate(out)
            if hk_hamiltonian(inst) == solve_sat(out):
                tests_passed += 1
            else:
                failures.append((inst, hk_hamiltonian(inst), solve_sat(out)))

    print(f"tests_run={tests_run} tests_passed={tests_passed}")
    if failures:
        print("FAILURES:")
        for f in failures[:10]:
            print(f)
    assert tests_run == tests_passed, f"{len(failures)} failures"
    print("ALL TESTS PASSED")


if __name__ == "__main__":
    main()
