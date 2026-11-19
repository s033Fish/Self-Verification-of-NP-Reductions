"""Independent verification of reduce.py (DominatingSet -> Sat).

problems.py provides no solvers, so this file contains brute-force solvers
for both problems written directly from the definitions, plus tests that
compare the solver answers on many small source instances and their
reductions, and a check of the polynomial-time requirement.
"""
import itertools
import random
import time

from problems import DominatingSet, Sat
from reduce import reduce


# ----------------------------------------------------------------------
# Brute-force solvers written directly from the problem definitions.
# ----------------------------------------------------------------------

def ds_answer(inst):
    """Brute force: is there a dominating set of size <= k?"""
    n, edges, k = inst["n"], inst["edges"], inst["k"]
    if k < 0:
        return False
    if n == 0 or k >= n:
        return True
    adj = [set() for _ in range(n)]
    for u, v in edges:
        adj[u].add(v)
        adj[v].add(u)
    for size in range(0, k + 1):
        for D in itertools.combinations(range(n), size):
            Dset = set(D)
            if all(v in Dset or (adj[v] & Dset) for v in range(n)):
                return True
    return False


def sat_answer(inst):
    """Brute force: is the CNF formula satisfiable?"""
    m, clauses = inst["num_vars"], inst["clauses"]
    if any(len(c) == 0 for c in clauses):
        return False
    for bits in itertools.product([False, True], repeat=m):
        if all(any((bits[abs(l) - 1] if l > 0 else not bits[abs(l) - 1])
                   for l in c) for c in clauses):
            return True
    return False


# ----------------------------------------------------------------------
# Instance generators
# ----------------------------------------------------------------------

def random_ds_instance(rng, n):
    all_edges = [(u, v) for u in range(n) for v in range(u + 1, n)]
    rng.shuffle(all_edges)
    m = rng.randint(0, len(all_edges))
    edges = [list(e) for e in all_edges[:m]]
    k = rng.randint(-1, n + 1)
    return {"n": n, "edges": edges, "k": k}


def small_source_instances():
    insts = [
        {"n": 0, "edges": [], "k": 0},
        {"n": 0, "edges": [], "k": -1},
        {"n": 0, "edges": [], "k": 5},
        {"n": 1, "edges": [], "k": 0},
        {"n": 1, "edges": [], "k": -1},
        {"n": 1, "edges": [], "k": 1},
    ]
    # Exhaustive over all graphs on n = 0..4 vertices and all k.
    for n in range(0, 5):
        all_edges = [(u, v) for u in range(n) for v in range(u + 1, n)]
        for mask in range(1 << len(all_edges)):
            edges = [list(all_edges[i]) for i in range(len(all_edges)) if mask >> i & 1]
            for k in range(-1, n + 2):
                insts.append({"n": n, "edges": edges, "k": k})
    # Random larger instances (n = 5..7).
    rng = random.Random(12345)
    for _ in range(400):
        insts.append(random_ds_instance(rng, rng.randint(5, 7)))
    return insts


# ----------------------------------------------------------------------
# Tests
# ----------------------------------------------------------------------

def run():
    tests_run = 0
    tests_passed = 0
    failures = []

    # 1) Correctness: answer(reduce(I)) == answer(I) on many small instances.
    for inst in small_source_instances():
        tests_run += 1
        try:
            DominatingSet.validate(inst)
            red = reduce(inst)
            Sat.validate(red)
            expected = ds_answer(inst)
            got = sat_answer(red)
            if expected == got:
                tests_passed += 1
            else:
                failures.append(("mismatch", inst, red, expected, got))
        except Exception as exc:  # noqa: BLE001
            failures.append(("exception", inst, repr(exc)))

    # 2) Polynomial-time requirement.  The reduction builds a clause for
    #    every (k+1)-subset of vertices, i.e. C(n, k+1) clauses.  With
    #    k = n//2 this is exponential in n, so the output (and runtime)
    #    is not polynomially bounded by the input size.
    poly_details = []
    for n in (14, 16, 18, 20):
        inst = {"n": n, "edges": [], "k": n // 2}
        t0 = time.time()
        red = reduce(inst)
        dt = time.time() - t0
        nclauses = len(red["clauses"])
        expected_combos = len(list(itertools.combinations(range(n), n // 2 + 1)))
        poly_details.append((n, nclauses, expected_combos, round(dt, 3)))
        tests_run += 1
        if nclauses <= n ** 3:  # generous polynomial bound
            tests_passed += 1
        else:
            failures.append(("non-polynomial clause blowup", n, nclauses, n ** 3))

    print("correctness comparisons run:", tests_run - len(poly_details))
    print("clause-count / timing details (n, clauses, C(n,k+1), seconds):")
    for row in poly_details:
        print("   ", row)
    print("failures:")
    for f in failures[:20]:
        print("   ", f)
    print("total tests_run:", tests_run, "tests_passed:", tests_passed)
    return tests_run, tests_passed, failures


if __name__ == "__main__":
    run()
