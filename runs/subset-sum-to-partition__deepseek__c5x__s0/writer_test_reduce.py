"""Tests comparing brute-force answers for Subset Sum and Partition."""

from __future__ import annotations

import itertools
import random

from problems import SOURCE, TARGET
from reduce import reduce


def subset_sum_solver(instance):
    """Brute force Subset Sum from the definition."""
    numbers = instance["numbers"]
    target = instance["target"]
    if target < 0:
        return False
    for r in range(len(numbers) + 1):
        for combo in itertools.combinations(numbers, r):
            if sum(combo) == target:
                return True
    return False


def partition_solver(instance):
    """Brute force Partition from the definition."""
    numbers = instance["numbers"]
    total = sum(numbers)
    if total % 2 != 0:
        return False
    half = total // 2
    for r in range(len(numbers) + 1):
        for combo in itertools.combinations(numbers, r):
            if sum(combo) == half:
                return True
    return False


def check(source_instance):
    """Validate, reduce, validate, and compare answers."""
    SOURCE.validate(source_instance)
    target_instance = reduce(source_instance)
    TARGET.validate(target_instance)
    expected = subset_sum_solver(source_instance)
    got = partition_solver(target_instance)
    return expected, got


def main():
    tests_run = 0
    tests_passed = 0
    failures = []

    def run(source_instance, label):
        nonlocal tests_run, tests_passed
        tests_run += 1
        try:
            expected, got = check(source_instance)
        except Exception as exc:  # noqa: BLE001
            failures.append((label, source_instance, f"exception: {exc!r}"))
            return
        if expected == got:
            tests_passed += 1
        else:
            failures.append((label, source_instance, f"expected {expected}, got {got}"))

    # Hand-picked edge cases.
    run({"numbers": [], "target": 0}, "empty/0")
    run({"numbers": [], "target": 1}, "empty/1")
    run({"numbers": [], "target": -1}, "empty/-1")
    run({"numbers": [5], "target": 0}, "single/0")
    run({"numbers": [5], "target": 5}, "single/5")
    run({"numbers": [5], "target": 3}, "single/3")
    run({"numbers": [5], "target": -3}, "single/-3")
    run({"numbers": [0, 0, 0], "target": 0}, "zeros/0")
    run({"numbers": [0, 0, 0], "target": 1}, "zeros/1")
    run({"numbers": [1, 2, 3], "target": 3}, "123/3")
    run({"numbers": [1, 2, 3], "target": 6}, "123/6")
    run({"numbers": [1, 2, 3], "target": 7}, "123/7")
    run({"numbers": [4, 4], "target": 4}, "44/4")
    run({"numbers": [4, 4], "target": 8}, "44/8")
    run({"numbers": [10**30, 1], "target": 10**30}, "huge")
    run({"numbers": [10**30, 1], "target": 1}, "huge/1")
    run({"numbers": [10**30, 1], "target": 10**30 + 1}, "huge/sum")

    # Exhaustive small cases.
    for n in range(0, 5):
        for numbers in itertools.product(range(0, 4), repeat=n):
            numbers = list(numbers)
            total = sum(numbers)
            for target in range(-2, total + 3):
                run({"numbers": numbers, "target": target}, f"exhaustive {numbers} {target}")

    # Random cases.
    rng = random.Random(12345)
    for _ in range(3000):
        n = rng.randint(0, 9)
        numbers = [rng.randint(0, 12) for _ in range(n)]
        total = sum(numbers)
        target = rng.randint(-3, total + 3)
        run({"numbers": numbers, "target": target}, "random")

    print(f"tests_run={tests_run} tests_passed={tests_passed}")
    if failures:
        for label, inst, msg in failures[:10]:
            print("FAIL", label, inst, msg)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
