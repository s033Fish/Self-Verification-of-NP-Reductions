"""Independent tests for reduce.py (Exact Cover -> Subset Sum).

We implement our own brute-force solvers directly from the problem
definitions in problems.py, then compare answers on many small source
instances and their reductions.
"""

from __future__ import annotations

import itertools
import random

from problems import ExactCover, SubsetSum, InvalidInstance
from reduce import reduce


# ----------------------------------------------------------------------
# Brute-force solvers written from the definitions.

def exact_cover_bruteforce(instance) -> bool:
    """Yes iff some sub-collection of sets is pairwise disjoint with union
    equal to the whole universe 0..u-1."""
    u = instance["universe_size"]
    sets = instance["sets"]
    m = len(sets)
    full = (1 << u) - 1
    for mask in range(1 << m):
        union = 0
        ok = True
        for j in range(m):
            if mask & (1 << j):
                s = 0
                for e in sets[j]:
                    s |= (1 << e)
                if union & s:  # overlap -> not disjoint
                    ok = False
                    break
                union |= s
        if ok and union == full:
            return True
    return False


def subset_sum_bruteforce(instance) -> bool:
    """Yes iff some sub-list sums to exactly target."""
    numbers = instance["numbers"]
    target = instance["target"]
    n = len(numbers)
    for mask in range(1 << n):
        total = 0
        for j in range(n):
            if mask & (1 << j):
                total += numbers[j]
        if total == target:
            return True
    return False


# ----------------------------------------------------------------------
# Test harness

tests_run = 0
tests_passed = 0
failures = []


def check(instance, label=""):
    global tests_run, tests_passed
    tests_run += 1
    try:
        ExactCover.validate(instance)
    except InvalidInstance as exc:
        failures.append(f"{label}: generated invalid source instance: {exc}")
        return
    expected = exact_cover_bruteforce(instance)
    try:
        out = reduce(instance)
    except Exception as exc:  # noqa: BLE001
        failures.append(f"{label}: reduce raised {type(exc).__name__}: {exc} on {instance}")
        return
    try:
        SubsetSum.validate(out)
    except InvalidInstance as exc:
        failures.append(f"{label}: reduce produced invalid target instance: {exc}")
        return
    got = subset_sum_bruteforce(out)
    if got != expected:
        failures.append(
            f"{label}: mismatch expected={expected} got={got}\n  src={instance}\n  tgt={out}"
        )
    else:
        tests_passed += 1


# ----------------------------------------------------------------------
# 1. Explicit edge cases.

edge_cases = [
    {"universe_size": 0, "sets": []},
    {"universe_size": 0, "sets": [[]]},
    {"universe_size": 0, "sets": [[], [], []]},
    {"universe_size": 1, "sets": []},
    {"universe_size": 1, "sets": [[]]},
    {"universe_size": 1, "sets": [[0]]},
    {"universe_size": 1, "sets": [[0], [0]]},
    {"universe_size": 1, "sets": [[0], [0], [0]]},
    {"universe_size": 2, "sets": [[0], [1]]},
    {"universe_size": 2, "sets": [[0, 1]]},
    {"universe_size": 2, "sets": [[0], [0], [1]]},
    {"universe_size": 2, "sets": [[0, 1], [0], [1]]},
    {"universe_size": 3, "sets": [[0, 1], [1, 2], [0, 2]]},
    {"universe_size": 3, "sets": [[0, 1], [2]]},
    {"universe_size": 3, "sets": [[0], [1], [2]]},
    {"universe_size": 3, "sets": [[0, 1, 2], [0, 1], [2]]},
    {"universe_size": 4, "sets": [[0, 1], [2, 3], [0, 2], [1, 3]]},
    {"universe_size": 4, "sets": [[0, 1, 2, 3]]},
    {"universe_size": 4, "sets": [[0], [1], [2], [3], [0, 1, 2, 3]]},
]
for i, inst in enumerate(edge_cases):
    check(inst, f"edge#{i}")


# ----------------------------------------------------------------------
# 2. Exhaustive small instances: all collections of subsets of a small
#    universe, including duplicates and empty sets.

def all_subsets(u):
    elems = list(range(u))
    subs = []
    for r in range(u + 1):
        for combo in itertools.combinations(elems, r):
            subs.append(list(combo))
    return subs


for u in range(0, 4):
    subs = all_subsets(u)
    # collections of size 0..3 drawn from subs (with repetition)
    for m in range(0, 4):
        for combo in itertools.product(range(len(subs)), repeat=m):
            inst = {"universe_size": u, "sets": [list(subs[k]) for k in combo]}
            check(inst, f"exhaustive u={u} m={m} combo={combo}")


# ----------------------------------------------------------------------
# 3. Random small instances.

rng = random.Random(12345)
for trial in range(4000):
    u = rng.randint(0, 6)
    m = rng.randint(0, 7)
    sets = []
    for _ in range(m):
        size = rng.randint(0, u) if u > 0 else 0
        elems = rng.sample(range(u), size) if u > 0 else []
        sets.append(elems)
    inst = {"universe_size": u, "sets": sets}
    check(inst, f"random#{trial}")


# ----------------------------------------------------------------------
# 4. Random instances biased toward yes-answers (build an exact cover then
#    add noise), to make sure positive cases are exercised.

for trial in range(3000):
    u = rng.randint(0, 6)
    # random partition of universe into blocks
    elems = list(range(u))
    rng.shuffle(elems)
    blocks = []
    i = 0
    while i < len(elems):
        take = rng.randint(1, max(1, len(elems) - i))
        blocks.append(sorted(elems[i:i + take]))
        i += take
    sets = [list(b) for b in blocks]
    # add noise sets
    for _ in range(rng.randint(0, 4)):
        size = rng.randint(0, u) if u > 0 else 0
        sets.append(rng.sample(range(u), size) if u > 0 else [])
    rng.shuffle(sets)
    inst = {"universe_size": u, "sets": sets}
    check(inst, f"partition#{trial}")


# ----------------------------------------------------------------------
# 5. A few larger random instances (still brute-forceable).

for trial in range(60):
    u = rng.randint(0, 8)
    m = rng.randint(0, 12)
    sets = []
    for _ in range(m):
        size = rng.randint(0, u) if u > 0 else 0
        sets.append(rng.sample(range(u), size) if u > 0 else [])
    inst = {"universe_size": u, "sets": sets}
    check(inst, f"larger#{trial}")


# ----------------------------------------------------------------------
# 6. Check reduce rejects malformed source instances (validation contract).

bad_instances = [
    {"universe_size": -1, "sets": []},
    {"universe_size": 2, "sets": [[2]]},
    {"universe_size": 2, "sets": [[0, 0]]},
    {"universe_size": 2, "sets": [[0], "x"]},
    {"universe_size": 2},
    {"sets": []},
]
for i, bad in enumerate(bad_instances):
    tests_run += 1
    try:
        reduce(bad)
    except InvalidInstance:
        tests_passed += 1
    except Exception as exc:  # noqa: BLE001
        failures.append(f"bad#{i}: expected InvalidInstance, got {type(exc).__name__}: {exc}")
    else:
        failures.append(f"bad#{i}: expected InvalidInstance, reduce accepted {bad}")


# ----------------------------------------------------------------------
# Report

print(f"tests_run={tests_run} tests_passed={tests_passed} failures={len(failures)}")
for f in failures[:20]:
    print("FAIL:", f)
if failures:
    raise SystemExit(1)
print("ALL TESTS PASSED")
