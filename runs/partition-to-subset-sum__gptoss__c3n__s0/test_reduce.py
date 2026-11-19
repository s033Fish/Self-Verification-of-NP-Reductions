import random
import itertools
import json
from problems import Partition, SubsetSum
from reduce import reduce


def partition_bruteforce(instance):
    numbers = instance["numbers"]
    total = sum(numbers)
    if total % 2 == 1:
        return False
    target = total // 2
    n = len(numbers)
    # iterate subsets
    for mask in range(1 << n):
        s = 0
        for i in range(n):
            if mask & (1 << i):
                s += numbers[i]
        if s == target:
            return True
    return False


def subset_sum_bruteforce(instance):
    numbers = instance["numbers"]
    target = instance["target"]
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


def run_tests():
    tests = []
    # edge cases
    tests.append({"numbers": []})
    tests.append({"numbers": [0,0,0]})
    tests.append({"numbers": [1]})
    tests.append({"numbers": [1,2,3]})
    tests.append({"numbers": [2,2,2,2]})
    # random small instances
    for _ in range(100):
        length = random.randint(0, 8)
        numbers = [random.randint(0, 10) for _ in range(length)]
        tests.append({"numbers": numbers})
    passed = 0
    for idx, inst in enumerate(tests):
        Partition.validate(inst)
        src_ans = partition_bruteforce(inst)
        red = reduce(inst)
        SubsetSum.validate(red)
        tgt_ans = subset_sum_bruteforce(red)
        if src_ans == tgt_ans:
            passed += 1
        else:
            print("FAIL", idx, inst, src_ans, red, tgt_ans)
    return len(tests), passed

if __name__ == "__main__":
    total, passed = run_tests()
    result = {
        "verified": passed == total,
        "tests_run": total,
        "tests_passed": passed,
    }
    print(json.dumps(result, indent=2))
    # write verdict.json
    with open('verdict.json', 'w') as f:
        json.dump(result, f)
