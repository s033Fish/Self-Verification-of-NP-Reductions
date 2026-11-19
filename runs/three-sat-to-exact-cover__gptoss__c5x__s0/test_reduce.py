"""Independent checks for reduce.py (3-SAT -> Exact Cover).

We implement our own brute-force solvers for both problems straight from the
definitions in problems.py, then:

  1. check answer-equivalence on many small source instances,
  2. check the produced target instances are valid,
  3. check the polynomial-time requirement.
"""

from __future__ import annotations

import itertools
import random
import signal
import time

from problems import ThreeSat, ExactCover
from reduce import reduce


# ----------------------------------------------------------------------
# Brute-force solvers written from the problem definitions.

def solve_three_sat(instance):
    """Return True iff the 3-SAT instance is satisfiable (brute force)."""
    num_vars = instance["num_vars"]
    clauses = instance["clauses"]
    for bits in itertools.product([False, True], repeat=num_vars):
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


def solve_exact_cover(instance):
    """Return True iff the Exact Cover instance has an exact cover."""
    u = instance["universe_size"]
    sets = instance["sets"]
    target = set(range(u))
    n = len(sets)
    for mask in range(1 << n):
        chosen = [sets[i] for i in range(n) if (mask >> i) & 1]
        flat = [e for s in chosen for e in s]
        if len(flat) != len(set(flat)):
            continue  # overlapping chosen sets
        if set(flat) == target:
            return True
    return False


# ----------------------------------------------------------------------
# Tiny test harness that counts individual checks.

class Harness:
    def __init__(self):
        self.run = 0
        self.passed = 0
        self.failures = []

    def check(self, name, condition):
        self.run += 1
        if condition:
            self.passed += 1
        else:
            self.failures.append(name)


def all_clauses(num_vars):
    """All valid 3-literal clauses over variables 1..num_vars."""
    out = []
    for combo in itertools.combinations(range(1, num_vars + 1), 3):
        for signs in itertools.product([1, -1], repeat=3):
            out.append([v * s for v, s in zip(combo, signs)])
    return out


def random_formula(rng, num_vars, num_clauses):
    clauses = []
    for _ in range(num_clauses):
        vs = rng.sample(range(1, num_vars + 1), 3)
        clauses.append([v * rng.choice([1, -1]) for v in vs])
    return {"num_vars": num_vars, "clauses": clauses}


def main():
    h = Harness()
    rng = random.Random(12345)

    # ---- 1. Exhaustive small instances (num_vars <= 3) ----
    for num_vars in range(0, 4):
        clauses = all_clauses(num_vars)
        # For num_vars <= 3 there are at most 8 clauses -> all subsets.
        for r in range(len(clauses) + 1):
            for subset in itertools.combinations(range(len(clauses)), r):
                inst = {"num_vars": num_vars, "clauses": [clauses[i] for i in subset]}
                ThreeSat.validate(inst)
                expected = solve_three_sat(inst)
                out = reduce(inst)
                ExactCover.validate(out)
                got = solve_exact_cover(out)
                h.check(
                    f"exhaustive nv={num_vars} clauses={inst['clauses']}",
                    expected == got,
                )

    # ---- 2. Random small instances ----
    for _ in range(400):
        num_vars = rng.randint(0, 6)
        num_clauses = rng.randint(0, 12)
        if num_vars < 3:
            num_clauses = 0
        inst = random_formula(rng, num_vars, num_clauses)
        ThreeSat.validate(inst)
        expected = solve_three_sat(inst)
        out = reduce(inst)
        ExactCover.validate(out)
        got = solve_exact_cover(out)
        h.check(f"random {inst}", expected == got)

    # ---- 3. Explicit edge cases ----
    edge = [
        {"num_vars": 0, "clauses": []},
        {"num_vars": 5, "clauses": []},
        {"num_vars": 3, "clauses": [[1, 2, 3]]},
        {"num_vars": 3, "clauses": [[1, 2, 3], [-1, -2, -3]]},
        {"num_vars": 3, "clauses": [[1, 2, 3], [1, 2, -3], [1, -2, 3],
                                    [1, -2, -3], [-1, 2, 3], [-1, 2, -3],
                                    [-1, -2, 3], [-1, -2, -3]]},
    ]
    for inst in edge:
        ThreeSat.validate(inst)
        expected = solve_three_sat(inst)
        out = reduce(inst)
        ExactCover.validate(out)
        got = solve_exact_cover(out)
        h.check(f"edge {inst}", expected == got)

    # ---- 4. Polynomial-time requirement ----
    # A formula over many variables must reduce quickly.  A correct
    # polynomial reduction would finish in well under a second here.
    class Timeout(Exception):
        pass

    def _alarm(signum, frame):
        raise Timeout()

    old = signal.signal(signal.SIGALRM, _alarm)
    try:
        for num_vars in (16, 20, 24):
            inst = {"num_vars": num_vars, "clauses": [[1, 2, 3]]}
            signal.setitimer(signal.ITIMER_REAL, 2.0)
            start = time.time()
            try:
                reduce(inst)
                elapsed = time.time() - start
                signal.setitimer(signal.ITIMER_REAL, 0)
                h.check(f"poly-time nv={num_vars} (took {elapsed:.3f}s)", elapsed < 1.0)
            except Timeout:
                signal.setitimer(signal.ITIMER_REAL, 0)
                h.check(f"poly-time nv={num_vars} (timed out >2s)", False)
    finally:
        signal.setitimer(signal.ITIMER_REAL, 0)
        signal.signal(signal.SIGALRM, old)

    print(f"tests_run={h.run} tests_passed={h.passed}")
    for f in h.failures:
        print("FAILED:", f)

    import json
    with open("verdict.json", "w") as fh:
        json.dump({"verified": h.run == h.passed, "tests_run": h.run,
                   "tests_passed": h.passed}, fh, indent=2)
    print("verdict:", "verified" if h.run == h.passed else "NOT verified")


if __name__ == "__main__":
    main()
