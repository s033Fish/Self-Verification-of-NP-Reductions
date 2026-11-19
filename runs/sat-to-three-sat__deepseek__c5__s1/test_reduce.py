"""Independent tests for reduce.py (SAT -> 3-SAT).

We implement brute-force solvers for both problems from the docstrings in
problems.py, then compare answers on many small source instances and their
reductions.  We also validate every reduced instance against ThreeSat.validate.
"""

import itertools
import random

from problems import Sat, ThreeSat
from reduce import reduce


# ----------------------------------------------------------------------
# Brute-force solvers written from the problem definitions.

def sat_solve(instance):
    """Brute force SAT.  Returns True iff satisfiable."""
    m = instance["num_vars"]
    clauses = instance["clauses"]
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


def three_sat_solve(instance):
    """Brute force 3-SAT.  Returns True iff satisfiable.

    The semantics are identical to SAT, so we reuse the same routine; the
    format guarantees exactly 3 distinct-variable literals per clause.
    """
    return sat_solve(instance)


# ----------------------------------------------------------------------
# Instance generators.

def all_clause_lists(literals, max_len):
    """All lists of length 0..max_len over `literals` (order/repeats kept)."""
    out = []
    for length in range(0, max_len + 1):
        for combo in itertools.product(literals, repeat=length):
            out.append(list(combo))
    return out


def exhaustive_instances(max_vars, max_clauses, max_clause_len):
    """Yield small SAT instances exhaustively."""
    for m in range(0, max_vars + 1):
        literals = [v for v in range(1, m + 1)] + [-v for v in range(1, m + 1)]
        clause_pool = all_clause_lists(literals, max_clause_len)
        for nclauses in range(0, max_clauses + 1):
            for clauses in itertools.product(clause_pool, repeat=nclauses):
                yield {"num_vars": m, "clauses": [list(c) for c in clauses]}


def random_instance(rng, max_vars, max_clauses, max_clause_len):
    m = rng.randint(0, max_vars)
    literals = [v for v in range(1, m + 1)] + [-v for v in range(1, m + 1)]
    nclauses = rng.randint(0, max_clauses)
    clauses = []
    for _ in range(nclauses):
        length = rng.randint(0, max_clause_len)
        if not literals:
            length = 0  # only the empty clause is expressible with 0 vars
        clauses.append([rng.choice(literals) for _ in range(length)])
    return {"num_vars": m, "clauses": clauses}


# ----------------------------------------------------------------------
# Test driver.

def main():
    tests_run = 0
    tests_passed = 0
    failures = []

    def check(instance, label):
        nonlocal tests_run, tests_passed
        tests_run += 1
        try:
            Sat.validate(instance)
        except Exception as exc:  # generator bug, not a reduction failure
            failures.append((label, instance, "source invalid: %r" % (exc,)))
            return
        expected = sat_solve(instance)
        reduced = reduce(instance)
        # The reduction must produce a valid 3-SAT instance.
        try:
            ThreeSat.validate(reduced)
        except Exception as exc:
            failures.append((label, instance, "reduced invalid: %r -> %r" % (exc, reduced)))
            return
        got = three_sat_solve(reduced)
        if got != expected:
            failures.append(
                (label, instance, "sat=%r but reduced sat=%r (reduced=%r)" % (expected, got, reduced))
            )
            return
        tests_passed += 1

    # 1) Exhaustive small instances.
    for inst in exhaustive_instances(max_vars=2, max_clauses=2, max_clause_len=3):
        check(inst, "exhaustive-m<=2")
    for inst in exhaustive_instances(max_vars=3, max_clauses=1, max_clause_len=4):
        check(inst, "exhaustive-m<=3-1clause")

    # 2) Exhaustive over pairs of clauses for m<=3 (clause len 0..3).
    for m in range(0, 4):
        literals = [v for v in range(1, m + 1)] + [-v for v in range(1, m + 1)]
        pool = all_clause_lists(literals, 3)
        for c1 in pool:
            for c2 in pool:
                check({"num_vars": m, "clauses": [list(c1), list(c2)]}, "pairs-m<=3")

    # 2b) All single clauses up to length 6 over m<=3 vars (chain gadget).
    for m in range(0, 4):
        literals = [v for v in range(1, m + 1)] + [-v for v in range(1, m + 1)]
        for length in range(0, 7):
            for combo in itertools.product(literals, repeat=length):
                check({"num_vars": m, "clauses": [list(combo)]}, "long-single-clause")

    # 3) Random instances, including longer clauses (exercises the chain).
    rng = random.Random(12345)
    for _ in range(4000):
        inst = random_instance(rng, max_vars=4, max_clauses=4, max_clause_len=6)
        check(inst, "random")

    # 4) Targeted edge cases.
    edge_cases = [
        {"num_vars": 0, "clauses": []},
        {"num_vars": 0, "clauses": [[]]},
        {"num_vars": 1, "clauses": [[1]]},
        {"num_vars": 1, "clauses": [[-1]]},
        {"num_vars": 1, "clauses": [[1, -1]]},
        {"num_vars": 1, "clauses": [[1, 1, 1]]},
        {"num_vars": 2, "clauses": [[1, 2], [-1, -2], [1, -2], [-1, 2]]},
        {"num_vars": 2, "clauses": [[1, 2], [-1, -2]]},
        {"num_vars": 3, "clauses": [[1, 2, 3], [-1, -2, -3]]},
        {"num_vars": 4, "clauses": [[1, 2, 3, 4]]},
        {"num_vars": 4, "clauses": [[-1, -2, -3, -4]]},
        {"num_vars": 5, "clauses": [[1, 2, 3, 4, 5], [-1], [-2], [-3], [-4], [-5]]},
        {"num_vars": 6, "clauses": [[1, 2, 3, 4, 5, 6], [-1, -2, -3, -4, -5, -6]]},
        {"num_vars": 3, "clauses": [[1, 2, 3], [1, 2, 3], [1, 2, 3]]},
        {"num_vars": 3, "clauses": [[1, 1, 2, 2, 3, 3]]},
        {"num_vars": 4, "clauses": [[1, -1, 2, 3, 4]]},
    ]
    for inst in edge_cases:
        check(inst, "edge")

    print("tests_run   =", tests_run)
    print("tests_passed=", tests_passed)
    print("failures    =", len(failures))
    for label, inst, msg in failures[:20]:
        print("FAIL", label, inst, msg)

    return tests_run, tests_passed, failures


if __name__ == "__main__":
    import json

    run, passed, fails = main()
    verdict = {
        "verified": len(fails) == 0 and run == passed,
        "tests_run": run,
        "tests_passed": passed,
    }
    with open("verdict.json", "w") as fh:
        json.dump(verdict, fh)
        fh.write("\n")
    print("verdict:", verdict)
    assert not fails, "reduction failed on %d instance(s)" % len(fails)
    print("ALL TESTS PASSED")
