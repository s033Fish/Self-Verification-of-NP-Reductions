"""Independent verification tests for reduce.py (3-SAT -> Independent Set).

We implement our own brute-force solvers directly from the problem
definitions in problems.py (which has no solvers), then compare the answer
of every small source instance with the answer of its reduction.
"""

from __future__ import annotations

import itertools
import json
import random
import time

from problems import ThreeSat, IndependentSet, InvalidInstance
from reduce import reduce


# ----------------------------------------------------------------------
# Brute-force solvers written from the definitions
# ----------------------------------------------------------------------

def solve_three_sat(instance):
    """Return True iff some assignment satisfies every clause."""
    ThreeSat.validate(instance)
    m = instance["num_vars"]
    clauses = instance["clauses"]
    for bits in itertools.product([False, True], repeat=m):
        # variable v (1..m) -> bits[v-1]
        ok = True
        for clause in clauses:
            if not any((bits[abs(l) - 1] if l > 0 else not bits[abs(l) - 1])
                       for l in clause):
                ok = False
                break
        if ok:
            return True
    return False


def solve_independent_set(instance):
    """Return True iff there is an independent set of size >= k."""
    IndependentSet.validate(instance)
    n = instance["n"]
    edges = instance["edges"]
    k = instance["k"]
    if k <= 0:
        return True
    if k > n:
        return False
    adj = [set() for _ in range(n)]
    for u, v in edges:
        adj[u].add(v)
        adj[v].add(u)
    # brute force over all subsets (small n only)
    for size in range(k, n + 1):
        for combo in itertools.combinations(range(n), size):
            s = set(combo)
            if all(not (adj[u] & s) for u in s):
                return True
    return False


# ----------------------------------------------------------------------
# Instance generation
# ----------------------------------------------------------------------

def random_three_sat(rng, max_vars=5, max_clauses=5, allow_empty_vars=True):
    m = rng.randint(0, max_vars)
    nclauses = rng.randint(0, max_clauses)
    clauses = []
    for _ in range(nclauses):
        if m < 3:
            break
        vars_ = rng.sample(range(1, m + 1), 3)
        clause = [v if rng.random() < 0.5 else -v for v in vars_]
        clauses.append(clause)
    return {"num_vars": m, "clauses": clauses}


def all_small_three_sat():
    """Exhaustively enumerate a structured family of small instances."""
    instances = []
    # no clauses, various m
    for m in range(0, 5):
        instances.append({"num_vars": m, "clauses": []})
    # all single clauses over variables {1,2,3} with all sign patterns
    for signs in itertools.product([1, -1], repeat=3):
        clause = [signs[0] * 1, signs[1] * 2, signs[2] * 3]
        instances.append({"num_vars": 3, "clauses": [list(clause)]})
    # all pairs of clauses over {1,2,3}
    base = []
    for signs in itertools.product([1, -1], repeat=3):
        base.append([signs[0] * 1, signs[1] * 2, signs[2] * 3])
    for c1 in base:
        for c2 in base:
            instances.append({"num_vars": 3, "clauses": [list(c1), list(c2)]})
    # duplicate clauses
    instances.append({"num_vars": 3, "clauses": [[1, 2, 3], [1, 2, 3]]})
    instances.append({"num_vars": 4, "clauses": [[1, 2, 3], [1, 2, 3], [1, 2, 3]]})
    # clauses with repeated variable patterns across clauses
    instances.append({"num_vars": 4, "clauses": [[1, 2, 3], [-1, 2, 4], [1, -2, -4]]})
    instances.append({"num_vars": 5, "clauses": [[1, 2, 3], [-1, -2, 3], [1, -2, -3], [-1, 2, -3]]})
    # unused variables
    instances.append({"num_vars": 6, "clauses": [[1, 2, 3]]})
    instances.append({"num_vars": 6, "clauses": [[4, 5, 6]]})
    return instances



