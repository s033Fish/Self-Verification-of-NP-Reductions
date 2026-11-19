"""Independent tests for reduce.py: 3-SAT -> Dominating Set.

We implement our own brute-force solvers for both problems directly from the
definitions in problems.py, then compare the answers of many small source
instances with the answers of their reductions.

The reduction is expected to satisfy: answer(source) == answer(reduce(source))
for every valid source instance, and reduce must not crash or call a solver.
"""

from __future__ import annotations

import itertools
import json
import random

from problems import ThreeSat, DominatingSet
from reduce import reduce


# ----------------------------------------------------------------------
# Brute-force solvers written from the problem definitions.

def brute_sat(instance):
    """Return True iff the 3-SAT instance is satisfiable."""
    ThreeSat.validate(instance)
    m = instance["num_vars"]
    clauses = instance["clauses"]
    for bits in itertools.product([False, True], repeat=m):
        good = True
        for clause in clauses:
            sat = False
            for lit in clause:
                val = bits[abs(lit) - 1]
                if (lit > 0 and val) or (lit < 0 and not val):
                    sat = True
                    break
            if not sat:
                good = False
                break
        if good:
            return True
    return False


def brute_ds(instance):
    """Return True iff the graph has a dominating set of size at most k."""
    DominatingSet.validate(instance)
    n = instance["n"]
    edges = instance["edges"]
    k = instance["k"]
    if k < 0:
        return False
    if k >= n:
        return True
    adj = [set() for _ in range(n)]
    for u, v in edges:
        adj[u].add(v)
        adj[v].add(u)
    for size in range(0, k + 1):
        for comb in itertools.combinations(range(n), size):
            dominated = set(comb)
            for v in comb:
                dominated |= adj[v]
            if len(dominated) == n:
                return True
    return False


def ds_witness(instance):
    """Return a dominating set of size <= k, or None."""
    n, edges, k = instance["n"], instance["edges"], instance["k"]
    if k < 0:
        return None
    adj = [set() for _ in range(n)]
    for u, v in edges:
        adj[u].add(v)
        adj[v].add(u)
    for size in range(0, min(k, n) + 1):
        for comb in itertools.combinations(range(n), size):
            dominated = set(comb)
            for v in comb:
                dominated |= adj[v]
            if len(dominated) == n:
                return comb
    return None


# ----------------------------------------------------------------------
# Instance generation.

def all_clauses(m):
    """All valid 3-literal clauses over variables 1..m."""
    clauses = []
    for vars_ in itertools.combinations(range(1, m + 1), 3):
        for signs in itertools.product([1, -1], repeat=3):
            clauses.append([s * v for s, v in zip(signs, vars_)])
    return clauses


def random_instance(rng, m, max_clauses):
    pool = all_clauses(m)
    if not pool:
        return {"num_vars": m, "clauses": []}
    c = rng.randint(0, max_clauses)
    return {"num_vars": m, "clauses": [list(rng.choice(pool)) for _ in range(c)]}


# ----------------------------------------------------------------------
# Test driver.

def main():
    rng = random.Random(20240517)
    tests_run = 0
    tests_passed = 0
    failures = []

    def check(inst, label=""):
        nonlocal tests_run, tests_passed
        tests_run += 1
        src_ans = brute_sat(inst)
        try:
            red = reduce(inst)
        except Exception as exc:  # reduction must not crash on valid input
            failures.append((label, inst, "reduce raised %r" % (exc,)))
            return
        try:
            DominatingSet.validate(red)
        except Exception as exc:
            failures.append((label, inst, "invalid target: %r" % (exc,)))
            return
        tgt_ans = brute_ds(red)
        if src_ans == tgt_ans:
            tests_passed += 1
        else:
            failures.append((label, inst, src_ans, tgt_ans, red))

    # 1) Edge cases: no clauses, small m (m=0,1,2 are only valid clause-free).
    for m in (0, 1, 2, 3):
        check({"num_vars": m, "clauses": []}, "empty-clauses m=%d" % m)

    # 2) Exhaustive over all 256 formulas with m = 3.
    pool3 = all_clauses(3)
    for r in range(len(pool3) + 1):
        for subset in itertools.combinations(range(len(pool3)), r):
            check({"num_vars": 3, "clauses": [list(pool3[i]) for i in subset]},
                  "exhaustive m=3")

    # 3) Known unsatisfiable formulas.
    known_unsat = [
        {"num_vars": 3,
         "clauses": [[s1 * 1, s2 * 2, s3 * 3]
                     for s1 in (1, -1) for s2 in (1, -1) for s3 in (1, -1)]},
        {"num_vars": 3,
         "clauses": [[1, 2, 3], [1, 2, -3], [1, -2, 3], [-1, 2, 3], [-1, -2, -3]]},
    ]
    for inst in known_unsat:
        check(inst, "known unsat")

    # 4) Explicit counterexample found during review: unsatisfiable 4-var
    #    formula whose reduction nevertheless has a dominating set of size 4
    #    (witness {3_T, 3_F, clause_1, clause_8}).
    counterexample = {
        "num_vars": 4,
        "clauses": [
            [-2, 3, -4], [1, 2, 4], [1, -3, -4], [-1, 2, 3], [-2, -3, 4],
            [-1, 2, -3], [-2, 3, 4], [1, 2, 3], [-1, -2, -4],
        ],
    }
    check(counterexample, "explicit counterexample")
    # Sanity-check the counterexample itself independently.
    assert brute_sat(counterexample) is False
    assert brute_ds(reduce(counterexample)) is True
    assert ds_witness(reduce(counterexample)) is not None

    # 5) Random formulas for m = 4 and 5.  Denser m=4 formulas are used
    #    because that is where the reduction's argument breaks down.
    for _ in range(4000):
        c = rng.randint(0, 16)
        pool = all_clauses(4)
        inst = {"num_vars": 4,
                "clauses": [list(rng.choice(pool)) for _ in range(c)]}
        check(inst, "random m=4")
    for _ in range(500):
        check(random_instance(rng, 5, max_clauses=8), "random m=5")

    # 6) Duplicated clauses.
    for _ in range(300):
        m = rng.randint(3, 5)
        inst = random_instance(rng, m, max_clauses=6)
        if inst["clauses"]:
            inst["clauses"].append(list(rng.choice(inst["clauses"])))
        check(inst, "duplicated clauses")

    print("tests_run    =", tests_run)
    print("tests_passed =", tests_passed)
    print("failures     =", len(failures))
    for f in failures[:5]:
        print("FAILURE:", f[0], "src_ans/tgt_ans =", f[2:4] if len(f) >= 4 else f[2:])
        if len(f) >= 5:
            print("   instance:", f[1])

    verified = (tests_run > 0) and (tests_run == tests_passed)
    verdict = {"verified": bool(verified), "tests_run": tests_run,
               "tests_passed": tests_passed}
    with open("verdict.json", "w") as fh:
        json.dump(verdict, fh)
    print("verdict:", verdict)


if __name__ == "__main__":
    main()
