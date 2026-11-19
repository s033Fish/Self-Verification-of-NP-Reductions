import json
import itertools
import random
import sys
from problems import Partition, SubsetSum
from reduce import reduce

def partition_bruteforce(nums):
    total = sum(nums)
    if total % 2 != 0:
        return False
    target = total // 2
    n = len(nums)
    # iterate subsets
    for mask in range(1 << n):
        s = 0
        for i in range(n):
            if mask & (1 << i):
                s += nums[i]
        if s == target:
            return True
    return False

def subset_sum_bruteforce(nums, target):
    if target < 0:
        return False
    n = len(nums)
    for mask in range(1 << n):
        s = 0
        for i in range(n):
            if mask & (1 << i):
                s += nums[i]
        if s == target:
            return True
    return False

def run_tests():
    tests_run = 0
    tests_passed = 0
    # generate deterministic small instances
    for length in range(0, 7):
        # values 0..4
        for nums in itertools.product(range(5), repeat=length):
            nums = list(nums)
            # validate Partition instance
            try:
                Partition.validate({"numbers": nums})
            except Exception as e:
                print("Invalid Partition instance", nums, e)
                continue
            src_ans = partition_bruteforce(nums)
            reduced = reduce({"numbers": nums})
            # validate SubsetSum instance
            try:
                SubsetSum.validate(reduced)
            except Exception as e:
                print("Invalid SubsetSum instance", reduced, e)
                continue
            tgt_ans = subset_sum_bruteforce(reduced["numbers"], reduced["target"])
            tests_run += 1
            if src_ans == tgt_ans:
                tests_passed += 1
            else:
                print("Mismatch!", nums, src_ans, reduced, tgt_ans)
    # also random tests
    random.seed(0)
    for _ in range(200):
        length = random.randint(0, 10)
        nums = [random.randint(0, 20) for _ in range(length)]
        try:
            Partition.validate({"numbers": nums})
        except Exception:
            continue
        src_ans = partition_bruteforce(nums)
        reduced = reduce({"numbers": nums})
        try:
            SubsetSum.validate(reduced)
        except Exception:
            continue
        tgt_ans = subset_sum_bruteforce(reduced["numbers"], reduced["target"])
        tests_run += 1
        if src_ans == tgt_ans:
            tests_passed += 1
        else:
            print("Random mismatch!", nums, src_ans, reduced, tgt_ans)
    return tests_run, tests_passed

if __name__ == "__main__":
    run, passed = run_tests()
    verdict = {
        "verified": run == passed,
        "tests_run": run,
        "tests_passed": passed,
    }
    print(json.dumps(verdict, indent=2))
    with open("verdict.json", "w") as f:
        json.dump(verdict, f)
