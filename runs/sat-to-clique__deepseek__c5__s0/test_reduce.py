"""Independent verification of reduce.py (SAT -> Clique).

We implement brute-force solvers for both problems straight from the
definitions in problems.py, generate many small source instances (including
all the documented edge cases plus exhaustive small formulas), reduce each
one, and compare the answers.  We also validate that every reduced instance
is a well-formed Clique instance.

Run:  python3 test_reduce.py
Writes verdict.json with {"verified", "tests_run", "tests_passed"}.
"""

from __future__ import annotations

import itertools
import json
import random

from problems import Sat, Clique
from reduce import reduce


# ----------------------------------------------------------------------
# Brute-force solvers written from the problem definitions.

def sat_brute(instance):
    """Return True iff the CNF instance is satisfiable (try all assignments)."""
    Sat.validate(instance)
    m = instance["num_vars"]
    clauses = instance["clauses"]
    for bits in itertools.product([False, True], repeat=m):
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


def clique_brute(instance):
    """Return True iff the graph has a clique of at least k vertices.

    Exact recursive search with pruning (still brute force, just not the
    hopeless itertools.combinations version on larger graphs).
    """
    Clique.validate(instance)
    n = instance["n"]
    k = instance["k"]
    if k <= 0:
        return True
    if k > n:
        return False

    adj = [set() for _ in range(n)]
    for u, v in instance["edges"]:
        adj[u].add(v)
        adj[v].add(u)

    def search(candidates, need):
        if need <= 0:
            return True
        if len(candidates) < need:
            return False
        for v in list(candidates):
            if search(candidates & adj[v], need - 1):
                return True
            candidates = candidates - {v}
            if len(candidates) < need:
                return False
        return False

    return search(set(range(n)), k)


# ----------------------------------------------------------------------
# Instance generation.

def random_sat(rng, max_vars=4, max_clauses=5, max_len=3):
    m = rng.randint(0, max_vars)
    nclauses = rng.randint(0, max_clauses)
    clauses = []
    for _ in range(nclauses):
        length = rng.randint(0, max_len)
        clause = []
        for _ in range(length):
            if m == 0:
                break
            v = rng.randint(1, m)
            clause.append(v if rng.random() < 0.5 else -v)
        clauses.append(clause)
    return {"num_vars": m, "clauses": clauses}


def edge_case_instances():
    """Hand-picked instances covering every documented edge case."""
    return [
        # no clauses -> yes
        {"num_vars": 0, "clauses": []},
        {"num_vars": 3, "clauses": []},
        # empty clause -> no
        {"num_vars": 0, "clauses": [[]]},
        {"num_vars": 3, "clauses": [[]]},
        {"num_vars": 3, "clauses": [[1], []]},
        {"num_vars": 3, "clauses": [[], []]},
        # single unit clauses
        {"num_vars": 1, "clauses": [[1]]},
        {"num_vars": 1, "clauses": [[-1]]},
        {"num_vars": 1, "clauses": [[1], [-1]]},
        # tautological clause (contains v and -v)
        {"num_vars": 1, "clauses": [[1, -1]]},
        {"num_vars": 1, "clauses": [[1, -1], []]},
        {"num_vars": 2, "clauses": [[1, -1], [2], [-2]]},
        # repeated literals inside a clause
        {"num_vars": 2, "clauses": [[1, 1, 1]]},
        {"num_vars": 2, "clauses": [[1, 1], [-1, -1]]},
        # repeated clauses
        {"num_vars": 2, "clauses": [[1], [1], [1]]},
        {"num_vars": 2, "clauses": [[1], [-1], [1]]},
        # variables that never appear
        {"num_vars": 5, "clauses": [[1], [2]]},
        # classic unsat
        {"num_vars": 1, "clauses": [[1], [-1], [1, -1]]},
        # a satisfiable 3-var formula
        {"num_vars": 3, "clauses": [[1, 2], [-1, 3], [-2, -3]]},
    ]


def exhaustive_small_instances():
    """Every formula with 0..2 clauses of length 0..2 over 0..2 variables."""
    out = []
    for m in range(0, 3):
        lits = []
        for v in range(1, m + 1):
            lits += [v, -v]
        pool = [[]]
        for L in (1, 2):
            for combo in itertools.combinations_with_replacement(lits, L):
                pool.append(list(combo))
        for ncl in range(0, 3):
            for combo in itertools.combinations_with_replacement(pool, ncl):
                out.append({"num_vars": m, "clauses": [list(c) for c in combo]})
    return out


def main():
    rng = random.Random(12345)

    tests_run = 0
    tests_passed = 0
    failures = []

    instances = edge_case_instances() + exhaustive_small_instances()
    for _ in range(4000):
        instances.append(random_sat(rng))
    for _ in range(3000):
        instances.append(random_sat(rng, max_vars=8, max_clauses=10, max_len=4))

    for inst in instances:
        tests_run += 1
        try:
            expected = sat_brute(inst)
            reduced = reduce(inst)
            # The reduction must itself produce a valid Clique instance.
            Clique.validate(reduced)
            got = clique_brute(reduced)
        except Exception as exc:  # noqa: BLE001
            failures.append((inst, f"exception: {exc!r}"))
            continue
        if expected == got:
            tests_passed += 1
        else:
            failures.append((inst, f"sat={expected} clique={got} reduced={reduced}"))

    # The reduction must be deterministic.
    for inst in instances[:50]:
        tests_run += 1
        if reduce(inst) == reduce(inst):
            tests_passed += 1
        else:
            failures.append((inst, "non-deterministic output"))

    verified = len(failures) == 0
    verdict = {
        "verified": verified,
        "tests_run": tests_run,
        "tests_passed": tests_passed,
    }
    with open("verdict.json", "w") as fh:
        json.dump(verdict, fh)
        fh.write("\n")

    print(f"tests_run={tests_run} tests_passed={tests_passed} verified={verified}")
    if failures:
        print(f"{len(failures)} FAILURES, first few:")
        for inst, msg in failures[:10]:
            print("  ", inst, "->", msg)


if __name__ == "__main__":
    main()
