"""Compare brute-force answers on source instances and their reductions."""

from __future__ import annotations

import itertools
import random

from problems import SOURCE, TARGET
from reduce import reduce
from solvers import partition_yes, subset_sum_yes


def check(instance: dict) -> bool:
    SOURCE.validate(instance)
    reduced = reduce(instance)
    TARGET.validate(reduced)
    src = subset_sum_yes(instance)
    tgt = partition_yes(reduced)
    assert src == tgt, (instance, reduced, src, tgt)
    return True


def main() -> None:
    tests_run = 0
    tests_passed = 0

    def run(instance: dict) -> None:
        nonlocal tests_run, tests_passed
        tests_run += 1
        if check(instance):
            tests_passed += 1

    # Exhaustive small cases: all lists over 0..4 of length 0..4, all targets.
    values = [0, 1, 2, 3, 4]
    for length in range(0, 5):
        for numbers in itertools.product(values, repeat=length):
            for target in range(-2, sum(numbers) + 3):
                run({"numbers": list(numbers), "target": target})

    # Random larger cases.
    rng = random.Random(12345)
    for _ in range(3000):
        length = rng.randint(0, 12)
        numbers = [rng.randint(0, 20) for _ in range(length)]
        target = rng.randint(-3, sum(numbers) + 3)
        run({"numbers": numbers, "target": target})

    # Explicit edge cases.
    run({"numbers": [], "target": 0})
    run({"numbers": [], "target": 5})
    run({"numbers": [], "target": -1})
    run({"numbers": [0, 0, 0], "target": 0})
    run({"numbers": [0, 0, 0], "target": 1})
    run({"numbers": [5], "target": 5})
    run({"numbers": [5], "target": 0})
    run({"numbers": [5], "target": 3})
    run({"numbers": [10**18, 10**18], "target": 10**18})
    run({"numbers": [10**18, 10**18 + 1], "target": 10**18})

    print(f"tests_run={tests_run} tests_passed={tests_passed}")
    assert tests_run == tests_passed, "some tests failed"

    import json

    with open("verdict.json", "w") as fh:
        json.dump(
            {"verified": True, "tests_run": tests_run, "tests_passed": tests_passed},
            fh,
        )


if __name__ == "__main__":
    main()
