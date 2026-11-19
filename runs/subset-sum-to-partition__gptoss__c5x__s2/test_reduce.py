"""Independent tests for reduce.py (Subset Sum -> Partition).

We implement our own brute-force solvers directly from the problem
definitions in problems.py, then compare solver answers on many small
source instances against the answers of their reductions.
"""

from itertools import combinations

from problems import SubsetSum, Partition
from reduce import reduce


def subset_sum_solver(instance):
    """Brute force: does any sub-list sum to target?"""
    numbers = instance["numbers"]
    target = instance["target"]
    n = len(numbers)
    for r in range(n + 1):
        for combo in combinations(range(n), r):
            if sum(numbers[i] for i in combo) == target:
                return True
    return False


def partition_solver(instance):
    """Brute force: can positions be split into two equal-sum groups?"""
    numbers = instance["numbers"]
    total = sum(numbers)
    if total % 2 != 0:
        return False
    half = total // 2
    n = len(numbers)
    for r in range(n + 1):
        for combo in combinations(range(n), r):
            if sum(numbers[i] for i in combo) == half:
                return True
    return False


def main():
    tests_run = 0
    tests_passed = 0

    # Exhaustive small instances: lengths 0..6, values in {0,1,2,3},
    # targets from -2 through total+2.
    import itertools

    failures = []
    for n in range(0, 7):
        for numbers in itertools.product([0, 1, 2, 3], repeat=n):
            numbers = list(numbers)
            total = sum(numbers)
            for target in range(-2, total + 3):
                src = {"numbers": numbers, "target": target}
                SubsetSum.validate(src)
                expected = subset_sum_solver(src)
                red = reduce(src)
                Partition.validate(red)
                got = partition_solver(red)
                tests_run += 1
                if expected == got:
                    tests_passed += 1
                else:
                    failures.append((src, expected, red, got))

    # A few larger random instances for extra confidence.
    import random
    random.seed(12345)
    for _ in range(3000):
        n = random.randint(0, 12)
        numbers = [random.randint(0, 8) for _ in range(n)]
        total = sum(numbers)
        target = random.randint(-3, total + 3)
        src = {"numbers": numbers, "target": target}
        SubsetSum.validate(src)
        expected = subset_sum_solver(src)
        red = reduce(src)
        Partition.validate(red)
        got = partition_solver(red)
        tests_run += 1
        if expected == got:
            tests_passed += 1
        else:
            failures.append((src, expected, red, got))

    for f in failures[:10]:
        print("FAIL", f)
    print(f"tests_run={tests_run} tests_passed={tests_passed} failures={len(failures)}")
    return tests_run, tests_passed, len(failures)


if __name__ == "__main__":
    main()
