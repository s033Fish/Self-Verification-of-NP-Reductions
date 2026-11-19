"""Independent checks for reduce.py: 3-SAT -> Clique.

We implement our own brute-force solvers for both problems from the
docstring definitions, generate many small valid source instances, reduce
them, and compare the answers.  We also check the documented edge cases and
that reduce does not blow up (polynomial-ish) on a larger instance.
"""

import itertools
import json
import random
import time

from problems import SOURCE, TARGET, InvalidInstance
from reduce import reduce


# ----------------------------------------------------------------------
# Brute-force solvers written from the problem definitions.

def solve_three_sat(instance):
    """Return True iff the 3-SAT instance is satisfiable.

    Instance: {"num_vars": m, "clauses": [[l1,l2,l3], ...]}
    Variables 1..m.  A literal +v is true iff v is assigned True.
    """
    m = instance["num_vars"]
    clauses = instance["clauses"]
    for bits in range(1 << m):
        # variable v (1..m) true iff bit (v-1) set
        ok = True
        for clause in clauses:
            sat = False
            for lit in clause:
                v = abs(lit)
                val = (bits >> (v - 1)) & 1
                if (lit > 0 and val == 1) or (lit < 0 and val == 0):
                    sat = True
                    break
            if not sat:
                ok = False
                break
        if ok:
            return True
    return False


def solve_clique(instance):
    """Return True iff the graph has a clique of size AT LEAST k."""
    n = instance["n"]
    k = instance["k"]
    if k <= 0:
        return True
    if k > n:
        return False
    adj = [[False] * n for _ in range(n)]
    for u, v in instance["edges"]:
        adj[u][v] = True
        adj[v][u] = True
    # brute force: try every subset of size k (and larger, but >= k suffices)
    for size in range(k, n + 1):
        for subset in itertools.combinations(range(n), size):
            good = True
            for a, b in itertools.combinations(subset, 2):
                if not adj[a][b]:
                    good = False
                    break
            if good:
                return True
    return False


# ----------------------------------------------------------------------
# Instance generation

def random_three_sat(rng, max_vars=4, max_clauses=5):
    m = rng.randint(0, max_vars)
    nclauses = rng.randint(0, max_clauses)
    clauses = []
    for _ in range(nclauses):
        if m < 3:
            # cannot form a valid clause; skip (only valid when m >= 3)
            continue
        vs = rng.sample(range(1, m + 1), 3)
        clause = [v if rng.random() < 0.5 else -v for v in vs]
        clauses.append(clause)
    return {"num_vars": m, "clauses": clauses}


def all_small_three_sat():
    """Exhaustively enumerate small valid 3-SAT instances."""
    out = []
    # m in 0..3, clauses drawn from all possible clauses over 1..m (m>=3)
    for m in range(0, 4):
        if m < 3:
            out.append({"num_vars": m, "clauses": []})
            continue
        literals = [v for v in range(1, m + 1)] + [-v for v in range(1, m + 1)]
        # all clauses: choose 3 distinct variables, then signs
        possible = []
        for vs in itertools.combinations(range(1, m + 1), 3):
            for signs in itertools.product([1, -1], repeat=3):
                possible.append([s * v for s, v in zip(signs, vs)])
        # all subsets of size 0..2 of possible clauses
        for r in range(0, 3):
            for combo in itertools.combinations(possible, r):
                out.append({"num_vars": m, "clauses": [list(c) for c in combo]})
    return out



def dpll_sat(instance):
    """Independent SAT solver via recursive DPLL (cross-check)."""
    clauses = [tuple(c) for c in instance["clauses"]]

    def simplify(clauses, var, val):
        out = []
        for c in clauses:
            if (var if val else -var) in c:
                continue
            out.append(tuple(l for l in c if l != (-var if val else var)))
        return out

    def rec(clauses):
        if not clauses:
            return True
        if any(len(c) == 0 for c in clauses):
            return False
        for c in clauses:
            if len(c) == 1:
                lit = c[0]
                return rec(simplify(clauses, abs(lit), lit > 0))
        lit = clauses[0][0]
        return rec(simplify(clauses, abs(lit), lit > 0)) or \
               rec(simplify(clauses, abs(lit), lit < 0))

    return rec(clauses)


def exhaustive_m3():
    m = 3
    possible = []
    for vs in itertools.combinations(range(1, m + 1), 3):
        for signs in itertools.product([1, -1], repeat=3):
            possible.append([s * v for s, v in zip(signs, vs)])
    out = []
    for mask in range(1 << len(possible)):
        out.append({"num_vars": m,
                    "clauses": [list(possible[i]) for i in range(len(possible))
                                if mask >> i & 1]})
    return out


# ----------------------------------------------------------------------
# Test driver

