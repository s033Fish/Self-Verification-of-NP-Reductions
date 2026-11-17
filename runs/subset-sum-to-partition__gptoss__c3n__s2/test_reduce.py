import random
import itertools
import json
from problems import SubsetSum, Partition
from reduce import reduce

def subset_sum_bruteforce(instance):
    SubsetSum.validate(instance)
    nums = instance['numbers']
    target = instance['target']
    n = len(nums)
    # Edge cases per definition
    if target == 0:
        return True
    if target < 0:
        return False
    # brute force all subsets
    for mask in range(1 << n):
        s = 0
        for i in range(n):
            if mask & (1 << i):
                s += nums[i]
        if s == target:
            return True
    return False

def partition_bruteforce(instance):
    Partition.validate(instance)
    nums = instance['numbers']
    total = sum(nums)
    # Edge cases
    if total % 2 != 0:
        return False
    if not nums:
        return True
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

def run_random_tests(num_tests=200):
    passed = 0
    for _ in range(num_tests):
        # generate small instance
        length = random.randint(0, 6)
        numbers = [random.randint(0, 10) for _ in range(length)]
        target = random.randint(-5, 20)
        src = {"numbers": numbers, "target": target}
        try:
            SubsetSum.validate(src)
        except Exception as e:
            print('Invalid source', src, e)
            continue
        reduced = reduce(src)
        # compare answers
        src_ans = subset_sum_bruteforce(src)
        red_ans = partition_bruteforce(reduced)
        if src_ans == red_ans:
            passed += 1
        else:
            print('FAIL')
            print('src', src, 'src_ans', src_ans)
            print('reduced', reduced, 'red_ans', red_ans)
            break
    return passed, num_tests

if __name__ == '__main__':
    passed, total = run_random_tests()
    result = {
        "verified": passed == total,
        "tests_run": total,
        "tests_passed": passed,
    }
    print(json.dumps(result))
    with open('verdict.json', 'w') as f:
        json.dump(result, f)
