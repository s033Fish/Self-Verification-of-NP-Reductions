import random
import itertools
import json
from problems import Partition, SubsetSum
from reduce import reduce


def partition_bruteforce(instance):
    numbers = instance['numbers']
    total = sum(numbers)
    if total % 2 == 1:
        return False
    half = total // 2
    n = len(numbers)
    # iterate subsets
    for r in range(n+1):
        for combo in itertools.combinations(range(n), r):
            s = sum(numbers[i] for i in combo)
            if s == half:
                return True
    return False


def subsetsum_bruteforce(instance):
    numbers = instance['numbers']
    target = instance['target']
    if target < 0:
        return False
    if target == 0:
        return True
    n = len(numbers)
    for r in range(1, n+1):
        for combo in itertools.combinations(range(n), r):
            if sum(numbers[i] for i in combo) == target:
                return True
    return False


def run_tests(num_tests=200):
    passed = 0
    for _ in range(num_tests):
        length = random.randint(0, 8)
        numbers = [random.randint(0, 10) for _ in range(length)]
        part_inst = {'numbers': numbers}
        # validate
        Partition.validate(part_inst)
        # compute answers
        ans_part = partition_bruteforce(part_inst)
        # reduce
        sub_inst = reduce(part_inst)
        SubsetSum.validate(sub_inst)
        ans_sub = subsetsum_bruteforce(sub_inst)
        if ans_part == ans_sub:
            passed += 1
        else:
            print('FAIL', part_inst, sub_inst, ans_part, ans_sub)
            break
    return num_tests, passed

if __name__ == '__main__':
    total, ok = run_tests(500)
    verdict = {
        "verified": ok == total,
        "tests_run": total,
        "tests_passed": ok
    }
    print(json.dumps(verdict))
    with open('verdict.json', 'w') as f:
        json.dump(verdict, f)
