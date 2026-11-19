"""Test suite for the reduction from Subset Sum to Partition.

The repository provides only validation functions for the two problems.
This test implements straightforward (exponential) solvers for both
problems and checks that the reduction defined in ``reduce.py`` preserves
the answer on a large collection of small random instances as well as on
all exhaustive instances up to a modest size.

The script prints a JSON object with the fields required for the final
``verdict.json`` file:

    {"verified": <bool>, "tests_run": <int>, "tests_passed": <int>}

If any test fails, ``verified`` will be ``false``.
"""

from __future__ import annotations

import json
import itertools
import random
import sys
from pathlib import Path

# Import the problem definitions and the reduction implementation.
import problems  # noqa: E402  (module is in the working directory)
import reduce as reduction  # noqa: E402


def subset_sum_bruteforce(numbers: list[int], target: int) -> bool:
    """Return True iff some sub‑list of *numbers* sums to *target*.

    This is a simple exponential‑time solver suitable for tiny inputs.
    """
    n = len(numbers)
    # Early edge cases matching the specification.
    if target == 0:
        return True
    if target < 0:
        return False
    for mask in range(1 << n):
        s = 0
        for i in range(n):
            if mask >> i & 1:
                s += numbers[i]
        if s == target:
            return True
    return False


def partition_bruteforce(numbers: list[int]) -> bool:
    """Return True iff *numbers* can be split into two groups of equal sum.
    """
    total = sum(numbers)
    # Odd total cannot be partitioned.
    if total % 2:
        return False
    half = total // 2
    # Find a subset that sums to half.
    return subset_sum_bruteforce(numbers, half)


def generate_random_instance(max_len: int = 5, max_val: int = 5) -> dict:
    length = random.randint(0, max_len)
    numbers = [random.randint(0, max_val) for _ in range(length)]
    # target may be negative as well.
    target = random.randint(-max_val, max_val * length)
    return {"numbers": numbers, "target": target}


def run_tests() -> tuple[int, int]:
    """Execute a mixture of exhaustive and random tests.

    Returns a tuple ``(tests_run, tests_passed)``.
    """
    tests_run = 0
    tests_passed = 0

    # Exhaustive enumeration for very small instances to catch corner cases.
    for length in range(0, 4):  # up to 3 elements
        for numbers in itertools.product(range(0, 4), repeat=length):
            for target in range(-2, 9):
                instance = {"numbers": list(numbers), "target": target}
                # Validate the source instance according to the problem definition.
                try:
                    problems.SubsetSum.validate(instance)
                except Exception:
                    # Skip malformed instances – there should be none for the ranges used.
                    continue
                # Compute expected answers.
                expected_source = subset_sum_bruteforce(instance["numbers"], instance["target"])
                # Apply reduction.
                reduced = reduction.reduce(instance)
                # Validate the target instance.
                try:
                    problems.Partition.validate(reduced)
                except Exception as e:
                    print("Invalid reduced instance", reduced, e, file=sys.stderr)
                    continue
                expected_target = partition_bruteforce(reduced["numbers"])
                tests_run += 1
                if expected_source == expected_target:
                    tests_passed += 1
                else:
                    print(
                        "Mismatch! source", instance,
                        "expected", expected_source,
                        "reduced", reduced,
                        "target answer", expected_target,
                        file=sys.stderr,
                    )

    # Additional random tests for slightly larger inputs.
    random.seed(0)
    for _ in range(2000):
        instance = generate_random_instance(max_len=6, max_val=7)
        try:
            problems.SubsetSum.validate(instance)
        except Exception:
            continue
        expected_source = subset_sum_bruteforce(instance["numbers"], instance["target"])
        reduced = reduction.reduce(instance)
        try:
            problems.Partition.validate(reduced)
        except Exception as e:
            print("Invalid reduced instance (random)", reduced, e, file=sys.stderr)
            continue
        expected_target = partition_bruteforce(reduced["numbers"])
        tests_run += 1
        if expected_source == expected_target:
            tests_passed += 1
        else:
            print(
                "Random mismatch! source", instance,
                "expected", expected_source,
                "reduced", reduced,
                "target answer", expected_target,
                file=sys.stderr,
            )

    return tests_run, tests_passed


if __name__ == "__main__":
    run, passed = run_tests()
    verified = run == passed
    result = {"verified": verified, "tests_run": run, "tests_passed": passed}
    # Write the verdict file as required by the task description.
    Path("verdict.json").write_text(json.dumps(result, indent=2))
    print(json.dumps(result))

