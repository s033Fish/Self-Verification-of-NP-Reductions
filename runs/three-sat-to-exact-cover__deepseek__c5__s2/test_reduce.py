"""Independent verification of reduce.py: 3-SAT -> Exact Cover.

We implement brute-force solvers for both problems from the definitions in
problems.py, generate many small 3-SAT instances, reduce them, and compare
the answers.  We also check that every produced instance validates and that
our exact-cover solver agrees with a second independent brute-force solver.
"""

import itertools
import random
from functools import lru_cache

from problems import ThreeSat, ExactCover
from reduce import reduce


# ---------------------------------------------------------------- solvers

def solve_three_sat(instance):
    """Brute force over all 2^m assignments."""
    m = instance["num_vars"]
    clauses = instance["clauses"]
    for bits in range(1 << m):
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


def solve_exact_cover(instance):
    """Exact cover via branching on the lowest uncovered element."""
    u = instance["universe_size"]
    full = (1 << u) - 1
    masks = []
    for s in instance["sets"]:
        mask = 0
        for e in s:
            mask |= 1 << e
        if mask:  # empty sets never matter
            masks.append(mask)
    masks = list(set(masks))  # duplicate sets never both chosen

    @lru_cache(maxsize=None)
    def rec(covered):
        if covered == full:
            return True
        rem = full & ~covered
        e = (rem & -rem).bit_length() - 1
        for mask in masks:
            if (mask >> e) & 1 and (mask & covered) == 0:
                if rec(covered | mask):
                    return True
        return False

    return rec(0)


def solve_exact_cover_bruteforce(instance):
    """Independent solver: try every subset of sets."""
    u = instance["universe_size"]
    sets = [set(s) for s in instance["sets"]]
    n = len(sets)
    for r in range(n + 1):
        for combo in itertools.combinations(range(n), r):
            covered = set()
            ok = True
            for idx in combo:
                if covered & sets[idx]:
                    ok = False
                    break
                covered |= sets[idx]
            if ok and covered == set(range(u)):
                return True
    return False


# ---------------------------------------------------------------- generators

def random_three_sat(rng, max_m=5, max_q=5):
    m = rng.randint(0, max_m)
    q = rng.randint(0, max_q)
    if q > 0:
        m = max(m, 3)
    clauses = []
    for _ in range(q):
        vs = rng.sample(range(1, m + 1), 3)
        clause = [v if rng.random() < 0.5 else -v for v in vs]
        clauses.append(clause)
    return {"num_vars": m, "clauses": clauses}


def all_small_instances():
    """Exhaustive small instances: m in 0..4, all clauses over 3 vars."""
    insts = []
    for m in range(0, 5):
        insts.append({"num_vars": m, "clauses": []})
    m = 3
    uniq = []
    seen = set()
    for vs in itertools.permutations([1, 2, 3]):
        for signs in itertools.product([1, -1], repeat=3):
            key = tuple(sorted(s * v for s, v in zip(signs, vs)))
            if key not in seen:
                seen.add(key)
                uniq.append(list(key))
    for c in uniq:
        insts.append({"num_vars": m, "clauses": [c]})
    for i in range(len(uniq)):
        for j in range(i, len(uniq)):
            insts.append({"num_vars": m, "clauses": [uniq[i], uniq[j]]})
    return insts


# ---------------------------------------------------------------- tests

def main():
    rng = random.Random(12345)
    tests_run = 0
    tests_passed = 0
    failures = []

    def check(inst, label):
        nonlocal tests_run, tests_passed
        tests_run += 1
        try:
            ThreeSat.validate(inst)
        except Exception as exc:  # noqa: BLE001
            failures.append(f"{label}: source invalid: {exc}")
            return
        src = solve_three_sat(inst)
        red = reduce(inst)
        try:
            ExactCover.validate(red)
        except Exception as exc:  # noqa: BLE001
            failures.append(f"{label}: reduced instance invalid: {exc}")
            return
        tgt = solve_exact_cover(red)
        if src == tgt:
            tests_passed += 1
        else:
            failures.append(
                f"{label}: mismatch src={src} tgt={tgt} inst={inst} red={red}"
            )

    # 1) exhaustive small instances
    for idx, inst in enumerate(all_small_instances()):
        check(inst, f"exhaustive[{idx}]")

    # 2) random small instances
    for idx in range(3000):
        check(random_three_sat(rng, max_m=5, max_q=5), f"random[{idx}]")

    # 3) larger random instances
    for idx in range(1500):
        check(random_three_sat(rng, max_m=8, max_q=10), f"large[{idx}]")

    # 4) targeted edge cases
    edge_cases = [
        {"num_vars": 0, "clauses": []},
        {"num_vars": 1, "clauses": []},
        {"num_vars": 3, "clauses": []},
        {"num_vars": 4, "clauses": []},
        {"num_vars": 3, "clauses": [
            [1, 2, 3], [1, 2, -3], [1, -2, 3], [1, -2, -3],
            [-1, 2, 3], [-1, 2, -3], [-1, -2, 3], [-1, -2, -3]]},  # unsat
        {"num_vars": 3, "clauses": [[1, 2, 3], [1, 2, 3], [1, 2, 3]]},
        {"num_vars": 5, "clauses": [[1, 2, 3]]},
        {"num_vars": 3, "clauses": [[-1, -2, -3]]},
        {"num_vars": 6, "clauses": [[1, 2, 3], [4, 5, 6], [-1, -4, 2]]},
    ]
    for idx, inst in enumerate(edge_cases):
        check(inst, f"edge[{idx}]")

    # 5) cross-check the exact-cover solver itself against a second solver
    for idx in range(2000):
        u = rng.randint(0, 6)
        sets = [rng.sample(range(u), rng.randint(0, u))
                for _ in range(rng.randint(0, 6))]
        inst = {"universe_size": u, "sets": sets}
        tests_run += 1
        if solve_exact_cover(inst) == solve_exact_cover_bruteforce(inst):
            tests_passed += 1
        else:
            failures.append(f"ec-solver[{idx}]: {inst}")

    print(f"tests_run={tests_run} tests_passed={tests_passed}")
    if failures:
        print(f"FAILURES ({len(failures)}):")
        for f in failures[:20]:
            print("  ", f)
    else:
        print("ALL PASSED")

    return tests_run, tests_passed, failures


if __name__ == "__main__":
    main()
