"""Independent verification of reduce.py: 1-in-3-SAT -> 3-SAT.

problems.py provides only validate(); we implement our own brute-force
solvers from the docstrings, then compare the source answer with the
answer of the reduced 3-SAT instance over many small instances.
"""

from __future__ import annotations

import itertools
import random

from problems import OneInThreeSat, ThreeSat
from reduce import reduce


# ----------------------------------------------------------------------
# Brute-force solvers written from the definitions in problems.py.

def solve_one_in_three(instance) -> bool:
    """True iff some assignment makes EXACTLY ONE var true per clause."""
    OneInThreeSat.validate(instance)
    m = instance["num_vars"]
    clauses = instance["clauses"]
    for bits in itertools.product((False, True), repeat=m):
        ok = True
        for (a, b, c) in clauses:
            count = int(bits[a - 1]) + int(bits[b - 1]) + int(bits[c - 1])
            if count != 1:
                ok = False
                break
        if ok:
            return True
    return False


def solve_three_sat(instance) -> bool:
    """True iff some assignment satisfies every clause (>= 1 true literal)."""
    ThreeSat.validate(instance)
    m = instance["num_vars"]
    clauses = instance["clauses"]
    for bits in itertools.product((False, True), repeat=m):
        ok = True
        for clause in clauses:
            if not any(
                bits[abs(lit) - 1] if lit > 0 else not bits[abs(lit) - 1]
                for lit in clause
            ):
                ok = False
                break
        if ok:
            return True
    return False


# ----------------------------------------------------------------------
# Instance generators.

def all_subsets_instances(m: int):
    """All formulas whose clause set is any subset of the C(m,3) triples."""
    triples = [list(t) for t in itertools.combinations(range(1, m + 1), 3)]
    for r in range(len(triples) + 1):
        for combo in itertools.combinations(triples, r):
            yield {"num_vars": m, "clauses": [list(c) for c in combo]}


def random_instances(count: int, seed: int = 2024):
    rng = random.Random(seed)
    out = []
    for _ in range(count):
        m = rng.randint(0, 7)
        if m < 3:
            out.append({"num_vars": m, "clauses": []})
            continue
        triples = [list(t) for t in itertools.combinations(range(1, m + 1), 3)]
        n_clauses = rng.randint(0, 6)
        clauses = [list(rng.choice(triples)) for _ in range(n_clauses)]
        out.append({"num_vars": m, "clauses": clauses})
    return out


def main() -> int:
    tests_run = 0
    tests_passed = 0
    failures = []

    instances = []
    # Edge cases: empty formulas for m = 0,1,2,3.
    for m in range(0, 4):
        instances.append({"num_vars": m, "clauses": []})
    # Exhaustive over all subsets of clauses for m = 3,4,5.
    for m in (3, 4, 5):
        instances.extend(all_subsets_instances(m))
    # Random instances (including duplicate clauses and unused variables).
    instances.extend(random_instances(600))
    # Larger random instances (m up to 8, up to 8 clauses).
    rng = random.Random(999)
    for _ in range(300):
        m = rng.randint(3, 8)
        triples = [list(t) for t in itertools.combinations(range(1, m + 1), 3)]
        n = rng.randint(0, 8)
        instances.append({"num_vars": m, "clauses": [list(rng.choice(triples)) for _ in range(n)]})

    for inst in instances:
        tests_run += 1
        try:
            src_answer = solve_one_in_three(inst)
            reduced = reduce(inst)
            ThreeSat.validate(reduced)
            tgt_answer = solve_three_sat(reduced)
            if src_answer == tgt_answer:
                tests_passed += 1
            else:
                failures.append((inst, src_answer, reduced, tgt_answer))
        except Exception as exc:  # noqa: BLE001
            failures.append((inst, "EXCEPTION", repr(exc), None))

    # Sanity check: reduce must not import/call a brute-force solver.
    import inspect
    src = inspect.getsource(reduce)
    for bad in ("itertools", "product", "solve_", "brute"):
        if bad in src:
            failures.append(("reduce.py references brute-force helper", bad, None, None))

    print(f"tests_run={tests_run} tests_passed={tests_passed}")
    if failures:
        print("FAILURES:")
        for f in failures[:10]:
            print(f)
    else:
        print("ALL PASSED")
    return 0 if not failures else 1


if __name__ == "__main__":
    raise SystemExit(main())
