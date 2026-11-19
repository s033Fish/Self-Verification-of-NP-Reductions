"""Independent checks that reduce.py is a correct reduction 3-SAT -> 3-Coloring.

problems.py provides only validate(), so we implement our own brute-force
solvers from the documented definitions, then compare solver answers on many
small source instances with solver answers on their reductions.

Running this file writes verdict.json with the observed counts.
"""
from __future__ import annotations

import itertools
import json
import random
import time

from problems import ThreeSat, ThreeColoring
from reduce import reduce


# ----------------------------------------------------------------------
# Brute-force solvers written from the definitions.

def sat_solve(instance) -> bool:
    """True iff some assignment satisfies every clause."""
    num_vars = instance["num_vars"]
    clauses = instance["clauses"]
    for bits in itertools.product((False, True), repeat=num_vars):
        good = True
        for clause in clauses:
            if not any(
                (bits[abs(lit) - 1] if lit > 0 else not bits[abs(lit) - 1])
                for lit in clause
            ):
                good = False
                break
        if good:
            return True
    return False


def color_solve(instance) -> bool:
    """True iff the graph is 3-colourable (backtracking)."""
    n = instance["n"]
    adj = [set() for _ in range(n)]
    for u, v in instance["edges"]:
        adj[u].add(v)
        adj[v].add(u)
    colour = [-1] * n

    def bt(i: int) -> bool:
        if i == n:
            return True
        for c in range(3):
            if all(colour[j] != c for j in adj[i] if j < i):
                colour[i] = c
                if bt(i + 1):
                    return True
                colour[i] = -1
        return False

    return bt(0)


# ----------------------------------------------------------------------
# Generators for valid source instances.

def all_clauses(num_vars):
    out = []
    for combo in itertools.combinations(range(1, num_vars + 1), 3):
        for signs in itertools.product((1, -1), repeat=3):
            out.append([s * v for s, v in zip(signs, combo)])
    return out


def gen_random(rng, max_vars=5, max_clauses=8):
    m = rng.randint(0, max_vars)
    clauses = []
    if m >= 3:
        for _ in range(rng.randint(0, max_clauses)):
            vs = rng.sample(range(1, m + 1), 3)
            clauses.append([v if rng.random() < 0.5 else -v for v in vs])
    return {"num_vars": m, "clauses": clauses}


def gen_all_small():
    """Exhaustive: every subset of the 8 clauses over 3 variables."""
    base = all_clauses(3)
    insts = []
    for r in range(len(base) + 1):
        for subset in itertools.combinations(base, r):
            insts.append({"num_vars": 3, "clauses": [list(c) for c in subset]})
    return insts


def gen_structured():
    insts = []
    for m in range(0, 6):                       # no clauses: always yes
        insts.append({"num_vars": m, "clauses": []})
    insts.append({"num_vars": 3, "clauses": [[1, 2, 3], [1, 2, 3], [1, 2, 3]]})
    insts.append({"num_vars": 3, "clauses": [[1, 2, 3], [-1, -2, -3],
                                             [1, 2, -3], [1, -2, 3],
                                             [-1, 2, 3], [-1, -2, 3],
                                             [1, -2, -3], [-1, 2, -3]]})
    insts.append({"num_vars": 5, "clauses": [[1, 2, 3]]})
    insts.append({"num_vars": 5, "clauses": [[3, 4, 5], [-3, -4, -5]]})
    insts.append({"num_vars": 4, "clauses": [[1, 2, 3], [-1, 2, 3], [1, -2, 3],
                                             [1, 2, -3], [-1, -2, -3]]})
    return insts


def main():
    tests_run = 0
    tests_passed = 0
    failures = []

    def check(inst, label):
        nonlocal tests_run, tests_passed
        tests_run += 1
        try:
            ThreeSat.validate(inst)
        except Exception as exc:  # noqa: BLE001
            failures.append(f"{label}: source invalid: {exc}")
            return
        red = reduce(inst)
        try:
            ThreeColoring.validate(red)
        except Exception as exc:  # noqa: BLE001
            failures.append(f"{label}: reduction invalid: {exc}")
            return
        want = sat_solve(inst)
        got = color_solve(red)
        if want == got:
            tests_passed += 1
        else:
            failures.append(f"{label}: sat={want} color={got} inst={inst}")

    for i, inst in enumerate(gen_all_small()):
        check(inst, f"exhaustive3[{i}]")
    for i, inst in enumerate(gen_structured()):
        check(inst, f"structured[{i}]")

    rng = random.Random(12345)
    for i in range(400):
        check(gen_random(rng), f"random[{i}]")
    rng2 = random.Random(999)
    for i in range(200):
        check(gen_random(rng2, max_vars=4, max_clauses=6), f"random4[{i}]")

    # Polynomial-time sanity check: large instance must reduce quickly.
    big = {"num_vars": 60,
           "clauses": [[(i % 60) + 1, ((i + 7) % 60) + 1, ((i + 19) % 60) + 1]
                       for i in range(200)]}
    t0 = time.time()
    red_big = reduce(big)
    dt = time.time() - t0
    poly_ok = dt < 5.0 and red_big["n"] > 0
    tests_run += 1
    if poly_ok:
        tests_passed += 1
    else:
        failures.append(f"polynomial-time check failed (dt={dt})")

    verified = len(failures) == 0
    verdict = {"verified": verified, "tests_run": tests_run,
               "tests_passed": tests_passed}
    with open("verdict.json", "w") as fh:
        json.dump(verdict, fh)

    print(f"tests_run={tests_run} tests_passed={tests_passed}")
    print(f"failures={len(failures)}")
    for f in failures[:10]:
        print("  FAIL:", f)
    print("verdict:", verdict)
    return verdict


if __name__ == "__main__":
    main()
