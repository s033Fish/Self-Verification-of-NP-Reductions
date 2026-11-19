"""Independent checks of reduce.py: 3-SAT -> NAE-3-SAT.

We implement brute-force solvers for both problems from the docstrings and
compare answers on many small source instances (exhaustive + random).
"""

from __future__ import annotations

import itertools
import random

from problems import ThreeSat, NaeThreeSat
from reduce import reduce


# ----------------------------------------------------------------------
# Brute-force solvers written from the problem definitions.
# ----------------------------------------------------------------------

def sat_solve(instance: dict) -> bool:
    """3-SAT: yes iff some assignment makes every clause have a true literal."""
    m = instance["num_vars"]
    clauses = instance["clauses"]
    if not clauses:
        return True
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


def nae_solve(instance: dict) -> bool:
    """NAE-3-SAT: yes iff some assignment makes every clause not all equal."""
    m = instance["num_vars"]
    clauses = instance["clauses"]
    if not clauses:
        return True
    for bits in itertools.product([False, True], repeat=m):
        ok = True
        for clause in clauses:
            vals = [(lit > 0) == bits[abs(lit) - 1] for lit in clause]
            if all(vals) or not any(vals):
                ok = False
                break
        if ok:
            return True
    return False


# ----------------------------------------------------------------------
# Instance generation.
# ----------------------------------------------------------------------

def all_clauses(m: int):
    """All valid 3-literal clauses over variables 1..m (3 distinct vars)."""
    out = []
    for vars_ in itertools.combinations(range(1, m + 1), 3):
        for signs in itertools.product([1, -1], repeat=3):
            out.append([s * v for s, v in zip(signs, vars_)])
    return out


def random_instance(rng: random.Random, m: int, max_clauses: int) -> dict:
    if m < 3:
        return {"num_vars": m, "clauses": []}
    pool = all_clauses(m)
    k = rng.randint(0, min(max_clauses, len(pool)))
    clauses = [list(rng.choice(pool)) for _ in range(k)]
    return {"num_vars": m, "clauses": clauses}


def main() -> None:
    rng = random.Random(12345)
    tests_run = 0
    tests_passed = 0
    failures = []

    def check(inst: dict, tag: str) -> None:
        nonlocal tests_run, tests_passed
        tests_run += 1
        ThreeSat.validate(inst)
        red = reduce(inst)
        # The reduction must produce a valid target instance.
        NaeThreeSat.validate(red)
        want = sat_solve(inst)
        got = nae_solve(red)
        if want == got:
            tests_passed += 1
        else:
            failures.append((tag, inst, red, want, got))

    # 1. Edge cases: no clauses, including m = 0.
    for m in range(0, 7):
        check({"num_vars": m, "clauses": []}, f"empty-m{m}")

    # 2. Exhaustive over ALL formulas for small m (all subsets is too many,
    #    so enumerate all single clauses, all pairs, and all triples).
    for m in range(3, 5):
        pool = all_clauses(m)
        # all single-clause formulas
        for c in pool:
            check({"num_vars": m, "clauses": [list(c)]}, f"single-m{m}")
        # all pairs of clauses
        for c1, c2 in itertools.combinations_with_replacement(pool, 2):
            check({"num_vars": m, "clauses": [list(c1), list(c2)]}, f"pair-m{m}")
        # all triples of clauses
        for combo in itertools.combinations_with_replacement(pool, 3):
            check({"num_vars": m, "clauses": [list(c) for c in combo]}, f"triple-m{m}")

    # 3. Random instances of various sizes.
    for _ in range(4000):
        m = rng.randint(0, 6)
        inst = random_instance(rng, m, max_clauses=8)
        check(inst, f"rand-m{m}")

    # 4. A few larger random instances (still brute-forceable).
    for _ in range(200):
        m = rng.randint(7, 9)
        inst = random_instance(rng, m, max_clauses=15)
        check(inst, f"big-m{m}")

    print(f"tests_run={tests_run} tests_passed={tests_passed} failures={len(failures)}")
    for tag, inst, red, want, got in failures[:10]:
        print("FAIL", tag, inst, "->", red, "want", want, "got", got)

    # Sanity check the gadget identity used by reduce.py directly.
    id_ok = True
    for a, b, c, d in itertools.product([False, True], repeat=4):
        lhs = not (a == b == c == d)
        rhs = any(
            (not (a == b == y)) and (not (c == d == (not y)))
            for y in (False, True)
        )
        if lhs != rhs:
            id_ok = False
            print("IDENTITY FAIL", a, b, c, d, lhs, rhs)
    print("gadget identity holds:", id_ok)

    assert not failures, "reduction mismatches found"
    assert id_ok
    assert tests_passed == tests_run


if __name__ == "__main__":
    main()