def main():
    tests_run = 0
    tests_passed = 0
    failures = []

    def check(name, condition, detail=""):
        nonlocal tests_run, tests_passed
        tests_run += 1
        if condition:
            tests_passed += 1
        else:
            failures.append((name, detail))

    # 1. Exhaustive small instances.
    for inst in all_small_three_sat():
        SOURCE.validate(inst)
        src = solve_three_sat(inst)
        red = reduce(inst)
        try:
            TARGET.validate(red)
            valid = True
        except InvalidInstance as e:
            valid = False
            detail = f"invalid reduction {red!r}: {e}"
        if not valid:
            check("exhaustive-valid", False, detail)
            continue
        tgt = solve_clique(red)
        check(
            "exhaustive",
            src == tgt,
            f"inst={inst} src={src} red={red} tgt={tgt}",
        )

    # 2. Random instances.
    rng = random.Random(12345)
    for _ in range(3000):
        inst = random_three_sat(rng, max_vars=5, max_clauses=6)
        SOURCE.validate(inst)
        src = solve_three_sat(inst)
        red = reduce(inst)
        try:
            TARGET.validate(red)
            valid = True
        except InvalidInstance as e:
            valid = False
            detail = f"invalid reduction {red!r}: {e}"
        if not valid:
            check("random-valid", False, detail)
            continue
        tgt = solve_clique(red)
        check(
            "random",
            src == tgt,
            f"inst={inst} src={src} red={red} tgt={tgt}",
        )

    # 3. Explicit edge cases.
    edge_cases = [
        {"num_vars": 0, "clauses": []},
        {"num_vars": 5, "clauses": []},
        {"num_vars": 3, "clauses": [[1, 2, 3]]},
        {"num_vars": 3, "clauses": [[1, 2, 3], [1, 2, 3]]},
        {"num_vars": 3, "clauses": [[-1, -2, -3]]},
        {"num_vars": 3, "clauses": [[1, 2, 3], [-1, -2, -3]]},
        {"num_vars": 3, "clauses": [[1, 2, 3], [-1, -2, -3], [1, -2, 3]]},
        # unsatisfiable: all 8 clauses over 3 vars
        {
            "num_vars": 3,
            "clauses": [
                [1, 2, 3], [1, 2, -3], [1, -2, 3], [1, -2, -3],
                [-1, 2, 3], [-1, 2, -3], [-1, -2, 3], [-1, -2, -3],
            ],
        },
    ]
    for inst in edge_cases:
        SOURCE.validate(inst)
        src = solve_three_sat(inst)
        red = reduce(inst)
        TARGET.validate(red)
        tgt = solve_clique(red)
        check("edge", src == tgt, f"inst={inst} src={src} red={red} tgt={tgt}")

    # 4. Sanity: reduction of empty formula is a yes target instance.
    red0 = reduce({"num_vars": 0, "clauses": []})
    check("empty-yes", solve_clique(red0) is True, f"red={red0}")

    # 5. Polynomial-time sanity: large instance should reduce quickly.
    rng = random.Random(7)
    big = {"num_vars": 200, "clauses": []}
    for _ in range(200):
        vs = rng.sample(range(1, 201), 3)
        big["clauses"].append([v if rng.random() < 0.5 else -v for v in vs])
    SOURCE.validate(big)
    t0 = time.time()
    redbig = reduce(big)
    dt = time.time() - t0
    TARGET.validate(redbig)
    check("poly-time", dt < 5.0, f"reduction took {dt:.3f}s")
    check("poly-size", redbig["n"] == 600 and redbig["k"] == 200,
          f"n={redbig['n']} k={redbig['k']}")


    # 6. Fully exhaustive m=3: every subset of the 8 possible clauses.
    for inst in exhaustive_m3():
        SOURCE.validate(inst)
        src_ans = solve_three_sat(inst)
        red = reduce(inst)
        TARGET.validate(red)
        tgt = solve_clique(red)
        check("exhaustive-m3", src_ans == tgt,
              f"inst={inst} src={src_ans} tgt={tgt}")

    # 7. Cross-check brute force vs DPLL vs reduction on random instances.
    rng = random.Random(999)
    for _ in range(2000):
        mv = rng.randint(0, 6)
        nc = rng.randint(0, 8)
        clauses = []
        for _ in range(nc):
            if mv < 3:
                break
            vs = rng.sample(range(1, mv + 1), 3)
            clauses.append([v if rng.random() < 0.5 else -v for v in vs])
        inst = {"num_vars": mv, "clauses": clauses}
        SOURCE.validate(inst)
        a = solve_three_sat(inst)
        b = dpll_sat(inst)
        red = reduce(inst)
        TARGET.validate(red)
        c = solve_clique(red)
        check("cross-check", a == b == c,
              f"inst={inst} brute={a} dpll={b} clique={c}")

    print(f"tests_run={tests_run} tests_passed={tests_passed}")
    if failures:
        print("FAILURES:")
        for name, detail in failures[:20]:
            print(" ", name, detail)
    verified = tests_passed == tests_run and tests_run > 0
    with open("verdict.json", "w") as f:
        json.dump({"verified": verified, "tests_run": tests_run,
                   "tests_passed": tests_passed}, f, indent=2)
    print("verified =", verified)


if __name__ == "__main__":
    main()
