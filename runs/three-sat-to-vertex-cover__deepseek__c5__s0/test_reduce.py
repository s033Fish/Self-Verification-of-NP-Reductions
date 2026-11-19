"""Independent tests for reduce.py (3-SAT -> Vertex Cover).

We implement brute-force solvers for both problems directly from the
definitions in problems.py, then compare answers on many small instances.

Run:  python3 test_reduce.py
"""

from __future__ import annotations

import itertools
import random
import sys

import problems
import reduce as reduce_mod


# ----------------------------------------------------------------------
# Brute-force solvers (written independently from the definitions)
# ----------------------------------------------------------------------

def solve_three_sat(instance: dict) -> bool:
    """Brute force: try all 2^m assignments."""
    m = instance["num_vars"]
    clauses = instance["clauses"]
    for bits in range(1 << m):
        # variable v (1..m) is true iff bit (v-1) is set
        ok = True
        for clause in clauses:
            clause_true = False
            for lit in clause:
                var = abs(lit)
                val = bool((bits >> (var - 1)) & 1)
                if (lit > 0 and val) or (lit < 0 and not val):
                    clause_true = True
                    break
            if not clause_true:
                ok = False
                break
        if ok:
            return True
    return False


def min_vertex_cover(n: int, edges: list) -> int:
    """Exact minimum vertex cover size via branching + memoization.

    Correct because for any edge (u, v), some minimum vertex cover contains
    u or v; branch on both and recurse on the graph with that vertex removed.
    """
    edge_set = frozenset(frozenset(e) for e in edges)
    memo: dict = {}

    def rec(es: frozenset) -> int:
        if not es:
            return 0
        if es in memo:
            return memo[es]
        e = next(iter(es))
        u, v = tuple(e)
        rem_u = frozenset(x for x in es if u not in x)
        rem_v = frozenset(x for x in es if v not in x)
        res = 1 + min(rec(rem_u), rec(rem_v))
        memo[es] = res
        return res

    return rec(edge_set)


def solve_vertex_cover(instance: dict) -> bool:
    """Yes iff there is a vertex cover of size at most k."""
    n = instance["n"]
    k = instance["k"]
    if k < 0:
        return False
    if not instance["edges"]:
        return k >= 0
    return min_vertex_cover(n, instance["edges"]) <= k


# ----------------------------------------------------------------------
# Instance generation
# ----------------------------------------------------------------------

def random_three_sat(rng: random.Random, max_m: int = 4, max_c: int = 4) -> dict:
    m = rng.randint(0, max_m)
    if m < 3:
        # clauses require m >= 3; keep it clause-free
        c = 0
    else:
        c = rng.randint(0, max_c)
    clauses = []
    for _ in range(c):
        vs = rng.sample(range(1, m + 1), 3)
        clause = [v if rng.random() < 0.5 else -v for v in vs]
        clauses.append(clause)
    return {"num_vars": m, "clauses": clauses}


def all_three_sat_small() -> list:
    """Exhaustive-ish small instances: m in 0..3, all clause subsets over a
    fixed literal pool, plus some m=4 random-ish structured ones."""
    instances = []
    # m = 0,1,2 : only empty clause list is valid
    for m in range(0, 3):
        instances.append({"num_vars": m, "clauses": []})
    # m = 3 : enumerate all possible clauses (3 vars, 2^3 sign patterns = 8),
    # then all subsets of size 0..2 (size 3 would be 8 choose 3 = 56, fine too)
    all_clauses = []
    for signs in itertools.product([1, -1], repeat=3):
        all_clauses.append([s * v for s, v in zip(signs, (1, 2, 3))])
    for r in range(0, 4):
        for combo in itertools.combinations(all_clauses, r):
            instances.append({"num_vars": 3, "clauses": [list(c) for c in combo]})
    # m = 4 : include clauses over subsets of variables, a handful
    pool = []
    for vs in itertools.combinations(range(1, 5), 3):
        for signs in itertools.product([1, -1], repeat=3):
            pool.append([s * v for s, v in zip(signs, vs)])
    rng = random.Random(12345)
    for _ in range(300):
        r = rng.randint(0, 4)
        clauses = [list(c) for c in rng.sample(pool, r)]
        instances.append({"num_vars": 4, "clauses": clauses})
    return instances


# ----------------------------------------------------------------------
# Test driver
# ----------------------------------------------------------------------

