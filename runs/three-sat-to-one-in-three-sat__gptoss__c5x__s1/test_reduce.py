"""Independent tests for reduce.py (3-SAT -> 1-in-3-SAT).

Solvers are written from scratch directly from the problem definitions in
problems.py.  We compare the answer of every small source instance with the
answer of its reduction.
"""

from __future__ import annotations

import itertools
import json
import random

from problems import ThreeSat, OneInThreeSat
from reduce import reduce


# ----------------------------------------------------------------------
# Solvers (exhaustive backtracking, written from the definitions).
# ----------------------------------------------------------------------

def solve_three_sat(instance):
    """Yes iff some assignment satisfies every 3-SAT clause."""
    ThreeSat.validate(instance)
    m = instance["num_vars"]
    clauses = instance["clauses"]

    def rec(i, assign):
        if i == m:
            for clause in clauses:
                if not any((assign[abs(l) - 1] if l > 0 else not assign[abs(l) - 1])
                           for l in clause):
                    return False
            return True
        for val in (False, True):
            assign.append(val)
            if rec(i + 1, assign):
                return True
            assign.pop()
        return False

    return rec(0, [])


def solve_one_in_three_sat(instance):
    """Yes iff some assignment makes exactly one var true in every clause."""
    OneInThreeSat.validate(instance)
    m = instance["num_vars"]
    clauses = instance["clauses"]

    def rec(i, assign):
        if i == m:
            for clause in clauses:
                if sum(assign[v - 1] for v in clause) != 1:
                    return False
            return True
        for val in (False, True):
            assign.append(val)
            if rec(i + 1, assign):
                return True
            assign.pop()
        return False

    return rec(0, [])


# ----------------------------------------------------------------------
# Generators for valid SOURCE (3-SAT) instances.
# ----------------------------------------------------------------------

def all_clauses(m):
    out = []
    for vars_ in itertools.combinations(range(1, m + 1), 3):
        for signs in itertools.product([1, -1], repeat=3):
            out.append([s * v for s, v in zip(signs, vars_)])
    return out


def source_instances():
    # No clauses, including m = 0,1,2 (edge cases).
    for m in range(0, 5):
        yield {"num_vars": m, "clauses": []}

    # Exhaustive: m = 3, every subset of up to 3 clauses.
    pool3 = all_clauses(3)
    for k in range(0, 4):
        for combo in itertools.combinations(pool3, k):
            yield {"num_vars": 3, "clauses": [list(c) for c in combo]}

    # Random small instances, keeping the reduced target brute-forceable.
    rng = random.Random(12345)
    for m in range(3, 5):
        pool = all_clauses(m)
        for _ in range(100):
            k = rng.randint(0, 2)
            yield {"num_vars": m, "clauses": [list(rng.choice(pool)) for _ in range(k)]}


# ----------------------------------------------------------------------
# Driver.
# ----------------------------------------------------------------------

def main():
    tests_run = 0
    tests_passed = 0
    failures = []

    for idx, inst in enumerate(source_instances()):
        tests_run += 1
        try:
            ThreeSat.validate(inst)
            expected = solve_three_sat(inst)
            reduced = reduce(inst)
            OneInThreeSat.validate(reduced)
            got = solve_one_in_three_sat(reduced)
        except Exception as exc:
            failures.append((idx, inst, "exception: %r" % (exc,)))
            continue
        if got == expected:
            tests_passed += 1
        elif len(failures) < 10:
            failures.append((idx, inst, expected, got))

    print("tests_run =", tests_run)
    print("tests_passed =", tests_passed)
    print("failures =", len(failures))
    for f in failures[:5]:
        print("FAIL:", f)

    verified = (tests_run > 0 and tests_passed == tests_run)
    verdict = {
        "verified": bool(verified),
        "tests_run": tests_run,
        "tests_passed": tests_passed,
    }
    with open("verdict.json", "w") as fh:
        json.dump(verdict, fh)
    print("verdict:", verdict)


if __name__ == "__main__":
    main()
