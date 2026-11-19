import random
import sys
from typing import List, Dict

from problems import SubsetSum, Partition
from reduce import reduce as reduction


def subset_sum_bruteforce(numbers: List[int], target: int) -> bool:
    # Edge cases handled by definition
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
    # Subset sum to half
    return subset_sum_bruteforce(numbers, half)


def test_one(instance: Dict) -> bool:
    # Validate source
    SubsetSum.validate(instance)
    # Compute answers
    src_ans = subset_sum_bruteforce(instance["numbers"], instance["target"])
    red_instance = reduction(instance)
    # Validate target
    Partition.validate(red_instance)
    tgt_ans = partition_bruteforce(red_instance["numbers"])
    return src_ans == tgt_ans


def generate_random_instance(max_len=6, max_val=10) -> Dict:
    length = random.randint(0, max_len)
    numbers = [random.randint(0, max_val) for _ in range(length)]
    # target can be negative, zero, or up to sum+5
    target = random.randint(-5, sum(numbers) + 5)
    return {"numbers": numbers, "target": target}


def main():
    random.seed(0)
    tests = 200
    passed = 0
    for i in range(tests):
        inst = generate_random_instance()
        if test_one(inst):
            passed += 1
        else:
            print("Failed on instance:", inst, file=sys.stderr)
            # also show reduction
            red = reduction(inst)
            print("Reduction result:", red, file=sys.stderr)
    # write verdict file
    verdict = {
        "verified": passed == tests,
        "tests_run": tests,
        "tests_passed": passed,
    }
    import json, pathlib
    pathlib.Path("verdict.json").write_text(json.dumps(verdict))
    print(json.dumps(verdict))
    sys.exit(0 if passed == tests else 1)

if __name__ == "__main__":
    main()