def main() -> int:
    tests_run = 0
    tests_passed = 0
    failures = []

    def check(cond: bool, msg: str) -> None:
        nonlocal tests_run, tests_passed
        tests_run += 1
        if cond:
            tests_passed += 1
        else:
            failures.append(msg)

    # 1. reduce.py imports and is callable.
    check(callable(getattr(reduce_mod, "reduce", None)),
          "reduce.py must define a callable reduce")

    rng = random.Random(987654321)
    instances = all_three_sat_small()
    instances += [random_three_sat(rng) for _ in range(2000)]

    for idx, inst in enumerate(instances):
        # source instance must itself be valid
        try:
            problems.SOURCE.validate(inst)
        except Exception as exc:  # pragma: no cover
            check(False, f"generated source instance {idx} invalid: {exc}")
            continue

        try:
            out = reduce_mod.reduce(inst)
        except Exception as exc:
            check(False, f"reduce raised on instance {idx}: {inst!r}: {exc}")
            continue

        # target instance must be valid
        try:
            problems.TARGET.validate(out)
            check(True, "")
        except Exception as exc:
            check(False, f"reduce output invalid on {inst!r}: {out!r}: {exc}")
            continue

        src_ans = solve_three_sat(inst)
        tgt_ans = solve_vertex_cover(out)
        check(src_ans == tgt_ans,
              f"mismatch on {inst!r}: source={src_ans} target={tgt_ans} out={out!r}")

    # 2. Explicit edge cases.
    explicit = [
        {"num_vars": 0, "clauses": []},
        {"num_vars": 5, "clauses": []},
        # unsatisfiable: all 8 clauses over 3 vars
        {"num_vars": 3, "clauses": [
            [1, 2, 3], [1, 2, -3], [1, -2, 3], [1, -2, -3],
            [-1, 2, 3], [-1, 2, -3], [-1, -2, 3], [-1, -2, -3]]},
        # duplicate clauses
        {"num_vars": 3, "clauses": [[1, 2, 3], [1, 2, 3]]},
        # variable not appearing
        {"num_vars": 6, "clauses": [[1, 2, 3]]},
    ]
    for inst in explicit:
        problems.SOURCE.validate(inst)
        out = reduce_mod.reduce(inst)
        problems.TARGET.validate(out)
        src_ans = solve_three_sat(inst)
        tgt_ans = solve_vertex_cover(out)
        check(src_ans == tgt_ans,
              f"explicit mismatch on {inst!r}: source={src_ans} target={tgt_ans} out={out!r}")

    # 3. Sanity: the brute-force vertex cover solver itself on known cases.
    check(solve_vertex_cover({"n": 0, "edges": [], "k": 0}) is True, "empty graph k=0")
    check(solve_vertex_cover({"n": 0, "edges": [], "k": -1}) is False, "empty graph k=-1")
    check(solve_vertex_cover({"n": 2, "edges": [[0, 1]], "k": 0}) is False, "single edge k=0")
    check(solve_vertex_cover({"n": 2, "edges": [[0, 1]], "k": 1}) is True, "single edge k=1")
    check(solve_vertex_cover({"n": 3, "edges": [[0, 1], [1, 2], [0, 2]], "k": 1}) is False, "triangle k=1")
    check(solve_vertex_cover({"n": 3, "edges": [[0, 1], [1, 2], [0, 2]], "k": 2}) is True, "triangle k=2")

    # 4. Cross-check min_vertex_cover against a naive combinations brute force.
    def naive_min_vc(n, edges):
        for k in range(n + 1):
            for comb in itertools.combinations(range(n), k):
                s = set(comb)
                if all(u in s or v in s for u, v in edges):
                    return k
        return n

    rng2 = random.Random(1)
    for _ in range(1500):
        n = rng2.randint(0, 7)
        all_edges = list(itertools.combinations(range(n), 2))
        edges = [list(e) for e in all_edges if rng2.random() < 0.5]
        a = min_vertex_cover(n, edges)
        b = naive_min_vc(n, edges)
        check(a == b, f"min_vertex_cover mismatch n={n} edges={edges}: {a} vs {b}")

    # 5. Larger random 3-SAT instances.
    rng3 = random.Random(42)
    for _ in range(2000):
        m = rng3.randint(3, 8)
        c = rng3.randint(0, 6)
        vs_pool = [rng3.sample(range(1, m + 1), 3) for _ in range(c)]
        inst = {"num_vars": m,
                "clauses": [[v if rng3.random() < 0.5 else -v for v in vs]
                            for vs in vs_pool]}
        problems.SOURCE.validate(inst)
        out = reduce_mod.reduce(inst)
        problems.TARGET.validate(out)
        check(solve_three_sat(inst) == solve_vertex_cover(out),
              f"larger mismatch on {inst!r}")

    # 6. Structural / polynomial-size checks.
    rng4 = random.Random(7)
    for _ in range(200):
        m = rng4.randint(0, 20)
        c = rng4.randint(0, 20) if m >= 3 else 0
        if m >= 3:
            clauses = []
            for _ in range(c):
                vs = rng4.sample(range(1, m + 1), 3)
                clauses.append([v if rng4.random() < 0.5 else -v for v in vs])
            inst = {"num_vars": m, "clauses": clauses}
        else:
            inst = {"num_vars": m, "clauses": []}
        out = reduce_mod.reduce(inst)
        check(out["n"] == 2 * m + 3 * c and out["k"] == m + 2 * c
              and len(out["edges"]) == m + 6 * c,
              f"structure mismatch for m={m} c={c}: {out}")

    print(f"tests_run={tests_run} tests_passed={tests_passed}")
    if failures:
        print("FAILURES:")
        for f in failures[:20]:
            print("  -", f)
        return 1
    print("ALL TESTS PASSED")
    return 0


if __name__ == "__main__":
    sys.exit(main())
