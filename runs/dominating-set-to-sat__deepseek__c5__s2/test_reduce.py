"""Independent tests for reduce.py (Dominating Set -> SAT).

We implement our own brute-force solvers from the problem definitions and a
DPLL solver (to reach instances whose reduction has more variables than a
2^m brute force can handle), then compare answers on many small instances.
"""
import random
from itertools import combinations, product

from problems import DominatingSet, Sat, InvalidInstance
from reduce import reduce


# --------------------------------------------------------------------------
# Solvers written from the definitions.

def solve_dominating_set(inst):
    n = inst["n"]
    edges = inst["edges"]
    k = inst["k"]
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
        for D in combinations(range(n), size):
            Ds = set(D)
            if all(v in Ds or (adj[v] & Ds) for v in range(n)):
                return True
    return False


def solve_sat_brute(inst):
    m = inst["num_vars"]
    clauses = inst["clauses"]
    for bits in product([False, True], repeat=m):
        ok = True
        for clause in clauses:
            if not any((bits[abs(l) - 1] if l > 0 else not bits[abs(l) - 1])
                       for l in clause):
                ok = False
                break
        if ok:
            return True
    return False


def solve_sat_dpll(inst):
    """DPLL with unit propagation; handles larger formulas than 2^m brute force."""
    m = inst["num_vars"]
    clauses = [set(c) for c in inst["clauses"]]
    # Simplify: drop duplicate literals, tautologies.
    norm = []
    for c in clauses:
        if any(-l in c for l in c):
            continue  # tautology
        norm.append(c)
    clauses = norm

    def simplify(clauses, assign):
        # assign: dict var -> bool
        out = []
        for c in clauses:
            newc = set()
            satisfied = False
            for l in c:
                v = abs(l)
                if v in assign:
                    if (l > 0) == assign[v]:
                        satisfied = True
                        break
                else:
                    newc.add(l)
            if satisfied:
                continue
            if not newc:
                return None  # conflict
            out.append(newc)
        return out

    def dpll(clauses, assign):
        # empty clause -> immediate conflict
        if any(len(c) == 0 for c in clauses):
            return False
        # unit propagation
        while True:
            unit = None
            for c in clauses:
                if len(c) == 1:
                    unit = next(iter(c))
                    break
            if unit is None:
                break
            assign = dict(assign)
            assign[abs(unit)] = unit > 0
            clauses = simplify(clauses, assign)
            if clauses is None:
                return False
        if not clauses:
            return True
        # pure literal elimination (optional)
        lits = set()
        for c in clauses:
            lits |= c
        pure = None
        for l in lits:
            if -l not in lits:
                pure = l
                break
        if pure is not None:
            assign = dict(assign)
            assign[abs(pure)] = pure > 0
            clauses = simplify(clauses, assign)
            if clauses is None:
                return False
            return dpll(clauses, assign)
        # branch on shortest clause
        c = min(clauses, key=len)
        lit = next(iter(c))
        for val in (True, False):
            assign2 = dict(assign)
            assign2[abs(lit)] = val
            cl2 = simplify(clauses, assign2)
            if cl2 is not None and dpll(cl2, assign2):
                return True
        return False

    return dpll(clauses, {})


def solve_sat(inst, prefer_dpll=False):
    m = inst["num_vars"]
    if prefer_dpll or m > 18:
        return solve_sat_dpll(inst)
    return solve_sat_brute(inst)


# --------------------------------------------------------------------------
# Instance generation.

def rand_graph(n, p, rng):
    edges = []
    for u in range(n):
        for v in range(u + 1, n):
            if rng.random() < p:
                edges.append([u, v])
    return edges


def all_graphs(n):
    pairs = [(u, v) for u in range(n) for v in range(u + 1, n)]
    for mask in range(1 << len(pairs)):
        yield [[u, v] for i, (u, v) in enumerate(pairs) if (mask >> i) & 1]