def exhaustive_three_sat_families():
    """Exhaustive families: clause multisets over small variable sets."""
    out = []

    def clauses_over(vs):
        res = []
        for signs in itertools.product([1, -1], repeat=len(vs)):
            res.append([signs[i] * vs[i] for i in range(len(vs))])
        return res

    base3 = clauses_over([1, 2, 3])
    for r in range(0, 4):
        for combo in itertools.combinations_with_replacement(range(8), r):
            out.append({"num_vars": 3, "clauses": [list(base3[i]) for i in combo]})

    base4 = []
    for vs in itertools.combinations([1, 2, 3, 4], 3):
        base4.extend(clauses_over(list(vs)))
    for r in range(0, 3):
        for combo in itertools.combinations_with_replacement(range(len(base4)), r):
            out.append({"num_vars": 4, "clauses": [list(base4[i]) for i in combo]})

    base5 = []
    for vs in itertools.combinations([1, 2, 3, 4, 5], 3):
        base5.extend(clauses_over(list(vs)))
    for c in base5:
        out.append({"num_vars": 5, "clauses": [list(c)]})

    for m in range(0, 7):
        out.append({"num_vars": m, "clauses": []})
    return out

# ----------------------------------------------------------------------
# Test runner
# ----------------------------------------------------------------------

def main():
    tests_run = 0
    tests_passed = 0
    failures = []

    def check(inst):
        nonlocal tests_run, tests_passed
        tests_run += 1
        try:
            src = solve_three_sat(inst)
            tgt_inst = reduce(inst)
            IndependentSet.validate(tgt_inst)
            tgt = solve_independent_set(tgt_inst)
            if src == tgt:
                tests_passed += 1
            else:
                failures.append((inst, tgt_inst, src, tgt))
        except Exception as exc:  # noqa: BLE001
            failures.append((inst, None, "EXC", repr(exc)))

    # 1. structured exhaustive family
    for inst in all_small_three_sat():
        check(inst)

    # 1b. exhaustive families
    for inst in exhaustive_three_sat_families():
        check(inst)

    # 2. random instances
    rng = random.Random(12345)
    for _ in range(3000):
        check(random_three_sat(rng))

    # 3. random instances with more clauses / vars (still brute-forceable)
    rng2 = random.Random(999)
    for _ in range(300):
        check(random_three_sat(rng2, max_vars=6, max_clauses=6))

    # 4. explicit edge-case checks
    # empty formula
    check({"num_vars": 0, "clauses": []})
    check({"num_vars": 10, "clauses": []})
    # unsatisfiable core: all 8 clauses over 3 vars
    all8 = []
    for signs in itertools.product([1, -1], repeat=3):
        all8.append([signs[0] * 1, signs[1] * 2, signs[2] * 3])
    check({"num_vars": 3, "clauses": all8})
    # satisfiable with all 8 minus one
    check({"num_vars": 3, "clauses": all8[:-1]})

    # 5. determinism of reduce
    for _ in range(50):
        inst = random_three_sat(rng, max_vars=5, max_clauses=5)
        tests_run += 1
        if reduce(inst) == reduce(inst):
            tests_passed += 1
        else:
            failures.append((inst, None, "nondeterministic", None))

    # 6. polynomial-time sanity: a larger instance should finish fast
    big = {"num_vars": 200, "clauses": []}
    r = random.Random(7)
    for _ in range(200):
        vs = r.sample(range(1, 201), 3)
        big["clauses"].append([v if r.random() < 0.5 else -v for v in vs])
    tests_run += 1
    t0 = time.time()
    out = reduce(big)
    dt = time.time() - t0
    if out["n"] == 600 and out["k"] == 200 and dt < 5.0:
        tests_passed += 1
    else:
        failures.append((big, out, "perf", dt))

    print(f"tests_run={tests_run} tests_passed={tests_passed}")
    if failures:
        print("FAILURES:")
        for f in failures[:10]:
            print(f)
    else:
        print("All tests passed.")

    verdict = {
        "verified": len(failures) == 0,
        "tests_run": tests_run,
        "tests_passed": tests_passed,
    }
    with open("verdict.json", "w") as fh:
        json.dump(verdict, fh)
    print("verdict:", verdict)


if __name__ == "__main__":
    main()
