"""Independent tests for reduce.py (3-SAT -> Exact Cover).

We implement our own brute-force solvers for both problems from the
definitions in problems.py, then check that reduce() preserves the answer
on many small source instances.  We also check the *polynomial-time*
requirement: reduce must not run an exponential brute-force search.
"""

from __future__ import annotations

import itertools
import random
import subprocess
import sys
import time

from problems import ThreeSat, ExactCover
import reduce as reduce_module


# ----------------------------------------------------------------------
# Brute-force solvers (written from the problem definitions)
# ----------------------------------------------------------------------

def solve_three_sat(instance) -> bool:
    """True iff the 3-SAT formula is satisfiable."""
    m = instance["num_vars"]
    clauses = instance["clauses"]
    for mask in range(1 << m):
        ok = True
        for clause in clauses:
            sat = False
            for lit in clause:
                v = abs(lit)
                val = (mask >> (v - 1)) & 1
                if (lit > 0 and val == 1) or (lit < 0 and val == 0):
                    sat = True
                    break
            if not sat:
                ok = False
                break
        if ok:
            return True
    return False


def solve_exact_cover(instance) -> bool:
    """True iff some sub-collection of sets exactly covers 0..u-1."""
    u = instance["universe_size"]
    sets = instance["sets"]
    full = (1 << u) - 1

    # Backtracking over the list of sets.
    def rec(i, covered):
        if covered == full:
            return True
        if i == len(sets):
            return False
        if rec(i + 1, covered):          # skip set i
            return True
        mask = 0
        for e in sets[i]:
            mask |= 1 << e
        if mask & covered == 0:          # set i is disjoint from covered
            if rec(i + 1, covered | mask):
                return True
        return False

    return rec(0, 0)


# ----------------------------------------------------------------------
# Instance generation
# ----------------------------------------------------------------------

def all_clauses(m):
    """All valid 3-literal clauses over variables 1..m (3 distinct vars)."""
    clauses = []
    for vars_ in itertools.combinations(range(1, m + 1), 3):
        for signs in itertools.product((1, -1), repeat=3):
            clauses.append([s * v for s, v in zip(signs, vars_)])
    return clauses


def generate_instances():
    instances = []

    # m = 0, 1, 2: only the empty clause list is valid.
    for m in range(0, 3):
        instances.append({"num_vars": m, "clauses": []})

    # m = 3: every subset of the 8 possible clauses (256 formulas).
    cl = all_clauses(3)
    for r in range(len(cl) + 1):
        for combo in itertools.combinations(cl, r):
            instances.append({"num_vars": 3, "clauses": [list(c) for c in combo]})

    # m = 4 and m = 5: random subsets of the possible clauses.
    rng = random.Random(12345)
    for m in (4, 5):
        cl = all_clauses(m)
        for _ in range(300):
            r = rng.randint(0, len(cl))
            chosen = rng.sample(cl, r)
            instances.append({"num_vars": m, "clauses": [list(c) for c in chosen]})

    # Some duplicated-clause and unused-variable cases.
    instances.append({"num_vars": 5, "clauses": [[1, 2, 3], [1, 2, 3]]})
    instances.append({"num_vars": 6, "clauses": [[4, 5, 6]]})
    instances.append({"num_vars": 6, "clauses": [[1, 2, 3], [-1, -2, -3], [1, 2, -3]]})

    return instances


# ----------------------------------------------------------------------
# Tests
# ----------------------------------------------------------------------

def main():
    tests_run = 0
    tests_passed = 0
    failures = []

    def check(name, condition):
        nonlocal tests_run, tests_passed
        tests_run += 1
        if condition:
            tests_passed += 1
        else:
            failures.append(name)

    instances = generate_instances()

    for idx, inst in enumerate(instances):
        # Source instance must be valid.
        try:
            ThreeSat.validate(inst)
        except Exception as exc:  # noqa: BLE001
            check(f"source valid #{idx}", False)
            continue

        expected = solve_three_sat(inst)

        try:
            target = reduce_module.reduce(inst)
        except Exception as exc:  # noqa: BLE001
            check(f"reduce ran #{idx}", False)
            continue

        # Target must be a valid ExactCover instance.
        try:
            ExactCover.validate(target)
            target_valid = True
        except Exception:
            target_valid = False
        check(f"target valid #{idx}", target_valid)

        got = solve_exact_cover(target)
        check(f"answer preserved #{idx}", got == expected)

    # Explicit edge cases.
    check("empty formula m=0 is yes", solve_three_sat({"num_vars": 0, "clauses": []}))
    check("empty formula m=5 is yes", solve_three_sat({"num_vars": 5, "clauses": []}))
    check("exact cover u=0 is yes", solve_exact_cover({"universe_size": 0, "sets": []}))
    check("exact cover u=1 no sets is no",
          not solve_exact_cover({"universe_size": 1, "sets": []}))

    # ------------------------------------------------------------------
    # Polynomial-time requirement.
    #
    # reduce.py's _satisfiable enumerates all 2^m assignments, which is a
    # brute-force solver and is exponential in m.  Demonstrate this at
    # runtime: an unsatisfiable formula on 25 variables must be reduced in
    # polynomial time if the requirement held.  We give it 5 seconds.
    # ------------------------------------------------------------------
    poly_ok = True
    poly_detail = ""
    unsat_25 = {
        "num_vars": 25,
        # All 8 clauses on variables 1,2,3 -> unsatisfiable.
        "clauses": [
            [1, 2, 3], [1, 2, -3], [1, -2, 3], [1, -2, -3],
            [-1, 2, 3], [-1, 2, -3], [-1, -2, 3], [-1, -2, -3],
        ],
    }
    # Sanity: our own solver agrees it is unsatisfiable (fast: 2^3 core).
    assert solve_three_sat(unsat_25) is False

    code = (
        "import reduce, json, sys\n"
        "inst = json.loads(sys.argv[1])\n"
        "reduce.reduce(inst)\n"
    )
    import json as _json
    try:
        proc = subprocess.run(
            [sys.executable, "-c", code, _json.dumps(unsat_25)],
            cwd=".",
            capture_output=True,
            timeout=5,
        )
        if proc.returncode != 0:
            poly_ok = False
            poly_detail = "reduce crashed: " + proc.stderr.decode()[:300]
    except subprocess.TimeoutExpired:
        poly_ok = False
        poly_detail = "reduce on 25-var unsatisfiable formula exceeded 5s (exponential)"

    check("reduce runs in polynomial time (no brute force)", poly_ok)

    # Static confirmation that the exponential enumeration is present.
    src = open("reduce.py").read()
    check("reduce.py contains no 2^m enumeration", "1 << m" not in src)

    print(f"tests_run={tests_run} tests_passed={tests_passed}")
    if failures:
        print("FAILURES:")
        for f in failures:
            print("  -", f)
    if poly_detail:
        print("poly detail:", poly_detail)
    return 0 if tests_passed == tests_run else 1


if __name__ == "__main__":
    sys.exit(main())
