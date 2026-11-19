"""Independent checks of reduce.py: 3-SAT -> Independent Set.

We implement brute-force solvers for both problems from the definitions in
problems.py, generate many small source instances, reduce them, and compare
the answers. We also check that the reduction output is a valid IndependentSet
instance and that reduce runs in polynomial time (structural checks).
"""

import itertools
import random

from problems import ThreeSat, IndependentSet, InvalidInstance
from reduce import reduce


# ----------------------------------------------------------------------
# Brute-force solvers (from the docstring definitions only)

def solve_three_sat(instance):
    """Return True iff the 3-SAT instance is satisfiable."""
    ThreeSat.validate(instance)
    m = instance["num_vars"]
    clauses = instance["clauses"]
    for bits in itertools.product([False, True], repeat=m):
        # bits[v-1] is the truth value of variable v
        ok = True
        for clause in clauses:
            if not any((lit > 0) == bits[abs(lit) - 1] for lit in clause):
                ok = False
                break
        if ok:
            return True
    return False


def solve_independent_set(instance):
    """Return True iff the graph has an independent set of size >= k."""
    IndependentSet.validate(instance)
    n = instance["n"]
    k = instance["k"]
    if k <= 0:
        return True
    if k > n:
        return False
    edges = instance["edges"]
    adj = [set() for _ in range(n)]
    for u, v in edges:
        adj[u].add(v)
        adj[v].add(u)
    # brute force over subsets of size >= k
    for size in range(k, n + 1):
        for comb in itertools.combinations(range(n), size):
            s = set(comb)
            if all(not (adj[u] & s) for u in s):
                return True
    return False


# ----------------------------------------------------------------------
# Instance generators

def random_three_sat(rng, max_vars=4, max_clauses=4):
    m = rng.randint(0, max_vars)
    nclauses = rng.randint(0, max_clauses)
    clauses = []
    for _ in range(nclauses):
        if m < 3:
            break
        vs = rng.sample(range(1, m + 1), 3)
        clause = [v if rng.random() < 0.5 else -v for v in vs]
        clauses.append(clause)
    return {"num_vars": m, "clauses": clauses}


def exhaustive_three_sat(max_vars=3, max_clauses=3):
    """Yield a systematic family of small valid instances."""
    for m in range(0, max_vars + 1):
        if m < 3:
            yield {"num_vars": m, "clauses": []}
            continue
        # all possible clauses over variables 1..m (ordered by sorted vars)
        all_clauses = []
        for vs in itertools.combinations(range(1, m + 1), 3):
            for signs in itertools.product([1, -1], repeat=3):
                all_clauses.append([s * v for s, v in zip(signs, vs)])
        # subsets of clauses up to max_clauses
        for size in range(0, max_clauses + 1):
            for combo in itertools.combinations(all_clauses, size):
                yield {"num_vars": m, "clauses": [list(c) for c in combo]}


def main():
    rng = random.Random(12345)
    tests_run = 0
    tests_passed = 0
    failures = []

    def check(instance, label):
        nonlocal tests_run, tests_passed
        tests_run += 1
        try:
            ThreeSat.validate(instance)
        except InvalidInstance as e:
            failures.append((label, "generated invalid source", instance, str(e)))
            return
        expected = solve_three_sat(instance)
        try:
            target = reduce(instance)
        except Exception as e:
            failures.append((label, "reduce raised", instance, repr(e)))
            return
        # target must be valid
        try:
            IndependentSet.validate(target)
        except InvalidInstance as e:
            failures.append((label, "invalid target", instance, str(e)))
            return
        got = solve_independent_set(target)
        if got == expected:
            tests_passed += 1
        else:
            failures.append((label, "answer mismatch",
                             instance, target, expected, got))

    # 1. systematic small instances
    for inst in exhaustive_three_sat(max_vars=3, max_clauses=2):
        check(inst, "exhaustive")

    # 2. random instances
    for _ in range(3000):
        check(random_three_sat(rng, max_vars=4, max_clauses=5), "random")

    # 3. targeted edge cases
    check({"num_vars": 0, "clauses": []}, "m=0 no clauses")
    check({"num_vars": 5, "clauses": []}, "no clauses")
    check({"num_vars": 3, "clauses": [[1, 2, 3]]}, "single clause")
    check({"num_vars": 3, "clauses": [[1, 2, 3], [1, 2, 3]]}, "duplicate clause")
    check({"num_vars": 3, "clauses": [[1, 2, 3], [-1, -2, -3]]}, "contradiction pair")
    check({"num_vars": 3, "clauses": [[1, 2, 3], [-1, 2, 3], [1, -2, 3],
                                       [1, 2, -3], [-1, -2, 3], [-1, 2, -3],
                                       [1, -2, -3], [-1, -2, -3]]}, "all 8 clauses")
    check({"num_vars": 4, "clauses": [[1, 2, 3], [2, 3, 4]]}, "shared vars")

    print(f"tests_run={tests_run} tests_passed={tests_passed}")
    if failures:
        print("FAILURES:")
        for f in failures[:20]:
            print(f)
    else:
        print("ALL PASSED")
    return tests_run, tests_passed, failures


if __name__ == "__main__":
    main()


def extra_checks():
    """More targeted checks including polynomial-time structural checks."""
    rng = random.Random(999)
    run = passed = 0
    for _ in range(4000):
        inst = random_three_sat(rng, max_vars=5, max_clauses=6)
        run += 1
        e = solve_three_sat(inst)
        t = reduce(inst)
        IndependentSet.validate(t)
        g = solve_independent_set(t)
        if e == g:
            passed += 1
        else:
            print("MISMATCH", inst, t, e, g)
    # exhaustive over m=3 with up to 3 clauses
    allc = []
    for vs in itertools.combinations([1, 2, 3], 3):
        for signs in itertools.product([1, -1], repeat=3):
            allc.append([s * v for s, v in zip(signs, vs)])
    for size in range(0, 4):
        for combo in itertools.combinations(allc, size):
            inst = {"num_vars": 3, "clauses": [list(c) for c in combo]}
            run += 1
            e = solve_three_sat(inst)
            t = reduce(inst)
            g = solve_independent_set(t)
            if e == g:
                passed += 1
            else:
                print("MISMATCH2", inst, t, e, g)
    # no-clause cases for many m
    for m in range(0, 10):
        inst = {"num_vars": m, "clauses": []}
        t = reduce(inst)
        IndependentSet.validate(t)
        run += 1
        if solve_independent_set(t) == True:
            passed += 1
    # structural: vertex count == 3 * num_clauses, k == num_clauses
    for _ in range(200):
        inst = random_three_sat(rng, max_vars=6, max_clauses=8)
        t = reduce(inst)
        run += 1
        if t["n"] == 3 * len(inst["clauses"]) and t["k"] == len(inst["clauses"]):
            passed += 1
    return run, passed
