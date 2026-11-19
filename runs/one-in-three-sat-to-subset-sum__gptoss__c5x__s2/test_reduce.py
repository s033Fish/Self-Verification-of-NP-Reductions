"""Independent tests for reduce.py (1-in-3-SAT -> Subset Sum).

We implement our own brute-force solvers from the problem definitions in
problems.py and compare their answers on many small source instances and on
the reductions produced by reduce.py.  We also check that every reduction
output is a valid SubsetSum instance and that reduce runs in polynomial time
(no brute-force search over assignments is performed by reduce itself).
"""
from __future__ import annotations

import itertools
import json
import random
import time

from problems import OneInThreeSat, SubsetSum
from reduce import reduce


# ----------------------------------------------------------------------
# Brute-force solvers written from the definitions.
# ----------------------------------------------------------------------

def solve_one_in_three_sat(instance) -> bool:
    """True iff some assignment makes exactly one var true in every clause."""
    m = instance["num_vars"]
    clauses = instance["clauses"]
    for bits in itertools.product([False, True], repeat=m):
        ok = True
        for clause in clauses:
            count = sum(1 for v in clause if bits[v - 1])
            if count != 1:
                ok = False
                break
        if ok:
            return True
    return False


def solve_subset_sum(instance) -> bool:
    """True iff some sub-list sums to exactly the target."""
    numbers = instance["numbers"]
    target = instance["target"]
    if target < 0:
        return False
    reachable = {0}
    for a in numbers:
        reachable |= {s + a for s in reachable}
    return target in reachable


# ----------------------------------------------------------------------
# Instance generation
# ----------------------------------------------------------------------

def random_one_in_three_sat(rng, max_m=8, max_clauses=6):
    m = rng.randint(0, max_m)
    clauses = []
    n_clauses = rng.randint(0, max_clauses)
    if m >= 3:
        for _ in range(n_clauses):
            clauses.append(sorted(rng.sample(range(1, m + 1), 3)))
    return {"num_vars": m, "clauses": clauses}


def edge_instances():
    yield {"num_vars": 0, "clauses": []}
    yield {"num_vars": 1, "clauses": []}
    yield {"num_vars": 2, "clauses": []}
    yield {"num_vars": 3, "clauses": [[1, 2, 3]]}
    yield {"num_vars": 3, "clauses": [[1, 2, 3], [1, 2, 3]]}
    yield {"num_vars": 3, "clauses": [[1, 2, 3], [1, 2, 3], [1, 2, 3]]}
    yield {"num_vars": 4, "clauses": [[1, 2, 3], [1, 2, 3]]}
    yield {"num_vars": 5, "clauses": [[1, 2, 3]]}
    yield {"num_vars": 4, "clauses": [[1, 2, 3], [1, 2, 4]]}
    yield {"num_vars": 4, "clauses": [[1, 2, 3], [2, 3, 4]]}
    yield {"num_vars": 5, "clauses": [[1, 2, 3], [3, 4, 5], [1, 4, 5]]}
    yield {"num_vars": 3, "clauses": [[1, 2, 3], [1, 2, 3], [1, 2, 3], [1, 2, 3]]}
    # clause order / variable order should not matter
    yield {"num_vars": 4, "clauses": [[3, 1, 2], [4, 2, 1]]}
    yield {"num_vars": 6, "clauses": [[6, 5, 4], [1, 2, 3], [2, 4, 6]]}


def main():
    tests_run = 0
    tests_passed = 0
    failures = []

    def check(inst):
        nonlocal tests_run, tests_passed
        tests_run += 1
        try:
            OneInThreeSat.validate(inst)
        except Exception as e:  # noqa: BLE001
            failures.append((inst, f"source invalid: {e}"))
            return
        expected = solve_one_in_three_sat(inst)
        try:
            out = reduce(inst)
        except Exception as e:  # noqa: BLE001
            failures.append((inst, f"reduce raised: {e}"))
            return
        try:
            SubsetSum.validate(out)
        except Exception as e:  # noqa: BLE001
            failures.append((inst, f"target invalid: {e}; out={out}"))
            return
        got = solve_subset_sum(out)
        if got != expected:
            failures.append((inst, f"expected {expected}, got {got}, out={out}"))
            return
        tests_passed += 1

    # 1) Hand-picked edge cases.
    for inst in edge_instances():
        check(inst)

    # 2) Random small instances.
    rng = random.Random(12345)
    for _ in range(3000):
        check(random_one_in_three_sat(rng))

    # 3) Exhaustive structured sweeps.
    for m in range(0, 5):
        if m < 3:
            check({"num_vars": m, "clauses": []})
            continue
        triples = [list(c) for c in itertools.combinations(range(1, m + 1), 3)]
        for c in triples:
            check({"num_vars": m, "clauses": [c]})
        for c1, c2 in itertools.combinations(triples, 2):
            check({"num_vars": m, "clauses": [c1, c2]})
        for combo in itertools.combinations(triples, 3):
            check({"num_vars": m, "clauses": list(combo)})

    # 4) Exhaustive multisets of clauses (duplicates allowed).
    for m in (4, 5):
        triples = [list(c) for c in itertools.combinations(range(1, m + 1), 3)]
        max_size = 4 if m == 4 else 3
        for size in range(0, max_size + 1):
            for combo in itertools.combinations_with_replacement(triples, size):
                check({"num_vars": m, "clauses": list(combo)})

    # 5) Larger random instances.
    for _ in range(2000):
        m = rng.randint(3, 10)
        nc = rng.randint(0, 10)
        cl = [sorted(rng.sample(range(1, m + 1), 3)) for _ in range(nc)]
        check({"num_vars": m, "clauses": cl})

    # 6) Polynomial-time sanity check on a big instance.
    big_m = 300
    big_clauses = [sorted(rng.sample(range(1, big_m + 1), 3)) for _ in range(600)]
    t0 = time.time()
    big_out = reduce({"num_vars": big_m, "clauses": big_clauses})
    elapsed = time.time() - t0
    SubsetSum.validate(big_out)
    assert elapsed < 5.0, f"reduce too slow on big instance: {elapsed}s"

    print(f"tests_run={tests_run} tests_passed={tests_passed}")
    if failures:
        print(f"FAILURES: {len(failures)}")
        for inst, msg in failures[:20]:
            print("  ", inst, "->", msg)
    else:
        print("ALL TESTS PASSED")

    verdict = {
        "verified": len(failures) == 0,
        "tests_run": tests_run,
        "tests_passed": tests_passed,
    }
    with open("verdict.json", "w") as f:
        json.dump(verdict, f)
        f.write("\n")
    print("wrote verdict.json:", verdict)
    return verdict


if __name__ == "__main__":
    main()
