import random
import itertools
import json
from problems import Partition, SubsetSum
from reduce import reduce

def partition_bruteforce(instance):
    numbers = instance["numbers"]
    total = sum(numbers)
    if total % 2 != 0:
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
    if target == 0:
        return True
    n = len(numbers)
    for mask in range(1 << n):
        s = 0
        for i in range(n):
            if mask & (1 << i):
                s += numbers[i]
        if s == target:
            return True
    return False


def run_tests(num_trials=200):
    passed = 0
    for _ in range(num_trials):
        length = random.randint(0, 6)
        numbers = [random.randint(0, 10) for _ in range(length)]
        part_inst = {"numbers": numbers}
        # validate
        Partition.validate(part_inst)
        reduced = reduce(part_inst)
        # check reduction correctness
        part_ans = partition_bruteforce(part_inst)
        subset_ans = subset_sum_bruteforce(reduced)
        if part_ans == subset_ans:
            passed += 1
        else:
            print("FAIL", part_inst, reduced, part_ans, subset_ans)
            break
    return passed, num_trials

if __name__ == "__main__":
    passed, total = run_tests(500)
    result = {
        "verified": passed == total,
        "tests_run": total,
        "tests_passed": passed,
    }
    print(json.dumps(result))
    with open("verdict.json", "w") as f:
        json.dump(result, f)
