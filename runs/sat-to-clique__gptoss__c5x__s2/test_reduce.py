"""Independent verification of reduce.py (SAT -> Clique).

We implement our own solvers for both problems straight from the docstrings
in problems.py (no solvers are provided there) and compare the answer of the
source instance with the answer of its reduction.

Solvers used:
  * brute_sat  : exhaustive over all 2^m assignments (tiny m).
  * dpll_sat   : DPLL with unit propagation (larger m).
  * brute_clique / max_clique_ge : exact max-clique search.

reduce.py is never trusted and never modified.
"""

from __future__ import annotations

import itertools
import random
import time

from problems import Sat, Clique
import reduce as reduce_module


# ----------------------------------------------------------------------
# Solvers
# ----------------------------------------------------------------------

def brute_sat(instance: dict) -> bool:
    Sat.validate(instance)
    m = instance["num_vars"]
    clauses = instance["clauses"]
    for bits in itertools.product([False, True], repeat=m):
        if all(
            any((lit > 0) == bits[abs(lit) - 1] for lit in clause)
            for clause in clauses
        ):
            return True
    return False


def dpll_sat(instance: dict) -> bool:
    Sat.validate(instance)
    if any(len(c) == 0 for c in instance["clauses"]):
        return False

    def solve(clauses, assign):
        clauses = [set(c) for c in clauses]
        changed = True
        while changed:
            changed = False
            for c in list(clauses):
                if len(c) == 0:
                    return False
                if len(c) == 1:
                    lit = next(iter(c))
                    var, val = abs(lit), lit > 0
                    if var in assign:
                        if assign[var] != val:
                            return False
                    else:
                        assign[var] = val
                        changed = True
                    clauses = [d for d in clauses if lit not in d]
                    for d in clauses:
                        d.discard(-lit)
        if not clauses:
            return True
        lit = next(iter(clauses[0]))
        var = abs(lit)
        for val in (True, False):
            a2 = dict(assign)
            a2[var] = val
            new = []
            for c in clauses:
                if (var if val else -var) in c:
                    continue
                new.append({x for x in c if x != (-var if val else var)})
            if solve(new, a2):
                return True
        return False

    return solve(instance["clauses"], {})


def brute_clique(instance: dict) -> bool:
    Clique.validate(instance)
    n, k = instance["n"], instance["k"]
    if k <= 0:
        return True
    if k > n:
        return False
    adj = [[False] * n for _ in range(n)]
    for u, v in instance["edges"]:
        adj[u][v] = adj[v][u] = True
    for r in range(n, k - 1, -1):
        for comb in itertools.combinations(range(n), r):
            if all(adj[a][b] for a, b in itertools.combinations(comb, 2)):
                return True
    return False


def max_clique_size(instance: dict) -> int:
    Clique.validate(instance)
    n = instance["n"]
    adj = [set() for _ in range(n)]
    for u, v in instance["edges"]:
        adj[u].add(v)
        adj[v].add(u)
    best = [0]

    def bk(r, p, x):
        if not p and not x:
            best[0] = max(best[0], len(r))
            return
        if len(r) + len(p) <= best[0]:
            return
        for v in list(p):
            bk(r | {v}, p & adj[v], x & adj[v])
            p = p - {v}
            x = x | {v}

    bk(set(), set(range(n)), set())
    return best[0]


def clique_ge(instance: dict) -> bool:
    Clique.validate(instance)
    k = instance["k"]
    if k <= 0:
        return True
    if k > instance["n"]:
        return False
    return max_clique_size(instance) >= k


# ----------------------------------------------------------------------
# Generators
# ----------------------------------------------------------------------

def make_instance(num_vars, clauses):
    return {"num_vars": num_vars, "clauses": [list(c) for c in clauses]}


def clause_pool(num_vars):
    lits = [v for v in range(1, num_vars + 1)] + [-v for v in range(1, num_vars + 1)]
    pool = [[]]
    for size in (1, 2, 3):
        for combo in itertools.combinations(lits, size):
            pool.append(list(combo))
    if num_vars >= 1:
        pool += [[1, 1], [-1, -1], [1, -1], [1, 1, -1], [1, -1, -1]]
    if num_vars >= 2:
        pool += [[1, 2, 2], [-1, -2, 1], [1, -1, 2, -2]]
    seen, out = set(), []
    for c in pool:
        key = tuple(sorted(c))
        if key not in seen:
            seen.add(key)
            out.append(c)
    return out


