"""Solvers and tests comparing DominatingSet answers to their SAT reductions.

solve_dominating_set is a brute force over subsets.
solve_sat is an exact DPLL solver (unit propagation + branching) so it can
handle the auxiliary variables produced by the reduction.
"""

from __future__ import annotations

import itertools
import random

from reduce import reduce


# ------------------------- exact solvers -------------------------

def solve_dominating_set(instance: dict) -> bool:
    n = instance["n"]
    edges = instance["edges"]
    k = instance["k"]
    if k < 0:
        return False
    if n == 0:
        return True
    if k >= n:
        return True
    adj = [set() for _ in range(n)]
    for u, v in edges:
        adj[u].add(v)
        adj[v].add(u)
    for size in range(0, k + 1):
        for combo in itertools.combinations(range(n), size):
            chosen = set(combo)
            if all(v in chosen or (adj[v] & chosen) for v in range(n)):
                return True
    return False


def solve_sat(instance: dict) -> bool:
    """Exact DPLL. clauses are lists of ints; variables 1..num_vars."""
    m = instance["num_vars"]
    clauses = [list(c) for c in instance["clauses"]]

    def simplify(clauses, assign):
        # assign: dict var -> bool. Returns reduced clause list or None if unsat.
        new = []
        for clause in clauses:
            sat = False
            rest = []
            for lit in clause:
                v = abs(lit)
                val = assign.get(v)
                if val is None:
                    rest.append(lit)
                else:
                    if (lit > 0) == val:
                        sat = True
                        break
            if sat:
                continue
            if not rest:
                return None
            new.append(rest)
        return new

    def dpll(clauses, assign):
        clauses = simplify(clauses, assign)
        if clauses is None:
            return False
        if not clauses:
            return True
        # unit propagation
        units = [c[0] for c in clauses if len(c) == 1]
        if units:
            a = dict(assign)
            for lit in units:
                v = abs(lit)
                val = lit > 0
                if v in a and a[v] != val:
                    return False
                a[v] = val
            return dpll(clauses, a)
        # pure literal elimination
        pos = set()
        neg = set()
        for c in clauses:
            for lit in c:
                (pos if lit > 0 else neg).add(abs(lit))
        pure = (pos - neg) | (neg - pos)
        if pure:
            a = dict(assign)
            for v in pos - neg:
                a[v] = True
            for v in neg - pos:
                a[v] = False
            return dpll(clauses, a)
        # branch on a variable
        v = abs(clauses[0][0])
        for val in (True, False):
            a = dict(assign)
            a[v] = val
            if dpll(clauses, a):
                return True
        return False

    return dpll(clauses, {})


# ------------------------------ tests ---------------------------------

def check(instance: dict) -> None:
    from problems import DominatingSet, Sat
    DominatingSet.validate(instance)
    target = reduce(instance)
    Sat.validate(target)
    expected = solve_dominating_set(instance)
    got = solve_sat(target)
    assert expected == got, (instance, target, expected, got)


def all_graphs(n: int):
    possible = [(u, v) for u in range(n) for v in range(u + 1, n)]
    for r in range(len(possible) + 1):
        for edges in itertools.combinations(possible, r):
            yield [list(e) for e in edges]


def main() -> None:
    tests_run = 0
    tests_passed = 0

    def run(instance: dict) -> None:
        nonlocal tests_run, tests_passed
        tests_run += 1
        check(instance)
        tests_passed += 1

    # Exhaustive small graphs, all k in a wide range (incl. negatives/large).
    for n in range(0, 5):
        for edges in all_graphs(n):
            for k in range(-2, n + 3):
                run({"n": n, "edges": edges, "k": k})

    # Random larger instances (DPLL handles the auxiliary variables).
    rng = random.Random(12345)
    for _ in range(500):
        n = rng.randint(0, 9)
        possible = [(u, v) for u in range(n) for v in range(u + 1, n)]
        edges = [list(e) for e in possible if rng.random() < 0.4]
        k = rng.randint(-1, n + 2)
        run({"n": n, "edges": edges, "k": k})

    # A few specific edge cases.
    run({"n": 0, "edges": [], "k": 0})
    run({"n": 0, "edges": [], "k": 5})
    run({"n": 0, "edges": [], "k": -1})
    run({"n": 1, "edges": [], "k": 0})   # isolated vertex, no
    run({"n": 1, "edges": [], "k": 1})   # isolated vertex, yes
    run({"n": 3, "edges": [], "k": 2})   # 3 isolated vertices, no
    run({"n": 3, "edges": [], "k": 3})   # yes
    run({"n": 4, "edges": [[0, 1], [2, 3]], "k": 2})  # yes
    run({"n": 4, "edges": [[0, 1], [2, 3]], "k": 1})  # no
    # A path of 5 vertices needs ceil(5/3)=2 dominators.
    run({"n": 5, "edges": [[0, 1], [1, 2], [2, 3], [3, 4]], "k": 1})  # no
    run({"n": 5, "edges": [[0, 1], [1, 2], [2, 3], [3, 4]], "k": 2})  # yes
    # Complete graph K5 needs exactly 1.
    run({"n": 5, "edges": [[u, v] for u in range(5) for v in range(u + 1, 5)], "k": 0})  # no
    run({"n": 5, "edges": [[u, v] for u in range(5) for v in range(u + 1, 5)], "k": 1})  # yes

    print(f"tests_run={tests_run} tests_passed={tests_passed}")
    assert tests_run == tests_passed

    import json
    with open("verdict.json", "w") as f:
        json.dump({"verified": True, "tests_run": tests_run,
                   "tests_passed": tests_passed}, f)
    print("verdict.json written")


if __name__ == "__main__":
    main()
