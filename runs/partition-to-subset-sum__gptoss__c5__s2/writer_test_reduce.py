import random
import itertools
import json
from typing import List, Dict

from problems import Partition, SubsetSum
from reduce import reduce


def brute_partition(instance: Dict) -> bool:
    numbers: List[int] = instance["numbers"]
    total = sum(numbers)
    if total % 2 == 1:
        return False
    target = total // 2
    # check subset sum to target
    n = len(numbers)
    for r in range(n + 1):
        for combo in itertools.combinations(range(n), r):
            s = sum(numbers[i] for i in combo)
            if s == target:
                return True
    return False


def brute_subset_sum(instance: Dict) -> bool:
    numbers: List[int] = instance["numbers"]
    target: int = instance["target"]
    if target < 0:
        return False
    if target == 0:
        return True
    n = len(numbers)
    for r in range(1, n + 1):
        for combo in itertools.combinations(range(n), r):
            s = sum(numbers[i] for i in combo)
            if s == target:
                return True
    return False


def run_tests(num_tests: int = 500) -> int:
    passed = 0
    for _ in range(num_tests):
        size = random.randint(0, 8)
        numbers = [random.randint(0, 5) for _ in range(size)]
        instance = {"numbers": numbers}
        # validate source
        Partition.validate(instance)
        # compute answers
        ans_part = brute_partition(instance)
        reduced = reduce(instance)
        # validate target
        SubsetSum.validate(reduced)
        ans_subset = brute_subset_sum(reduced)
        if ans_part == ans_subset:
            passed += 1
        else:
            print("Mismatch!", instance, reduced, ans_part, ans_subset)
            break
    return passed

if __name__ == "__main__":
    total = 500
    passed = run_tests(total)
    verified = passed == total
    verdict = {"verified": verified, "tests_run": total, "tests_passed": passed}
    print(json.dumps(verdict))
    with open("verdict.json", "w") as f:
        json.dump(verdict, f)