def gen_exhaustive_small():
    instances = []
    for m in range(0, 3):
        pool = clause_pool(m)
        for r in range(0, 4):
            for combo in itertools.product(pool, repeat=r):
                instances.append(make_instance(m, combo))
    return instances


def gen_random(count, seed, max_m, max_c, max_len):
    rng = random.Random(seed)
    out = []
    for _ in range(count):
        m = rng.randint(0, max_m)
        lits = [v for v in range(1, m + 1)] + [-v for v in range(1, m + 1)]
        clauses = []
        for _ in range(rng.randint(0, max_c)):
            size = rng.randint(0, max_len)
            clauses.append([rng.choice(lits) for _ in range(size)] if lits else [])
        out.append(make_instance(m, clauses))
    return out


# ----------------------------------------------------------------------
# Driver
# ----------------------------------------------------------------------

def run():
    tests_run = 0
    tests_passed = 0
    failures = []

    def check(inst, sat_solver, clique_solver):
        nonlocal tests_run, tests_passed
        tests_run += 1
        try:
            expected = sat_solver(inst)
            reduced = reduce_module.reduce(inst)
            # must be a well-formed Clique instance with the right keys
            assert set(reduced) == {"n", "edges", "k"}, reduced.keys()
            Clique.validate(reduced)
            got = clique_solver(reduced)
            if expected == got:
                tests_passed += 1
            else:
                failures.append((inst, expected, reduced, got))
        except Exception as exc:  # noqa: BLE001
            failures.append((inst, "EXCEPTION", repr(exc), None))

    # 1) exhaustive tiny formulas (brute force both sides)
    for inst in gen_exhaustive_small():
        check(inst, brute_sat, brute_clique)

    # 2) random small formulas (brute force both sides)
    for inst in gen_random(4000, 12345, max_m=4, max_c=5, max_len=4):
        check(inst, brute_sat, brute_clique)

    # 3) random larger formulas (DPLL + max-clique)
    for inst in gen_random(20000, 999, max_m=8, max_c=6, max_len=4):
        check(inst, dpll_sat, clique_ge)

    # 4) explicit edge cases
    edge_cases = [
        make_instance(0, []),
        make_instance(0, [[]]),
        make_instance(3, []),
        make_instance(3, [[]]),
        make_instance(1, [[1], [-1]]),
        make_instance(1, [[1, -1]]),
        make_instance(2, [[1], [2]]),
        make_instance(2, [[1], [-1], [2]]),
        make_instance(2, [[1, 2], [-1, 2], [1, -2], [-1, -2]]),
        make_instance(2, [[1, 2], [-1, 2], [1, -2]]),
        make_instance(1, [[1, 1]]),
        make_instance(1, [[1, -1, 1]]),
    ]
    for inst in edge_cases:
        check(inst, brute_sat, brute_clique)

    # 5) reduce must not mutate its input
    inst = make_instance(2, [[1, 2], [-1, 2]])
    snap = {"num_vars": 2, "clauses": [[1, 2], [-1, 2]]}
    reduce_module.reduce(inst)
    tests_run += 1
    if inst == snap:
        tests_passed += 1
    else:
        failures.append((inst, "MUTATED", snap, None))

    # 6) polynomial-time sanity on a larger instance
    big = make_instance(7, [[(i % 7) + 1, -(((i + 3) % 7) + 1)] for i in range(300)])
    t0 = time.time()
    reduce_module.reduce(big)
    dt = time.time() - t0
    tests_run += 1
    if dt < 5.0:
        tests_passed += 1
    else:
        failures.append((big, "TOO_SLOW", dt, None))

    print(f"tests_run={tests_run} tests_passed={tests_passed}")
    if failures:
        print(f"FAILURES: {len(failures)}")
        for f in failures[:10]:
            print("  ", f)
    else:
        print("ALL TESTS PASSED")
    return tests_run, tests_passed, failures


if __name__ == "__main__":
    run()
