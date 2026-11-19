"""Independent tests for reduce.py: 3-SAT -> 1-in-3-SAT.

Solvers are written from the definitions in problems.py.  Because the
reduced target instances contain many auxiliary variables, brute force over
all target variables is infeasible; instead we use a small, self-contained
DPLL CNF solver and encode each problem into CNF.  This is still an
independent, exact decision procedure.
"""

from __future__ import annotations

import itertools
import random

from problems import SOURCE, TARGET
from reduce import reduce


# ----------------------------------------------------------------------
# A small exact DPLL CNF solver (no external libraries).

def _simplify(clauses, lit):
    """Return clauses after assigning `lit` true, or None on conflict."""
    out = []
    for c in clauses:
        if lit in c:
            continue
        if -lit in c:
            nc = [x for x in c if x != -lit]
            if not nc:
                return None
            out.append(nc)
        else:
            out.append(c)
    return out


def solve_cnf(clauses) -> bool:
    """Exact satisfiability of a CNF given as a list of literal lists."""
    clauses = [list(c) for c in clauses]

    def rec(clauses) -> bool:
        while True:
            unit = None
            for c in clauses:
                if len(c) == 0:
                    return False
                if len(c) == 1:
                    unit = c[0]
                    break
            if unit is None:
                break
            clauses = _simplify(clauses, unit)
            if clauses is None:
                return False
        if not clauses:
            return True
        lit = clauses[0][0]
        for val in (lit, -lit):
            nxt = _simplify(clauses, val)
            if nxt is not None and rec(nxt):
                return True
        return False

    return rec(clauses)


# ----------------------------------------------------------------------
# Solvers for the two problems, from the definitions.

def solve_three_sat(instance: dict) -> bool:
    """Yes iff some assignment satisfies every clause (>=1 true literal)."""
    return solve_cnf(instance["clauses"])


def solve_one_in_three_sat(instance: dict) -> bool:
    """Yes iff some assignment makes EXACTLY ONE var true in every clause."""
    cnf = []
    for a, b, c in instance["clauses"]:
        cnf.append([a, b, c])          # at least one true
        cnf.append([-a, -b])           # at most one true
        cnf.append([-a, -c])
        cnf.append([-b, -c])
    return solve_cnf(cnf)


# ----------------------------------------------------------------------
# Instance generators

def random_three_sat(rng: random.Random, m: int, num_clauses: int) -> dict:
    clauses = []
    for _ in range(num_clauses):
        vs = rng.sample(range(1, m + 1), 3)
        clause = [v if rng.random() < 0.5 else -v for v in vs]
        clauses.append(clause)
    return {"num_vars": m, "clauses": clauses}


def all_three_sat_clauses(m: int):
    """All possible clauses (as sorted tuples) over variables 1..m."""
    out = []
    for vs in itertools.combinations(range(1, m + 1), 3):
        for signs in itertools.product([1, -1], repeat=3):
            out.append(tuple(sorted(s * v for s, v in zip(signs, vs))))
    return out


# ----------------------------------------------------------------------
# Tests

def main() -> int:
    rng = random.Random(12345)
    tests_run = 0
    tests_passed = 0
    failures = []

    def check(inst: dict, label: str) -> None:
        nonlocal tests_run, tests_passed
        tests_run += 1
        try:
            SOURCE.validate(inst)
        except Exception as e:  # generated instance should be valid
            failures.append(f"{label}: source invalid: {e}")
            return
        src_ans = solve_three_sat(inst)
        red = reduce(inst)
        try:
            TARGET.validate(red)
        except Exception as e:
            failures.append(f"{label}: reduced invalid: {e}\n  red={red}")
            return
        tgt_ans = solve_one_in_three_sat(red)
        if src_ans != tgt_ans:
            failures.append(
                f"{label}: MISMATCH src={src_ans} tgt={tgt_ans}\n  src={inst}\n  red={red}"
            )
            return
        tests_passed += 1

    # Edge cases: no clauses, various m.
    for m in range(0, 7):
        check({"num_vars": m, "clauses": []}, f"empty m={m}")

    # Exhaustive: m=3, all single clauses and all pairs of clauses.
    all_cl = all_three_sat_clauses(3)
    for c in all_cl:
        check({"num_vars": 3, "clauses": [list(c)]}, f"m3 single {c}")
    for c1 in all_cl:
        for c2 in all_cl:
            check({"num_vars": 3, "clauses": [list(c1), list(c2)]}, f"m3 pair {c1},{c2}")

    # Random instances over a range of sizes.
    for _ in range(4000):
        m = rng.randint(3, 6)
        nc = rng.randint(0, 10)
        check(random_three_sat(rng, m, nc), f"rand m={m} nc={nc}")

    for _ in range(1500):
        m = rng.randint(6, 8)
        nc = rng.randint(0, 20)
        check(random_three_sat(rng, m, nc), f"rand2 m={m} nc={nc}")

    # Duplicated clauses.
    for _ in range(500):
        m = rng.randint(3, 5)
        base = random_three_sat(rng, m, rng.randint(1, 4))
        cl = base["clauses"] + [list(c) for c in base["clauses"]]
        check({"num_vars": m, "clauses": cl}, "duplicated")

    # Unsat-ish structured instances: all 8 clauses on 3 vars (unsat).
    check({"num_vars": 3, "clauses": [list(c) for c in all_cl]}, "all8 m3")
    # All 8 clauses on 3 vars except one (sat).
    for skip in range(len(all_cl)):
        cl = [list(c) for i, c in enumerate(all_cl) if i != skip]
        check({"num_vars": 3, "clauses": cl}, f"all8-minus-{skip}")

    print(f"tests_run={tests_run} tests_passed={tests_passed} failures={len(failures)}")
    for f in failures[:20]:
        print("FAIL:", f)
    return 0 if not failures else 1


if __name__ == "__main__":
    raise SystemExit(main())
