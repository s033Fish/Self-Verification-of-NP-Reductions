"""Independent tests for reduce.py (SAT -> 3-SAT).

We implement brute-force solvers for both problems directly from the
docstrings in problems.py, then compare answers on many small instances
and validate that every reduction output is a legal 3-SAT instance.
"""

from __future__ import annotations

import itertools
import random

from problems import Sat, ThreeSat, InvalidInstance
from reduce import reduce


# ----------------------------------------------------------------------
# Brute-force solvers written from the problem definitions.

def sat_answer(instance: dict) -> bool:
    """Brute force SAT: try every assignment of variables 1..m."""
    m = instance["num_vars"]
    clauses = instance["clauses"]
    for bits in itertools.product((False, True), repeat=m):
        # bits[i] is the value of variable i+1
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


def three_sat_answer(instance: dict) -> bool:
    """Brute force 3-SAT (same semantics, clauses of size 3)."""
    return sat_answer(instance)


# ----------------------------------------------------------------------
# Instance generators

def random_sat_instance(rng: random.Random, max_vars: int = 4, max_clauses: int = 5,
                        max_len: int = 6) -> dict:
    m = rng.randint(0, max_vars)
    clauses = []
    for _ in range(rng.randint(0, max_clauses)):
        length = rng.randint(0, max_len)
        clause = []
        for _ in range(length):
            if m == 0:
                break
            v = rng.randint(1, m)
            clause.append(v if rng.random() < 0.5 else -v)
        clauses.append(clause)
    return {"num_vars": m, "clauses": clauses}


def all_clauses_over(m: int) -> list[list[int]]:
    """Every possible clause over vars 1..m (each var absent/pos/neg)."""
    result = []
    for choices in itertools.product(range(3), repeat=m):
        clause = []
        for i, c in enumerate(choices):
            if c == 1:
                clause.append(i + 1)
            elif c == 2:
                clause.append(-(i + 1))
        result.append(clause)
    return result


def exhaustive_instances(m: int, max_clauses: int):
    """Exhaustively enumerate formulas with up to max_clauses clauses."""
    pool = all_clauses_over(m)
    for k in range(0, max_clauses + 1):
        for combo in itertools.combinations_with_replacement(pool, k):
            yield {"num_vars": m, "clauses": [list(c) for c in combo]}


# ----------------------------------------------------------------------
# Test driver

def main() -> int:
    tests_run = 0
    tests_passed = 0
    failures: list[str] = []

    def check(inst: dict) -> None:
        nonlocal tests_run, tests_passed
        tests_run += 1
        try:
            Sat.validate(inst)
        except InvalidInstance as exc:
            failures.append(f"generated invalid source {inst!r}: {exc}")
            return
        src = sat_answer(inst)
        out = reduce(inst)
        try:
            ThreeSat.validate(out)
        except InvalidInstance as exc:
            failures.append(f"reduce produced invalid 3-SAT for {inst!r}: {out!r} ({exc})")
            return
        tgt = three_sat_answer(out)
        if src != tgt:
            failures.append(
                f"MISMATCH src={inst!r} (sat={src}) -> out={out!r} (3sat={tgt})"
            )
            return
        tests_passed += 1

    # 1. Hand-picked edge cases.
    edge = [
        {"num_vars": 0, "clauses": []},
        {"num_vars": 3, "clauses": []},
        {"num_vars": 0, "clauses": [[]]},
        {"num_vars": 5, "clauses": [[]]},
        {"num_vars": 1, "clauses": [[1]]},
        {"num_vars": 1, "clauses": [[-1]]},
        {"num_vars": 1, "clauses": [[1], [-1]]},
        {"num_vars": 1, "clauses": [[1, -1]]},
        {"num_vars": 2, "clauses": [[1, 2]]},
        {"num_vars": 2, "clauses": [[1, -2], [-1, 2]]},
        {"num_vars": 3, "clauses": [[1, 2, 3]]},
        {"num_vars": 3, "clauses": [[1, 2, 3], [-1, -2, -3]]},
        {"num_vars": 4, "clauses": [[1, 2, 3, 4]]},
        {"num_vars": 4, "clauses": [[-1, -2, -3, -4]]},
        {"num_vars": 5, "clauses": [[1, 2, 3, 4, 5]]},
        {"num_vars": 5, "clauses": [[1, -2, 3, -4, 5]]},
        {"num_vars": 6, "clauses": [[1, 2, 3, 4, 5, 6]]},
        {"num_vars": 3, "clauses": [[1, 1, 2], [1, -1, 2], [3, 3, 3]]},
        {"num_vars": 3, "clauses": [[1, 2, 3], [1, 2, 3], [1, 2, 3]]},
        {"num_vars": 3, "clauses": [[1, 2], [1, 2], [-1, -2]]},
        {"num_vars": 4, "clauses": [[1, 2, 3, 4], [-1, -2, -3, -4], [1, -1]]},
    ]
    for inst in edge:
        check(inst)

    # 2. Exhaustive enumeration for m = 0, 1, 2 with up to 3 clauses.
    for m in (0, 1, 2):
        for inst in exhaustive_instances(m, 3):
            check(inst)

    # 3. Random instances.
    rng = random.Random(12345)
    for _ in range(4000):
        check(random_sat_instance(rng, max_vars=4, max_clauses=6, max_len=7))
    for _ in range(2000):
        check(random_sat_instance(rng, max_vars=5, max_clauses=8, max_len=9))

    # 4. Deterministic long-clause checks (chain correctness for many k).
    for k in range(1, 13):
        for signs in itertools.product((1, -1), repeat=k):
            clause = [signs[i] * (i + 1) for i in range(k)]
            check({"num_vars": k, "clauses": [clause]})
            # negation of every literal: still a single clause
            check({"num_vars": k, "clauses": [[-l for l in clause]]})

    print(f"tests_run={tests_run} tests_passed={tests_passed} failures={len(failures)}")
    for f in failures[:20]:
        print("FAIL:", f)
    return 0 if not failures else 1


if __name__ == "__main__":
    raise SystemExit(main())
