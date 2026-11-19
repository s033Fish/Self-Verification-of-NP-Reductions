import itertools
import random
import json
from problems import Partition, SubsetSum
from reduce import reduce

def solve_partition_bruteforce(instance):
    Partition.validate(instance)
    nums = instance["numbers"]
    total = sum(nums)
    if total % 2 != 0:
        return False
    target = total // 2
    n = len(nums)
    # enumerate subsets
    for mask in range(1 << n):
        s = 0
        for i in range(n):
            if mask & (1 << i):
                s += nums[i]
        if s == target:
            return True
    return False

def solve_subset_sum_bruteforce(instance):
    SubsetSum.validate(instance)
    nums = instance["numbers"]
    target = instance["target"]
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


def test_random_cases(num_cases=200):
    for _ in range(num_cases):
        length = random.randint(0, 6)
        nums = [random.randint(0, 5) for _ in range(length)]
        part_inst = {"numbers": nums}
        # reduce
        ss_inst = reduce(part_inst)
        # compare answers
        ans_part = solve_partition_bruteforce(part_inst)
        ans_ss = solve_subset_sum_bruteforce(ss_inst)
        if ans_part != ans_ss:
            print("Mismatch!", part_inst, ss_inst, ans_part, ans_ss)
            return False
    return True


def test_edge_cases():
    cases = [
        {"numbers": []},
        {"numbers": [0,0,0]},
        {"numbers": [1]},
        {"numbers": [1,2,3]},
        {"numbers": [2,2,2,2]},
    ]
    for part_inst in cases:
        ss_inst = reduce(part_inst)
        if solve_partition_bruteforce(part_inst) != solve_subset_sum_bruteforce(ss_inst):
            print("Edge mismatch", part_inst, ss_inst)
            return False
    return True

if __name__ == "__main__":
    ok = test_random_cases() and test_edge_cases()
    result = {
        "verified": ok,
        "tests_run": 1,
        "tests_passed": int(ok)
    }
    with open('verdict.json', 'w') as f:
        json.dump(result, f)
    print(json.dumps(result))
