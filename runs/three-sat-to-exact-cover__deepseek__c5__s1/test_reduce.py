"""Independent verification of reduce.py: 3-SAT -> Exact Cover.

We implement brute-force solvers for both problems directly from the
docstrings in problems.py, then compare answers on many small instances.
"""

from __future__ import annotations

import itertools
import random
import sys

from problems import ThreeSat, ExactCover, InvalidInstance
from reduce import reduce


# ----------------------------------------------------------------------
# Brute-force solvers (independent of reduce.py)
# ----------------------------------------------------------------------

def solve_three_sat(instance: dict) -> bool:
    """True iff some assignment satisfies every clause."""
    m = instance["num_vars"]
    clauses = instance["clauses"]
    for bits in itertools.product((False, True), repeat=m):
        # variable v (1..m) is bits[v-1]
        ok = True
        for clause in clauses:
            if not any(
                (bits[abs(lit) - 1] if lit > 0 else not bits[abs(lit) - 1])
                for lit in clause
            ):
                ok = False
                break
        if ok:
            return True
    return False


def solve_exact_cover(instance: dict) -> bool:
    """True iff some subcollection partitions the universe exactly."""
    u = instance["universe_size"]
    full = (1 << u) - 1
    masks = []
    for s in instance["sets"]:
        mask = 0
        for e in s:
            mask |= 1 << e
        if mask:
            masks.append(mask)
    masks = list(set(masks))  # duplicates never help

    seen: set[int] = set()

    def dfs(covered: int) -> bool:
        if covered == full:
            return True
        if covered in seen:
            return False
        seen.add(covered)
        inv = (~covered) & full
        # lowest uncovered element
        e = (inv & -inv).bit_length() - 1
        for mask in masks:
            if (mask >> e) & 1 and (mask & covered) == 0:
                if dfs(covered | mask):
                    return True
        return False

    return dfs(0)


# ----------------------------------------------------------------------
# Instance generators
# ----------------------------------------------------------------------

def random_three_sat(rng: random.Random) -> dict:
    while True:
        m = rng.randint(0, 5)
        n = rng.randint(0, 6)
        if n > 0 and m < 3:
            continue
        clauses = []
        for _ in range(n):
            vars_ = rng.sample(range(1, m + 1), 3)
            clause = [v if rng.random() < 0.5 else -v for v in vars_]
            clauses.append(clause)
        # occasionally duplicate a clause
        if clauses and rng.random() < 0.2:
            clauses.append(list(rng.choice(clauses)))
        return {"num_vars": m, "clauses": clauses}


# ----------------------------------------------------------------------
# Test driver
# ----------------------------------------------------------------------

