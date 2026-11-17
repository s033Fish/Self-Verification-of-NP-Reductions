import random
import itertools
import json
from problems import SubsetSum, Partition
from reduce import reduce

def subset_sum_bruteforce(instance):
    SubsetSum.validate(instance)
    nums = instance['numbers']
    t = instance['target']
    if t == 0:
        return True
    if t < 0:
        return False
    n = len(nums)
    for mask in range(1 << n):
        s = 0
        for i in range(n):
            if mask >> i & 1:
                s += nums[i]
        if s == t:
            return True
    return False

def partition_bruteforce(instance):
    Partition.validate(instance)
    nums = instance['numbers']
    total = sum(nums)
    if total % 2 != 0:
        return False
    target = total // 2
    n = len(nums)
    for mask in range(1 << n):
        s = 0
        for i in range(n):
            if mask >> i & 1:
                s += nums[i]
        if s == target:
            return True
    return True if total == 0 else False

def run_random_tests(num_tests=200):
    passed = 0
    for _ in range(num_tests):
        length = random.randint(0, 6)
        nums = [random.randint(0, 5) for _ in range(length)]
        target = random.randint(-3, sum(nums) + 3)
        src = {'numbers': nums, 'target': target}
        # compute answers
        ans_src = subset_sum_bruteforce(src)
        red = reduce(src)
        ans_tgt = partition_bruteforce(red)
        if ans_src == ans_tgt:
            passed += 1
        else:
            print('FAIL')
            print('src', src)
            print('reduction', red)
            print('src ans', ans_src, 'tgt ans', ans_tgt)
            break
    return passed, num_tests

if __name__ == '__main__':
    passed, total = run_random_tests(500)
    print(f'Passed {passed}/{total} tests')
    # write verdict.json
    verdict = {
        'verified': passed == total,
        'tests_run': total,
        'tests_passed': passed,
    }
    with open('verdict.json', 'w') as f:
        json.dump(verdict, f)
    print('Verdict written to verdict.json')
