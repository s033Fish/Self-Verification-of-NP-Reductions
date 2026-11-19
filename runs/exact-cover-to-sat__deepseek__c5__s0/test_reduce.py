"""Independent tests for reduce.py (Exact Cover -> SAT).

problems.py provides only validate(); it has no solvers.  We implement our
own brute-force solvers directly from the definitions, then compare the
answer of each source instance with the answer of its reduction.

Checks performed:
  * hand-picked edge cases (u=0, empty sets, duplicates, uncovered elements)
  * random small instances
  * exhaustive enumeration of small instances
  * structured instances built from random partitions
  * reduce() does not mutate its input
  * the output is a valid Sat instance of polynomial size and reduce() is fast
"""

from __future__ import annotations

import copy
import itertools
import random
import time

import problems
from problems import ExactCover, Sat
from reduce import reduce


# ----------------------------------------------------------------------
# Brute-force solvers written from the definitions.

def solve_exact_cover(instance) -> bool:
    """Yes iff some sub-collection of sets partitions the universe."""
    u = instance["universe_size"]
    sets = instance["sets"]
    n = len(sets)
    full = (1 << u) - 1
    for mask in range(1 << n):
        covered = 0
        ok = True
        for i in range(n):
            if mask & (1 << i):
                s = 0
                for e in sets[i]:
                    s |= 1 << e
                if covered & s:          # chosen sets must be disjoint
                    ok = False
                    break
                covered |= s
        if ok and covered == full:
            return True
    return False


def solve_sat(instance) -> bool:
    """Yes iff some assignment satisfies every clause."""
    m = instance["num_vars"]
    clauses = instance["clauses"]
    for bits in range(1 << m):
        good = True
        for clause in clauses:
            if not any((bits >> (abs(lit) - 1)) & 1 == (1 if lit > 0 else 0)
                       for lit in clause):
                good = False
                break
        if good:
            return True
    return False


# ----------------------------------------------------------------------
# Helpers

def check_instance(inst, label, results):
    """Validate, solve, reduce, validate reduction, compare. Returns bool."""
    ExactCover.validate(inst)
    src = solve_exact_cover(inst)
    red = reduce(inst)
    Sat.validate(red)
    tgt = solve_sat(red)
    results["run"] += 1
    if src == tgt:
        results["pass"] += 1
        return True
    print(f"FAIL {label}: source={src} target={tgt}\n  inst={inst}\n  red={red}")
    return False


def random_instance(rng):
    u = rng.randint(0, 5)
    n = rng.randint(0, 6)
    sets = [rng.sample(range(u), rng.randint(0, u)) if u else []
            for _ in range(n)]
    return {"universe_size": u, "sets": sets}


def main():
    results = {"run": 0, "pass": 0}
    ok = True

    # --- Hand-picked edge cases ---
    edge = [
        {"universe_size": 0, "sets": []},
        {"universe_size": 0, "sets": [[], []]},
        {"universe_size": 1, "sets": []},
        {"universe_size": 1, "sets": [[]]},
        {"universe_size": 1, "sets": [[0]]},
        {"universe_size": 1, "sets": [[0], [0]]},
        {"universe_size": 2, "sets": [[0], [1]]},
        {"universe_size": 2, "sets": [[0, 1]]},
        {"universe_size": 2, "sets": [[0], [0, 1]]},
        {"universe_size": 2, "sets": [[0, 1], [0, 1]]},
        {"universe_size": 3, "sets": [[0, 1], [1, 2], [0, 2]]},
        {"universe_size": 3, "sets": [[0], [1], [2]]},
        {"universe_size": 3, "sets": [[0, 1, 2]]},
        {"universe_size": 3, "sets": [[0], [1], [2], [0, 1, 2]]},
        {"universe_size": 4, "sets": [[0, 1], [2, 3], [0], [1], [2], [3]]},
        {"universe_size": 4, "sets": [[0, 1, 2, 3], [0, 1], [2, 3]]},
        {"universe_size": 5, "sets": [[0, 1], [1, 2], [2, 3], [3, 4], [4, 0]]},
        {"universe_size": 5, "sets": [[0, 1, 2], [2, 3, 4], [0, 4]]},
        {"universe_size": 3, "sets": [[], [], [0], [1], [2]]},
        {"universe_size": 3, "sets": [[0], [], [1], [], [2], []]},
    ]
    for i, inst in enumerate(edge):
        if not check_instance(inst, f"edge{i}", results):
            ok = False

    # --- Random small instances ---
    rng = random.Random(12345)
    for t in range(3000):
        if not check_instance(random_instance(rng), f"random{t}", results):
            ok = False

    # --- Exhaustive small instances: u in 0..3, all collections of up to 4
    #     subsets (empties and duplicates included). ---
    for u in range(0, 4):
        subsets = []
        for r in range(u + 1):
            subsets.extend(list(c) for c in itertools.combinations(range(u), r))
        for n in range(0, 5):
            for combo in itertools.product(subsets, repeat=n):
                inst = {"universe_size": u, "sets": [list(s) for s in combo]}
                if not check_instance(inst, f"exh_u{u}_n{n}_{combo}", results):
                    ok = False

    # --- Structured instances from random partitions (+ noise) ---
    rng = random.Random(7)
    for t in range(300):
        u = rng.randint(1, 6)
        sets = []
        remaining = list(range(u))
        rng.shuffle(remaining)
        while remaining:
            k = rng.randint(1, len(remaining))
            sets.append(remaining[:k])
            remaining = remaining[k:]
        for _ in range(rng.randint(0, 4)):
            sets.append(rng.sample(range(u), rng.randint(0, u)))
        rng.shuffle(sets)
        if not check_instance({"universe_size": u, "sets": sets},
                              f"struct{t}", results):
            ok = False

    # --- Larger random instances (brute force still feasible) ---
    rng = random.Random(424242)
    for t in range(400):
        u = rng.randint(0, 6)
        n = rng.randint(0, 9)
        sets = [rng.sample(range(u), rng.randint(0, u)) if u else []
                for _ in range(n)]
        if not check_instance({"universe_size": u, "sets": sets},
                              f"large{t}", results):
            ok = False

    # --- No mutation of the input ---
    rng = random.Random(999)
    for t in range(500):
        inst = random_instance(rng)
        before = copy.deepcopy(inst)
        reduce(inst)
        results["run"] += 1
        if inst == before:
            results["pass"] += 1
        else:
            ok = False
            print("MUTATION FAIL", before, inst)

    # --- Polynomial size / fast on a large instance ---
    u, n = 300, 300
    rng = random.Random(1)
    sets = [rng.sample(range(u), rng.randint(0, 5)) for _ in range(n)]
    inst = {"universe_size": u, "sets": sets}
    t0 = time.time()
    red = reduce(inst)
    dt = time.time() - t0
    Sat.validate(red)
    results["run"] += 1
    bound = u + u * n * n
    if red["num_vars"] == n and len(red["clauses"]) <= bound:
        results["pass"] += 1
    else:
        ok = False
        print("SIZE FAIL", red["num_vars"], len(red["clauses"]), bound)
    print(f"large instance: {len(red['clauses'])} clauses in {dt:.4f}s (bound {bound})")

    print(f"tests_run={results['run']} tests_passed={results['pass']}")
    print("ALL PASS" if ok else "SOME FAILED")
    return ok, results


if __name__ == "__main__":
    main()
