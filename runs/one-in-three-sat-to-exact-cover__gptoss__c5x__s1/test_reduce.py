"""Independent tests for reduce.py (OneInThreeSat -> ExactCover).

We implement our own brute-force solvers from the problem definitions, then
compare answers on many small source instances.  We also check the explicit
task requirement that reduce() runs in polynomial time and does not call a
brute-force solver.
"""

import itertools
import random
import time

from problems import OneInThreeSat, ExactCover
from reduce import reduce


# ----------------------------------------------------------------------
# Our own brute-force solvers (independent of reduce.py)
# ----------------------------------------------------------------------

def solve_one_in_three_sat(instance):
    """Yes iff some assignment makes exactly one variable true per clause."""
    m = instance["num_vars"]
    clauses = instance["clauses"]
    for bits in itertools.product([False, True], repeat=m):
        ok = True
        for clause in clauses:
            if sum(1 for v in clause if bits[v - 1]) != 1:
                ok = False
                break
        if ok:
            return True
    return False


def solve_exact_cover(instance):
    """Yes iff some sub-collection is pairwise disjoint and covers universe."""
    u = instance["universe_size"]
    sets = instance["sets"]
    target = (1 << u) - 1
    n = len(sets)
    for mask in range(1 << n):
        union = 0
        good = True
        for i in range(n):
            if mask & (1 << i):
                s = 0
                for e in sets[i]:
                    s |= 1 << e
                if union & s:          # overlap -> not disjoint
                    good = False
                    break
                union |= s
        if good and union == target:
            return True
    return False


# ----------------------------------------------------------------------
# Instance generators
# ----------------------------------------------------------------------

def random_source_instance(rng, max_vars=6, max_clauses=5):
    m = rng.randint(0, max_vars)
    nclauses = rng.randint(0, max_clauses)
    clauses = []
    if m >= 3:
        for _ in range(nclauses):
            clauses.append(rng.sample(range(1, m + 1), 3))
    return {"num_vars": m, "clauses": clauses}


def all_small_source_instances():
    """Exhaustive-ish enumeration of tiny instances."""
    instances = []
    for m in range(0, 5):
        instances.append({"num_vars": m, "clauses": []})
    for m in range(3, 5):
        for clause in itertools.combinations(range(1, m + 1), 3):
            instances.append({"num_vars": m, "clauses": [list(clause)]})
    for m in range(3, 5):
        clauses = [list(c) for c in itertools.combinations(range(1, m + 1), 3)]
        for c1 in clauses:
            for c2 in clauses:
                instances.append({"num_vars": m, "clauses": [list(c1), list(c2)]})
    return instances


# ----------------------------------------------------------------------
# Test harness
# ----------------------------------------------------------------------

results = []
test_counter = {"run": 0, "passed": 0}


def record(ok):
    test_counter["run"] += 1
    if ok:
        test_counter["passed"] += 1


def check(name, condition):
    results.append((name, bool(condition)))
    print(("PASS" if condition else "FAIL"), name)


def main():
    rng = random.Random(12345)

    # 1. Exhaustive small instances: answers must match.
    exhaustive = all_small_source_instances()
    mismatches = []
    for inst in exhaustive:
        OneInThreeSat.validate(inst)
        expected = solve_one_in_three_sat(inst)
        reduced = reduce(inst)
        ExactCover.validate(reduced)
        got = solve_exact_cover(reduced)
        record(expected == got)
        if expected != got:
            mismatches.append((inst, expected, reduced, got))
    check("exhaustive small instances match (%d cases)" % len(exhaustive),
          not mismatches)
    for mm in mismatches[:5]:
        print("  MISMATCH:", mm)

    # 2. Random instances: answers must match.
    random_mismatches = []
    N_RANDOM = 400
    for _ in range(N_RANDOM):
        inst = random_source_instance(rng)
        OneInThreeSat.validate(inst)
        expected = solve_one_in_three_sat(inst)
        reduced = reduce(inst)
        ExactCover.validate(reduced)
        got = solve_exact_cover(reduced)
        record(expected == got)
        if expected != got:
            random_mismatches.append((inst, expected, reduced, got))
    check("random instances match (%d cases)" % N_RANDOM, not random_mismatches)
    for mm in random_mismatches[:5]:
        print("  MISMATCH:", mm)

    # 3. reduce() must return a valid ExactCover instance.
    valid = True
    for inst in exhaustive:
        try:
            ExactCover.validate(reduce(inst))
            record(True)
        except Exception:
            valid = False
            record(False)
            break
    check("reduce output always validates as ExactCover", valid)

    # 4. Edge cases: m = 0 / no clauses (yes), and a forced-unsat formula.
    edge_ok = True
    for inst in ({"num_vars": 0, "clauses": []},
                 {"num_vars": 5, "clauses": []}):
        a = solve_one_in_three_sat(inst) is True
        b = solve_exact_cover(reduce(inst)) is True
        record(a); record(b)
        if not (a and b):
            edge_ok = False
    # single clause [1,2,3] repeated: exactly-one is satisfiable (yes)
    sat = {"num_vars": 3, "clauses": [[1, 2, 3]]}
    a = solve_exact_cover(reduce(sat)) is True
    record(a)
    if not a:
        edge_ok = False
    # clauses [1,2,3] and [1,2,4] with m=4 is unsat? (check via solver)
    unsat_candidate = {"num_vars": 4, "clauses": [[1, 2, 3], [1, 2, 4]]}
    exp = solve_one_in_three_sat(unsat_candidate)
    a = solve_exact_cover(reduce(unsat_candidate)) == exp
    record(a)
    if not a:
        edge_ok = False
    check("edge cases handled", edge_ok)

    # 5. reduce() must run in polynomial time: no 2^m blowup.
    #    A single repeated clause is unsatisfiable, forcing a brute-force
    #    solver to scan all 2^m assignments.
    def time_reduce(m):
        inst = {"num_vars": m, "clauses": [[1, 2, 3]]}
        OneInThreeSat.validate(inst)
        t0 = time.time()
        reduce(inst)
        return time.time() - t0

    times = {}
    for m in (16, 20, 24):
        times[m] = time_reduce(m)
    print("  reduce() times:", {m: round(t, 4) for m, t in times.items()})
    # Brute force doubles per variable; a polynomial reduction would be
    # essentially flat.  Require the largest to stay tiny.
    polynomial_like = times[24] < 0.2
    record(polynomial_like)
    check("reduce() runs in polynomial time (no 2^m blowup)", polynomial_like)

    # 6. Static check: reduce.py must not contain brute-force enumeration.
    with open("reduce.py") as f:
        src = f.read()
    uses_product = "itertools" in src and "product" in src
    record(not uses_product)
    check("reduce.py does not enumerate assignments (no itertools.product)",
          not uses_product)

    total = len(results)
    passed = sum(1 for _, ok in results if ok)
    print("\n%d/%d checks passed" % (passed, total))

    import json
    verdict = {
        "verified": bool(passed == total),
        "tests_run": test_counter["run"],
        "tests_passed": test_counter["passed"],
    }
    with open("verdict.json", "w") as f:
        json.dump(verdict, f, indent=2)
    print("verdict:", verdict)
    return total, passed


if __name__ == "__main__":
    main()
