"""Tests for reduce.py: compare exact answers on source instances with exact
answers on their reductions."""

from __future__ import annotations

import itertools
import random

from problems import SOURCE, TARGET
from reduce import reduce


def solve_three_sat(instance) -> bool:
    """Brute force 3-SAT: every clause has at least one true literal."""
    m = instance["num_vars"]
    clauses = instance["clauses"]
    for bits in itertools.product([False, True], repeat=m):
        ok = True
        for clause in clauses:
            if not any(
                (bits[abs(l) - 1] if l > 0 else not bits[abs(l) - 1]) for l in clause
            ):
                ok = False
                break
        if ok:
            return True
    return False


def solve_one_in_three_sat(instance) -> bool:
    """Exact solver for 1-in-3-SAT via backtracking with propagation.

    Variables are 1..m.  State: -1 unassigned, 0 false, 1 true.
    """
    m = instance["num_vars"]
    clauses = [tuple(c) for c in instance["clauses"]]

    state = [-1] * (m + 1)

    def propagate():
        """Return False on conflict; apply forced assignments until fixpoint."""
        changed = True
        while changed:
            changed = False
            for (a, b, c) in clauses:
                vals = [state[a], state[b], state[c]]
                t = vals.count(1)
                u = vals.count(-1)
                if t > 1:
                    return False
                if t == 1:
                    if u == 0:
                        continue  # satisfied
                    # remaining unassigned must be false
                    for v in (a, b, c):
                        if state[v] == -1:
                            state[v] = 0
                            changed = True
                else:  # t == 0
                    if u == 0:
                        return False
                    if u == 1:
                        for v in (a, b, c):
                            if state[v] == -1:
                                state[v] = 1
                                changed = True
        return True

    def search():
        if not propagate():
            return False
        # pick an unassigned variable
        v = -1
        for i in range(1, m + 1):
            if state[i] == -1:
                v = i
                break
        if v == -1:
            return True
        for val in (0, 1):
            saved = state[:]
            state[v] = val
            if search():
                return True
            for i in range(m + 1):
                state[i] = saved[i]
        return False

    return search()


def random_three_sat(rng, max_vars=5, max_clauses=6):
    m = rng.randint(0, max_vars)
    clauses = []
    if m >= 3:
        for _ in range(rng.randint(0, max_clauses)):
            vs = rng.sample(range(1, m + 1), 3)
            clause = [v if rng.random() < 0.5 else -v for v in vs]
            clauses.append(clause)
    return {"num_vars": m, "clauses": clauses}


def run():
    tests_run = 0
    tests_passed = 0
    failures = []

    def check(inst, label):
        nonlocal tests_run, tests_passed
        tests_run += 1
        SOURCE.validate(inst)
        out = reduce(inst)
        TARGET.validate(out)
        src = solve_three_sat(inst)
        tgt = solve_one_in_three_sat(out)
        if src == tgt:
            tests_passed += 1
        else:
            failures.append((label, inst, out, src, tgt))

    # Hand-picked edge cases.
    check({"num_vars": 0, "clauses": []}, "empty m=0")
    check({"num_vars": 1, "clauses": []}, "empty m=1")
    check({"num_vars": 2, "clauses": []}, "empty m=2")
    check({"num_vars": 5, "clauses": []}, "empty m=5")
    check({"num_vars": 3, "clauses": [[1, 2, 3]]}, "single positive")
    check({"num_vars": 3, "clauses": [[-1, -2, -3]]}, "single negative")
    check({"num_vars": 3, "clauses": [[1, -2, 3]]}, "mixed")
    check({"num_vars": 3, "clauses": [[1, 2, 3], [-1, -2, -3]]}, "two clauses")
    check({"num_vars": 3, "clauses": [[1, 2, 3]] * 3}, "duplicate clauses")
    check(
        {"num_vars": 4, "clauses": [[1, 2, 3], [1, 2, 4], [1, 3, 4], [2, 3, 4]]},
        "all pos 4",
    )
    check(
        {
            "num_vars": 4,
            "clauses": [[-1, -2, -3], [-1, -2, -4], [-1, -3, -4], [-2, -3, -4]],
        },
        "all neg 4",
    )
    # Unsatisfiable 3-SAT: all 8 clauses over 3 vars.
    all_clauses = []
    for signs in itertools.product([1, -1], repeat=3):
        all_clauses.append([signs[i] * (i + 1) for i in range(3)])
    check({"num_vars": 3, "clauses": all_clauses}, "unsat all 8")

    # Random tests.
    rng = random.Random(12345)
    for i in range(500):
        inst = random_three_sat(rng)
        check(inst, f"random {i}")

    print(f"tests_run={tests_run} tests_passed={tests_passed}")
    if failures:
        for f in failures[:5]:
            print("FAIL", f)
        raise SystemExit(1)
    return tests_run, tests_passed


if __name__ == "__main__":
    run()
