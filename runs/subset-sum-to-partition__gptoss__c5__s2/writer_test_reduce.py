import random
import itertools
import sys
from typing import List, Dict

from reduce import reduce as reduction
from problems import SubsetSum, Partition


def subset_sum_bruteforce(nums: List[int], target: int) -> bool:
    if target < 0:
        return False
    # empty subset covers target==0
    n = len(nums)
    for r in range(n + 1):
        for comb in itertools.combinations(range(n), r):
            if sum(nums[i] for i in comb) == target:
                return True
    return False


def partition_bruteforce(nums: List[int]) -> bool:
    total = sum(nums)
    if total % 2 != 0:
        return False
    half = total // 2
    n = len(nums)
    for r in range(n + 1):
        for comb in itertools.combinations(range(n), r):
            if sum(nums[i] for i in comb) == half:
                return True
    return False


def run_tests(num_trials: int = 500) -> int:
    passed = 0
    for _ in range(num_trials):
        n = random.randint(0, 6)
        nums = [random.randint(0, 10) for _ in range(n)]
        total = sum(nums)
        target = random.randint(-5, total + 5)
        src_instance: Dict = {"numbers": nums, "target": target}
        # validate source
        try:
            SubsetSum.validate(src_instance)
        except Exception as e:
            print('Invalid source instance', src_instance, e)
            sys.exit(1)
        src_ans = subset_sum_bruteforce(nums, target)
        red_instance = reduction(src_instance)
        # validate target
        try:
            Partition.validate(red_instance)
        except Exception as e:
            print('Invalid reduced instance', red_instance, e)
            sys.exit(1)
        tgt_ans = partition_bruteforce(red_instance["numbers"])
        if src_ans == tgt_ans:
            passed += 1
        else:
            print('FAIL')
            print('Source', src_instance, 'src_ans', src_ans)
            print('Reduced', red_instance, 'tgt_ans', tgt_ans)
            sys.exit(1)
    return passed

if __name__ == "__main__":
    total_trials = 1000
    passed = run_tests(total_trials)
    print(f'Passed {passed}/{total_trials} tests')
    # write verdict
    import json
    verdict = {"verified": passed == total_trials, "tests_run": total_trials, "tests_passed": passed}
    with open('verdict.json', 'w') as f:
        json.dump(verdict, f)
    print('Verdict written to verdict.json')