def main() -> int:
    tests_run = 0
    tests_passed = 0
    failures = []

    def check(name, instance):
        nonlocal tests_run, tests_passed
        tests_run += 1
        try:
            ThreeSat.validate(instance)
        except InvalidInstance as exc:
            failures.append(f"{name}: source invalid: {exc}")
            return
        reduced = reduce(instance)
        try:
            ExactCover.validate(reduced)
        except InvalidInstance as exc:
            failures.append(f"{name}: reduced instance invalid: {exc}")
            return
        src = solve_three_sat(instance)
        tgt = solve_exact_cover(reduced)
        if src != tgt:
            failures.append(
                f"{name}: MISMATCH src={src} tgt={tgt}\n"
                f"  instance={instance}\n  reduced={reduced}"
            )
            return
        tests_passed += 1

    # ---- explicit edge cases ----
    edge = [
        ("m=0,n=0", {"num_vars": 0, "clauses": []}),
        ("m=1,n=0", {"num_vars": 1, "clauses": []}),
        ("m=5,n=0", {"num_vars": 5, "clauses": []}),
        ("single clause sat", {"num_vars": 3, "clauses": [[1, 2, 3]]}),
        ("single clause sat mixed", {"num_vars": 3, "clauses": [[1, -2, 3]]}),
        ("all 8 clauses on 3 vars (unsat)",
         {"num_vars": 3,
          "clauses": [[s * v for s, v in zip(signs, (1, 2, 3))]
                      for signs in itertools.product((1, -1), repeat=3)]}),
        ("dup clauses", {"num_vars": 3, "clauses": [[1, 2, 3], [1, 2, 3]]}),
        ("unused vars", {"num_vars": 6, "clauses": [[1, 2, 3]]}),
        ("forced unsat 4 vars",
         {"num_vars": 4,
          "clauses": [[1, 2, 3], [-1, 2, 3], [1, -2, 3], [1, 2, -3],
                      [-1, -2, -3]]}),
    ]
    for name, inst in edge:
        check(name, inst)

    # ---- exhaustive over all small formulas ----
    # all formulas with m=3, n=1 and n=2 (up to clause ordering)
    all_clauses_m3 = []
    for vars_ in itertools.combinations([1, 2, 3], 3):
        for signs in itertools.product((1, -1), repeat=3):
            all_clauses_m3.append([s * v for s, v in zip(signs, vars_)])
    for clause in all_clauses_m3:
        check("exh m3 n1", {"num_vars": 3, "clauses": [clause]})
    for c1 in all_clauses_m3:
        for c2 in all_clauses_m3:
            check("exh m3 n2", {"num_vars": 3, "clauses": [c1, c2]})
    for c1 in all_clauses_m3:
        for c2 in all_clauses_m3:
            for c3 in all_clauses_m3:
                check("exh m3 n3", {"num_vars": 3, "clauses": [c1, c2, c3]})

    # exhaustive m=4, n=2 over all 32 clauses
    all_clauses_m4 = []
    for vars_ in itertools.combinations([1, 2, 3, 4], 3):
        for signs in itertools.product((1, -1), repeat=3):
            all_clauses_m4.append([s * v for s, v in zip(signs, vars_)])
    for c1 in all_clauses_m4:
        for c2 in all_clauses_m4:
            check("exh m4 n2", {"num_vars": 4, "clauses": [c1, c2]})

    # ---- randomized ----
    rng = random.Random(12345)
    for t in range(3000):
        inst = random_three_sat(rng)
        check(f"rand{t}", inst)

    # ---- output size sanity (polynomial) ----
    big = {"num_vars": 20,
           "clauses": [[1, 2, 3], [-1, 4, 5], [6, -2, 7], [8, 9, -3]]}
    red = reduce(big)
    expected_u = 20 + 4 * 4
    if red["universe_size"] != expected_u:
        failures.append(
            f"size: expected universe_size {expected_u}, got {red['universe_size']}"
        )
    tests_run += 1
    if not any(f.startswith("size:") for f in failures):
        tests_passed += 1

    # ---- polynomial size scaling ----
    import time
    for (m, n) in [(10, 20), (50, 100), (200, 400)]:
        clauses = []
        rng2 = random.Random(m * 1000 + n)
        for _ in range(n):
            vs = rng2.sample(range(1, m + 1), 3)
            clauses.append([v if rng2.random() < 0.5 else -v for v in vs])
        inst = {"num_vars": m, "clauses": clauses}
        t0 = time.time()
        red = reduce(inst)
        dt = time.time() - t0
        tests_run += 1
        ok = True
        if red["universe_size"] != m + 4 * n:
            failures.append(f"scale m={m},n={n}: bad universe_size {red['universe_size']}")
            ok = False
        if len(red["sets"]) != 2 * m + 6 * n:
            failures.append(f"scale m={m},n={n}: bad #sets {len(red['sets'])}")
            ok = False
        try:
            ExactCover.validate(red)
        except InvalidInstance as exc:
            failures.append(f"scale m={m},n={n}: invalid reduced: {exc}")
            ok = False
        if dt > 5.0:
            failures.append(f"scale m={m},n={n}: too slow {dt:.2f}s")
            ok = False
        if ok:
            tests_passed += 1

    print(f"tests_run={tests_run}")
    print(f"tests_passed={tests_passed}")
    if failures:
        print(f"FAILURES ({len(failures)}):")
        for f in failures[:20]:
            print(" -", f)
        return 1
    print("ALL TESTS PASSED")
    return 0


if __name__ == "__main__":
    sys.exit(main())
