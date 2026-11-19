"""Independent brute-force checks of reduce.py (NAE-3-SAT -> 3-Coloring)."""

from __future__ import annotations

import itertools
import random

import problems
from problems import NaeThreeSat, ThreeColoring
from reduce import reduce


# ----------------------------------------------------------------------
# Brute-force solvers written from the problem definitions.

def nae3sat_solve(instance: dict) -> bool:
    """True iff some assignment makes every clause not-all-equal."""
    NaeThreeSat.validate(instance)
    m = instance["num_vars"]
    clauses = instance["clauses"]
    for bits in itertools.product((False, True), repeat=m):
        ok = True
        for clause in clauses:
            values = []
            for lit in clause:
                v = abs(lit)
                val = bits[v - 1]
                values.append(val if lit > 0 else not val)
            if all(values) or not any(values):
                ok = False
                break
        if ok:
            return True
    return False


def three_coloring_solve(instance: dict) -> bool:
    """Backtracking 3-colorability solver."""
    ThreeColoring.validate(instance)
    n = instance["n"]
    adj = [set() for _ in range(n)]
    for u, v in instance["edges"]:
        adj[u].add(v)
        adj[v].add(u)

    color = [-1] * n

    def backtrack(i: int) -> bool:
        if i == n:
            return True
        used = {color[j] for j in adj[i] if color[j] != -1}
        for c in range(3):
            if c not in used:
                color[i] = c
                if backtrack(i + 1):
                    return True
                color[i] = -1
        return False

    return backtrack(0)


# ----------------------------------------------------------------------
# Instance generators (small, valid NAE-3-SAT instances).

def random_nae_instance(rng: random.Random, max_vars: int, max_clauses: int) -> dict:
    m = rng.randint(0, max_vars)
    nclauses = rng.randint(0, max_clauses)
    clauses = []
    for _ in range(nclauses):
        if m < 3:
            break
        variables = rng.sample(range(1, m + 1), 3)
        clause = [v if rng.random() < 0.5 else -v for v in variables]
        rng.shuffle(clause)
        clauses.append(clause)
    return {"num_vars": m, "clauses": clauses}


def main() -> None:
    tests_run = 0
    tests_passed = 0
    failures = []

    def check(instance: dict, label: str) -> None:
        nonlocal tests_run, tests_passed
        tests_run += 1
        try:
            NaeThreeSat.validate(instance)
        except problems.InvalidInstance as exc:
            failures.append(f"{label}: source invalid: {exc}")
            return
        reduced = reduce(instance)
        try:
            ThreeColoring.validate(reduced)
        except problems.InvalidInstance as exc:
            failures.append(f"{label}: reduced instance invalid: {exc}\n  {reduced}")
            return
        src = nae3sat_solve(instance)
        tgt = three_coloring_solve(reduced)
        if src == tgt:
            tests_passed += 1
        else:
            failures.append(
                f"{label}: MISMATCH src={src} tgt={tgt}\n  instance={instance}\n  reduced={reduced}"
            )

    # --- Hand-picked edge cases -------------------------------------
    check({"num_vars": 0, "clauses": []}, "m=0 no clauses")
    check({"num_vars": 1, "clauses": []}, "m=1 no clauses")
    check({"num_vars": 2, "clauses": []}, "m=2 no clauses")
    check({"num_vars": 5, "clauses": []}, "m=5 no clauses")
    # Single clause, all sign combinations (always satisfiable for NAE).
    for signs in itertools.product((1, -1), repeat=3):
        clause = [signs[i] * (i + 1) for i in range(3)]
        check({"num_vars": 3, "clauses": [clause]}, f"single clause {clause}")
    # Two clauses forcing a variable to both values: still satisfiable.
    check({"num_vars": 3, "clauses": [[1, 2, 3], [-1, 2, 3]]}, "two clauses")
    # Duplicate clause.
    check({"num_vars": 3, "clauses": [[1, 2, 3], [1, 2, 3]]}, "duplicate clause")
    # Unused variables.
    check({"num_vars": 6, "clauses": [[1, 2, 3]]}, "unused vars")
    # A formula that is unsatisfiable (all 8 clauses over 3 vars are NAE-unsat
    # because for 3 vars, every assignment makes some clause all-equal; the
    # full set of 8 sign patterns is unsat for NAE).
    all_clauses = []
    for signs in itertools.product((1, -1), repeat=3):
        all_clauses.append([signs[i] * (i + 1) for i in range(3)])
    check({"num_vars": 3, "clauses": all_clauses}, "all 8 clauses (unsat)")

    # --- Random small instances -------------------------------------
    rng = random.Random(12345)
    for i in range(1500):
        inst = random_nae_instance(rng, max_vars=6, max_clauses=6)
        check(inst, f"random#{i}")

    # A few slightly larger ones.
    for i in range(60):
        inst = random_nae_instance(rng, max_vars=8, max_clauses=10)
        check(inst, f"random-large#{i}")

    print(f"tests_run={tests_run} tests_passed={tests_passed}")
    if failures:
        print(f"FAILURES ({len(failures)}):")
        for f in failures[:20]:
            print(" -", f)
    else:
        print("All checks passed.")

    import json
    verdict = {
        "verified": tests_run == tests_passed and tests_run > 0,
        "tests_run": tests_run,
        "tests_passed": tests_passed,
    }
    with open("verdict.json", "w") as fh:
        json.dump(verdict, fh)
    print("verdict:", verdict)


if __name__ == "__main__":
    main()
