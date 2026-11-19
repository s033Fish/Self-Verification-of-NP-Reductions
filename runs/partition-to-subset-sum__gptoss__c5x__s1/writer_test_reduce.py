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
    for r in range(n + 1):
        for combo in itertools.combinations(range(n), r):
            s = sum(numbers[i] for i in combo)
            if s == target:
                return True
    return False


def subset_sum_bruteforce(instance):
    numbers = instance["numbers"]
    target = instance["target"]
    if target < 0:
        return False
    n = len(numbers)
    for r in range(n + 1):
        for combo in itertools.combinations(range(n), r):
            if sum(numbers[i] for i in combo) == target:
                return True
    return False


def run_tests(num_tests=200):
    passed = 0
    for _ in range(num_tests):
        length = random.randint(0, 8)
        numbers = [random.randint(0, 10) for _ in range(length)]
        instance = {"numbers": numbers}
        # validate
        Partition.validate(instance)
        # compute answers
        ans_part = partition_bruteforce(instance)
        reduced = reduce(instance)
        ans_subset = subset_sum_bruteforce(reduced)
        if ans_part == ans_subset:
            passed += 1
        else:
            print("FAIL", instance, ans_part, reduced, ans_subset)
            break
    # edge cases
    edge_instances = [
        {"numbers": []},
        {"numbers": [0,0,0]},
        {"numbers": [1,2,3]},  # sum 6 even, yes (1+2=3?) actually subset 3? check
    ]
    for inst in edge_instances:
        Partition.validate(inst)
        ans_part = partition_bruteforce(inst)
        reduced = reduce(inst)
        ans_subset = subset_sum_bruteforce(reduced)
        if ans_part == ans_subset:
            passed += 1
        else:
            print("FAIL EDGE", inst, ans_part, reduced, ans_subset)
            break
    total = num_tests + len(edge_instances)
    return total, passed

if __name__ == "__main__":
    total, passed = run_tests()
    result = {
        "verified": passed == total,
        "tests_run": total,
        "tests_passed": passed,
    }
    print(json.dumps(result, indent=2))
    with open("verdict.json", "w") as f:
        json.dump(result, f)
