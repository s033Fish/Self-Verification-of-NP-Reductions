import random
import sys
from typing import List

from reduce import reduce as reduction
from problems import SubsetSum, Partition


def subset_sum_bruteforce(numbers: List[int], target: int) -> bool:
    # Edge cases as per definition
    if target == 0:
        return True
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


def partition_bruteforce(numbers: List[int]) -> bool:
    total = sum(numbers)
    if total % 2 != 0:
        return False
    half = total // 2
    n = len(numbers)
    for mask in range(1 << n):
        s = 0
        for i in range(n):
            if mask & (1 << i):
                s += numbers[i]
        if s == half:
            return True
    return False


def run_tests(num_tests: int = 2000) -> int:
    passed = 0
    for _ in range(num_tests):
        length = random.randint(0, 6)
        numbers = [random.randint(0, 10) for _ in range(length)]
        target = random.randint(-5, 15)
        src_instance = {"numbers": numbers, "target": target}
        # Validate input (will raise if invalid)
        SubsetSum.validate(src_instance)
        src_ans = subset_sum_bruteforce(numbers, target)
        # Reduce
        tgt_instance = reduction(src_instance)
        Partition.validate(tgt_instance)
        tgt_ans = partition_bruteforce(tgt_instance["numbers"])
        if src_ans == tgt_ans:
            passed += 1
        else:
            print("Mismatch!", src_instance, src_ans, tgt_instance, tgt_ans, file=sys.stderr)
            break
    return passed

if __name__ == "__main__":
    total = 2000
    passed = run_tests(total)
    result = {
        "verified": passed == total,
        "tests_run": total,
        "tests_passed": passed,
    }
    import json
    with open("verdict.json", "w") as f:
        json.dump(result, f)
    print(json.dumps(result, indent=2))
    sys.exit(0 if result["verified"] else 1)