# --------------------------------------------------------------------------
# Tests.

TESTS_RUN = 0
TESTS_PASSED = 0


def check(cond, msg):
    global TESTS_RUN, TESTS_PASSED
    TESTS_RUN += 1
    if cond:
        TESTS_PASSED += 1
    else:
        print("FAIL:", msg)


def main():
    rng = random.Random(12345)

    # 1. Exhaustive small graphs, all k in a range, brute-force SAT compare.
    for n in range(0, 5):
        for edges in all_graphs(n):
            for k in range(-2, n + 3):
                inst = {"n": n, "edges": edges, "k": k}
                DominatingSet.validate(inst)
                red = reduce(inst)
                Sat.validate(red)  # output must be a valid SAT instance
                src = solve_dominating_set(inst)
                tgt = solve_sat_brute(red)
                check(src == tgt, f"n={n} edges={edges} k={k} src={src} red={red} tgt={tgt}")

    # 2. Random graphs up to n=8, k in 0..n-1 (cardinality encoding active),
    #    compared with DPLL.
    for _ in range(4000):
        n = rng.randint(0, 8)
        p = rng.choice([0.0, 0.15, 0.3, 0.5, 0.75, 1.0])
        edges = rand_graph(n, p, rng)
        k = rng.randint(-2, n + 1)
        inst = {"n": n, "edges": edges, "k": k}
        red = reduce(inst)
        Sat.validate(red)
        src = solve_dominating_set(inst)
        tgt = solve_sat(red, prefer_dpll=True)
        check(src == tgt, f"rand n={n} edges={edges} k={k} src={src} red={red} tgt={tgt}")

    # 3. Larger random graphs n=9..12, k around n/2, DPLL compare.
    for _ in range(800):
        n = rng.randint(9, 12)
        p = rng.choice([0.1, 0.25, 0.4, 0.6])
        edges = rand_graph(n, p, rng)
        k = rng.randint(0, n - 1)
        inst = {"n": n, "edges": edges, "k": k}
        red = reduce(inst)
        Sat.validate(red)
        src = solve_dominating_set(inst)
        tgt = solve_sat(red, prefer_dpll=True)
        check(src == tgt, f"big n={n} edges={edges} k={k} src={src} red={red} tgt={tgt}")

    # 4. Explicit edge cases from the docstrings.
    edge_cases = [
        ({"n": 0, "edges": [], "k": 0}, True),
        ({"n": 0, "edges": [], "k": 5}, True),
        ({"n": 0, "edges": [], "k": -1}, False),
        ({"n": 1, "edges": [], "k": 0}, False),   # isolated vertex must be in D
        ({"n": 1, "edges": [], "k": 1}, True),
        ({"n": 3, "edges": [], "k": 2}, False),   # 3 isolated vertices
        ({"n": 3, "edges": [], "k": 3}, True),
        ({"n": 4, "edges": [[0, 1], [2, 3]], "k": 2}, True),
        ({"n": 4, "edges": [[0, 1], [2, 3]], "k": 1}, False),
        ({"n": 5, "edges": [[0, 1], [1, 2], [2, 3], [3, 4], [4, 0]], "k": 2}, True),
        ({"n": 5, "edges": [[0, 1], [1, 2], [2, 3], [3, 4], [4, 0]], "k": 1}, False),
        ({"n": 2, "edges": [[0, 1]], "k": -3}, False),
    ]
    for inst, expected in edge_cases:
        DominatingSet.validate(inst)
        red = reduce(inst)
        Sat.validate(red)
        src = solve_dominating_set(inst)
        tgt = solve_sat(red, prefer_dpll=True)
        check(src == expected, f"edge src {inst} got {src} want {expected}")
        check(tgt == expected, f"edge tgt {inst} red={red} got {tgt} want {expected}")

    # 5. Structural checks on the reduction.
    #    - k < 0 -> unsatisfiable (contains empty clause)
    r = reduce({"n": 3, "edges": [[0, 1]], "k": -1})
    check(solve_sat(r, prefer_dpll=True) is False, "k<0 must reduce to unsat")
    #    - n = 0, k >= 0 -> no clauses -> sat
    r = reduce({"n": 0, "edges": [], "k": 0})
    check(r["clauses"] == [] and solve_sat(r) is True, "n=0 k=0 sat with no clauses")
    #    - k >= n -> only domination clauses, sat iff graph has dominating set
    r = reduce({"n": 3, "edges": [], "k": 3})
    check(solve_sat(r) is True, "k>=n always sat")
    #    - output variables are within range
    for _ in range(200):
        n = rng.randint(0, 10)
        edges = rand_graph(n, rng.choice([0.2, 0.5]), rng)
        k = rng.randint(-1, n + 1)
        red = reduce({"n": n, "edges": edges, "k": k})
        Sat.validate(red)

    # 6. Exhaustive n=5, all graphs, all k, DPLL compare (cardinality active).
    for edges in all_graphs(5):
        for k in range(-2, 7):
            inst = {"n": 5, "edges": edges, "k": k}
            red = reduce(inst)
            Sat.validate(red)
            src = solve_dominating_set(inst)
            tgt = solve_sat(red, prefer_dpll=True)
            check(src == tgt, f"exh5 edges={edges} k={k} src={src} red={red} tgt={tgt}")

    # 7. Isolated vertices: need all n selected, so yes iff k >= n.
    for n in range(1, 11):
        for k in range(0, n + 1):
            inst = {"n": n, "edges": [], "k": k}
            red = reduce(inst)
            Sat.validate(red)
            src = solve_dominating_set(inst)
            tgt = solve_sat(red, prefer_dpll=True)
            check(src == (k >= n), f"iso n={n} k={k} src={src}")
            check(tgt == (k >= n), f"iso n={n} k={k} red={red} tgt={tgt}")

    # 8. Perfect matchings: min dominating set = n/2.
    for half in range(1, 6):
        n = 2 * half
        edges = [[2 * i, 2 * i + 1] for i in range(half)]
        for k in range(0, n + 1):
            inst = {"n": n, "edges": edges, "k": k}
            red = reduce(inst)
            Sat.validate(red)
            src = solve_dominating_set(inst)
            tgt = solve_sat(red, prefer_dpll=True)
            check(src == (k >= half), f"match n={n} k={k} src={src}")
            check(tgt == (k >= half), f"match n={n} k={k} tgt={tgt}")

    # 9. Larger sparse graphs with small k, DPLL compare.
    for _ in range(300):
        n = rng.randint(13, 18)
        edges = rand_graph(n, rng.choice([0.05, 0.1, 0.2]), rng)
        k = rng.randint(0, 4)
        inst = {"n": n, "edges": edges, "k": k}
        red = reduce(inst)
        Sat.validate(red)
        src = solve_dominating_set(inst)
        tgt = solve_sat(red, prefer_dpll=True)
        check(src == tgt, f"large n={n} edges={edges} k={k} src={src} red={red} tgt={tgt}")

    # 10. Reduction output must be polynomial size (no blow-up).
    for n in [10, 20, 40]:
        edges = rand_graph(n, 0.3, rng)
        for k in [0, 1, n // 2, n - 1, n]:
            red = reduce({"n": n, "edges": edges, "k": k})
            # Sinz encoding is O(n*k); allow a generous polynomial bound.
            check(len(red["clauses"]) <= 4 * n * n + 10,
                  f"clause count blow-up n={n} k={k}: {len(red['clauses'])}")
            check(red["num_vars"] <= n * (n + 1) + 1,
                  f"var count blow-up n={n} k={k}: {red['num_vars']}")

    print(f"tests_run={TESTS_RUN} tests_passed={TESTS_PASSED}")
    return TESTS_RUN, TESTS_PASSED


if __name__ == "__main__":
    main()
