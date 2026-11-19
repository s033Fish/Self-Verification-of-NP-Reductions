"""Independent verification of reduce.py (Partition -> Subset Sum).

We implement our own brute-force solvers directly from the problem
definitions in problems.py, then compare answers on many small source
instances and their reductions.
"""

from __future__ import annotations

import itertools
import random

from problems import Partition, SubsetSum
from reduce import reduce


# ----------------------------------------------------------------------
# Brute-force solvers (written from the definitions, not from reduce.py)

def partition_bruteforce(instance: dict) -> bool:
    """Yes iff positions can be split into two groups of equal sum."""
    numbers = instance["numbers"]
    total = sum(numbers)
    if total % 2 != 0:
        return False
    half = total // 2
    # Try every subset; if any sums to half, the complement also does.
    n = len(numbers)
    for mask in range(1 << n):
        s = 0
        for i in range(n):
            if mask & (1 << i):
                s += numbers[i]
        if s == half:
            return True
    return False


def subset_sum_bruteforce(instance: dict) -> bool:
    """Yes iff some sub-list (each position at most once) sums to target."""
    numbers = instance["numbers"]
    target = instance["target"]
    if target < 0:
        return False
    n = len(numbers)
    for mask in range(1 << n):
        s = 0
        for i in range(n):
            if mask & (1 << i):
                s += numbers[i]
        if s == target:
            return True
    return False


# ----------------------------------------------------------------------
# Test harness

tests_run = 0
tests_passed = 0
failures = []


def check(instance: dict, label: str) -> None:
    global tests_run, tests_passed
    tests_run += 1
    # Both instances must be valid per the problem definitions.
    Partition.validate(instance)
    src_answer = partition_bruteforce(instance)
    reduced = reduce(instance)
    SubsetSum.validate(reduced)
    tgt_answer = subset_sum_bruteforce(reduced)
    if src_answer == tgt_answer:
        tests_passed += 1
    else:
        failures.append((label, instance, src_answer, reduced, tgt_answer))


# --- Exhaustive small instances -------------------------------------
# All lists of length 0..5 with values 0..4.
for length in range(0, 6):
    for combo in itertools.product(range(0, 5), repeat=length):
        check({"numbers": list(combo)}, f"exhaustive len={length} {combo}")

# All lists of length 0..4 with values 0..7 (more variety, incl. odd totals)
for length in range(0, 5):
    for combo in itertools.product(range(0, 8), repeat=length):
        check({"numbers": list(combo)}, f"exhaustive2 len={length} {combo}")

# --- Random instances ------------------------------------------------
rng = random.Random(12345)
for _ in range(3000):
    length = rng.randint(0, 9)
    numbers = [rng.randint(0, 20) for _ in range(length)]
    check({"numbers": numbers}, f"random {numbers}")

# Random with larger values and many zeros
for _ in range(1000):
    length = rng.randint(0, 8)
    numbers = [rng.choice([0, 0, 1, 2, 3, 10, 100, 999]) for _ in range(length)]
    check({"numbers": numbers}, f"random-mixed {numbers}")

# --- Explicit edge cases --------------------------------------------
edge_cases = [
    {"numbers": []},                       # empty: yes
    {"numbers": [0]},                      # yes
    {"numbers": [0, 0, 0]},                # yes
    {"numbers": [1]},                      # odd total: no
    {"numbers": [1, 2]},                   # odd total: no
    {"numbers": [1, 1]},                   # yes
    {"numbers": [1, 3]},                   # yes (1+3 vs ... no: total 4, half 2, no)
    {"numbers": [2, 2]},                   # yes
    {"numbers": [5, 5, 5, 5]},             # yes
    {"numbers": [1, 2, 3, 4, 5]},          # odd total 15: no
    {"numbers": [1, 2, 3, 4, 6]},          # total 16, half 8: yes
    {"numbers": [10**18, 10**18]},         # huge, yes
    {"numbers": [10**18, 10**18 + 1]},     # odd total, no
    {"numbers": [10**30, 1, 10**30]},      # odd total, no
]
for inst in edge_cases:
    check(inst, f"edge {inst}")

# --- Report ----------------------------------------------------------
print(f"tests_run={tests_run}")
print(f"tests_passed={tests_passed}")
if failures:
    print(f"FAILURES ({len(failures)}):")
    for label, inst, src, red, tgt in failures[:20]:
        print(f"  {label}: src={src} reduced={red} tgt={tgt}")
else:
    print("All tests passed: reduce.py agrees with brute force on every case.")

assert tests_run == tests_passed, "some tests failed"
