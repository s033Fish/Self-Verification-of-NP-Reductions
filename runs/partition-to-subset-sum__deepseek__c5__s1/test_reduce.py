"""Independent verification of reduce.py (Partition -> Subset Sum).

We write our own brute-force solvers for both problems from the
definitions in problems.py, then compare answers on many small source
instances and their reductions.  We also check that the reduction output
is a valid TARGET instance and that the reduction is deterministic and
does not mutate its input.
"""

from __future__ import annotations

import itertools
import random

import problems
from problems import Partition, SubsetSum
from reduce import reduce


# ----------------------------------------------------------------------
# Brute-force solvers, written directly from the problem definitions.
# ----------------------------------------------------------------------

def partition_bruteforce(instance: dict) -> bool:
    """Partition: yes iff positions split into two equal-sum groups."""
    numbers = instance["numbers"]
    total = sum(numbers)
    if total % 2 != 0:
        return False
    half = total // 2
    n = len(numbers)
    # Try every subset as one group; the complement is the other group.
    for mask in range(1 << n):
        s = 0
        for i in range(n):
            if mask & (1 << i):
                s += numbers[i]
        if s == half:
            return True
    return False


def subset_sum_bruteforce(instance: dict) -> bool:
    """SubsetSum: yes iff some sub-list sums to exactly target."""
    numbers = instance["numbers"]
    target = instance["target"]
    if target == 0:
        return True  # empty sub-list
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
# Tests
# ----------------------------------------------------------------------

tests_run = 0
tests_passed = 0
failures = []


def check(condition: bool, message: str) -> None:
    global tests_run, tests_passed
    tests_run += 1
    if condition:
        tests_passed += 1
    else:
        failures.append(message)


def check_instance(numbers, expected_partition=None):
    """Reduce a Partition instance and compare solver answers."""
    inst = {"numbers": list(numbers)}
    # Validate the source instance is well-formed.
    Partition.validate(inst)

    red = reduce(inst)

    # The reduction output must be a valid TARGET instance.
    try:
        SubsetSum.validate(red)
        valid_target = True
    except Exception as exc:  # noqa: BLE001
        valid_target = False
        check(False, f"invalid TARGET instance for {numbers}: {exc}")

    if valid_target:
        check(True, "")

    src = partition_bruteforce(inst)
    tgt = subset_sum_bruteforce(red)
    check(
        src == tgt,
        f"answer mismatch for {numbers}: partition={src}, "
        f"reduction={red}, subset_sum={tgt}",
    )

    if expected_partition is not None:
        check(
            src == expected_partition,
            f"brute-force sanity failed for {numbers}: got {src}, "
            f"expected {expected_partition}",
        )

    # reduce must not mutate its input.
    check(inst == {"numbers": list(numbers)}, f"reduce mutated input {numbers}")

    # determinism
    check(reduce(inst) == red, f"reduce not deterministic for {numbers}")

    return red


# ---- Explicit edge cases ------------------------------------------------

check_instance([], expected_partition=True)          # empty list is yes
check_instance([0], expected_partition=True)         # single zero
check_instance([0, 0, 0], expected_partition=True)   # all zeros
check_instance([1], expected_partition=False)        # odd total
check_instance([1, 2], expected_partition=False)     # total 3 odd
check_instance([1, 1], expected_partition=True)      # total 2
check_instance([1, 2, 3], expected_partition=True)   # 1+2=3, total 6
check_instance([1, 2, 4], expected_partition=False)  # total 7 odd
check_instance([2, 2], expected_partition=True)
check_instance([3, 3, 3], expected_partition=False)  # total 9 odd
check_instance([5, 5], expected_partition=True)
check_instance([2, 3, 5], expected_partition=True)   # 2+3=5
check_instance([1000000000000, 1000000000000], expected_partition=True)
check_instance([10**30, 10**30 + 1], expected_partition=False)

# ---- Exhaustive small instances ----------------------------------------

for n in range(0, 8):
    for combo in itertools.product(range(0, 6), repeat=n):
        check_instance(list(combo))

# ---- Random larger instances -------------------------------------------

rng = random.Random(12345)
for _ in range(400):
    n = rng.randint(0, 12)
    numbers = [rng.randint(0, 30) for _ in range(n)]
    check_instance(numbers)

# ---- Explicitly verify odd-total unreachability property ----------------

for _ in range(200):
    n = rng.randint(1, 10)
    numbers = [rng.randint(0, 20) for _ in range(n)]
    total = sum(numbers)
    if total % 2 == 1:
        red = reduce({"numbers": numbers})
        check(
            red["target"] == total + 1,
            f"odd total {total} should map to target {total + 1}, got {red['target']}",
        )
        check(
            red["target"] > sum(red["numbers"]),
            f"odd-total target {red['target']} must exceed max possible sum {total}",
        )

# ---- Even-total target correctness -------------------------------------

for _ in range(200):
    n = rng.randint(0, 10)
    numbers = [rng.randint(0, 20) for _ in range(n)]
    total = sum(numbers)
    if total % 2 == 0:
        red = reduce({"numbers": numbers})
        check(
            red["target"] == total // 2,
            f"even total {total} should map to target {total // 2}, got {red['target']}",
        )


print(f"tests_run={tests_run} tests_passed={tests_passed}")
if failures:
    print("FAILURES:")
    for f in failures[:20]:
        print("  -", f)
    raise SystemExit(1)
print("ALL TESTS PASSED")
