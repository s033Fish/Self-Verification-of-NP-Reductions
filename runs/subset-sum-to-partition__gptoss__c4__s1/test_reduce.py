import random
import itertools
import json
from problems import SubsetSum, Partition
from reduce import reduce

def subset_sum_bruteforce(instance):
    SubsetSum.validate(instance)
    nums = instance["numbers"]
    t = instance["target"]
    n = len(nums)
    # Edge cases covered by brute force as well
    for mask in range(1 << n):
        s = 0
        for i in range(n):
            if mask & (1 << i):
                s += nums[i]
        if s == t:
            return True
    return False

def partition_bruteforce(instance):
    Partition.validate(instance)
    nums = instance["numbers"]
    total = sum(nums)
    if total % 2 != 0:
        return False
    half = total // 2
    n = len(nums)
    for mask in range(1 << n):
        s = 0
        for i in range(n):
            if mask & (1 << i):
                s += nums[i]
        if s == half:
            return True
    return False

def test_random(num_tests=200):
    for _ in range(num_tests):
        n = random.randint(0, 6)
        nums = [random.randint(0, 10) for _ in range(n)]
        t = random.randint(-5, sum(nums) + 5)
        ss_instance = {"numbers": nums, "target": t}
        # compute answers
        ans_ss = subset_sum_bruteforce(ss_instance)
        # reduction
        part_instance = reduce(ss_instance)
        ans_part = partition_bruteforce(part_instance)
        if ans_ss != ans_part:
            print("Mismatch!", ss_instance, part_instance, ans_ss, ans_part)
            return False
    return True

if __name__ == '__main__':
    ok = test_random(500)
    print('All tests passed' if ok else 'Some tests failed')
