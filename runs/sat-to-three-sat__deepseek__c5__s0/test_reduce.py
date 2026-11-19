"""Independent tests for reduce.py: SAT -> 3-SAT.

We implement brute-force solvers for both problems directly from the
docstrings in problems.py, then compare answers on many small instances.
"""

from __future__ import annotations

import itertools
import json
import random

import problems
from problems import Sat, ThreeSat
from reduce import reduce


# ----------------------------------------------------------------------
# Brute-force solvers (one generic CNF solver works for both problems).

def solve_cnf(instance: dict) -> bool:
    """True iff some assignment satisfies every clause.

    Works for SAT and 3-SAT (both are CNF).  An empty clause makes the
    formula unsatisfiable; no clauses makes it satisfiable.
    """
    m = instance["num_vars"]
    clauses = instance["clauses"]
    for bits in itertools.product((False, True), repeat=m):
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


# ----------------------------------------------------------------------
# Instance generators.

def random_clause(rng: random.Random, m: int, max_len: int) -> list[int]:
    length = rng.randint(0, max_len)
    clause = []
    for _ in range(length):
        if m == 0:
            break
        v = rng.randint(1, m)
        clause.append(v if rng.random() < 0.5 else -v)
    return clause


def random_sat(rng: random.Random, max_vars: int = 4, max_clauses: int = 5,
               max_len: int = 6) -> dict:
    m = rng.randint(0, max_vars)
    n = rng.randint(0, max_clauses)
    return {
        "num_vars": m,
        "clauses": [random_clause(rng, m, max_len) for _ in range(n)],
    }


# ----------------------------------------------------------------------
# Test harness.

class Counter:
    def __init__(self) -> None:
        self.run = 0
        self.passed = 0
        self.failures: list[str] = []

    def check(self, condition: bool, message: str) -> None:
        self.run += 1
        if condition:
            self.passed += 1
        else:
            self.failures.append(message)


def check_instance(c: Counter, inst: dict) -> None:
    """Validate source, reduce, validate target, compare answers."""
    label = repr(inst)
    try:
        Sat.validate(inst)
    except problems.InvalidInstance as exc:  # pragma: no cover
        c.check(False, f"source invalid {label}: {exc}")
        return

    src_answer = solve_cnf(inst)

    try:
        out = reduce(inst)
    except Exception as exc:  # noqa: BLE001
        c.check(False, f"reduce raised on {label}: {exc!r}")
        return

    # Target must be a valid 3-SAT instance.
    try:
        ThreeSat.validate(out)
        valid_target = True
        err = ""
    except problems.InvalidInstance as exc:
        valid_target = False
        err = str(exc)

    c.check(valid_target, f"target invalid for {label}: {err}")

    # Target must keep the same number of *original* variables available
    # (fresh variables may be added, so only require >=).
    c.check(
        out["num_vars"] >= inst["num_vars"],
        f"target num_vars shrank for {label}: {out['num_vars']}",
    )

    if valid_target:
        tgt_answer = solve_cnf(out)
        c.check(
            src_answer == tgt_answer,
            f"answer mismatch for {label}: source={src_answer} target={tgt_answer} out={out}",
        )


def main() -> None:
    c = Counter()
    rng = random.Random(12345)

    # --- Hand-picked edge cases -------------------------------------
    edge_cases = [
        {"num_vars": 0, "clauses": []},                       # yes
        {"num_vars": 0, "clauses": [[]]},                     # no
        {"num_vars": 3, "clauses": []},                       # yes
        {"num_vars": 1, "clauses": [[1]]},                    # yes
        {"num_vars": 1, "clauses": [[-1]]},                   # yes
        {"num_vars": 1, "clauses": [[1], [-1]]},              # no
        {"num_vars": 2, "clauses": [[1, 2], [-1, -2], [1, -2], [-1, 2]]},  # no
        {"num_vars": 2, "clauses": [[1, -1]]},                # yes (tautology)
        {"num_vars": 2, "clauses": [[1, 1, -1, 2]]},          # yes
        {"num_vars": 4, "clauses": [[1, 2, 3, 4]]},           # yes
        {"num_vars": 4, "clauses": [[-1, -2, -3, -4]]},       # yes
        {"num_vars": 4, "clauses": [[1, 2, 3, 4], [-1], [-2], [-3], [-4]]},  # no
        {"num_vars": 5, "clauses": [[1, 2, 3, 4, 5]]},        # yes
        {"num_vars": 5, "clauses": [[-1, -2, -3, -4, -5]]},   # yes
        {"num_vars": 6, "clauses": [[1, 2, 3, 4, 5, 6]]},     # yes
        {"num_vars": 6, "clauses": [[-1, -2, -3, -4, -5, -6]]},  # yes
        {"num_vars": 3, "clauses": [[1, 2, 3], [1, 2, 3]]},   # yes
        {"num_vars": 3, "clauses": [[1, 2, 3], [-1, -2, -3], [1, 2, -3], [1, -2, 3], [-1, 2, 3], [1, -2, -3], [-1, 2, -3], [-1, -2, 3]]},  # no
    ]
    for inst in edge_cases:
        check_instance(c, inst)

    # --- Exhaustive small instances ---------------------------------
    # All formulas over 0..2 variables with 0, 1 or 2 clauses of length 0..3.
    for m in range(0, 3):
        pool = [lit for v in range(1, m + 1) for lit in (v, -v)]
        clauses = [[]]
        for length in range(1, 4):
            clauses.extend([list(t) for t in itertools.product(pool, repeat=length)])
        formulas = [[]]
        formulas.extend([[cl] for cl in clauses])
        formulas.extend([[a, b] for a in clauses for b in clauses])
        for f in formulas:
            check_instance(c, {"num_vars": m, "clauses": f})

    # --- Random instances -------------------------------------------
    for _ in range(4000):
        inst = random_sat(rng, max_vars=5, max_clauses=6, max_len=7)
        check_instance(c, inst)

    # --- Random instances biased toward long clauses ----------------
    for _ in range(2000):
        m = rng.randint(3, 6)
        n = rng.randint(1, 4)
        clauses = []
        for _ in range(n):
            length = rng.randint(3, 8)
            clauses.append([rng.choice([1, -1]) * rng.randint(1, m) for _ in range(length)])
        check_instance(c, {"num_vars": m, "clauses": clauses})

    print(f"tests_run={c.run} tests_passed={c.passed}")
    if c.failures:
        print(f"FAILURES ({len(c.failures)}):")
        for msg in c.failures[:20]:
            print("  " + msg)

    verdict = {
        "verified": len(c.failures) == 0,
        "tests_run": c.run,
        "tests_passed": c.passed,
    }
    with open("verdict.json", "w") as fh:
        json.dump(verdict, fh, indent=2)
    print("verdict:", verdict)


if __name__ == "__main__":
    main()
