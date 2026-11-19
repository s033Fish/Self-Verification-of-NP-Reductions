import random
import itertools
import sys
from problems import Partition, SubsetSum
from reduce import reduce

def solve_partition_bruteforce(instance):
    numbers = instance["numbers"]
    total = sum(numbers)
    if total % 2 == 1:
        return False
    target = total // 2
    n = len(numbers)
    # iterate subsets
    for r in range(n + 1):
        for combo in itertools.combinations(range(n), r):
            s = sum(numbers[i] for i in combo)
            if s == target:
                return True
    return False

def solve_subsetsum_bruteforce(instance):
    numbers = instance["numbers"]
    target = instance["target"]
    if target < 0:
        return False
    if target == 0:
        return True
    n = len(numbers)
    for r in range(1, n + 1):
        for combo in itertools.combinations(range(n), r):
            if sum(numbers[i] for i in combo) == target:
                return True
    return False

def check_instance(inst):
    # validate
    Partition.validate(inst)
    reduced = reduce(inst)
    SubsetSum.validate(reduced)
    ans1 = solve_partition_bruteforce(inst)
    ans2 = solve_subsetsum_bruteforce(reduced)
    return ans1 == ans2

def main():
    random.seed(0)
    tests = []
    # edge cases
    tests.append({"numbers": []})
    tests.append({"numbers": [0,0,0]})
    tests.append({"numbers": [1]})
    tests.append({"numbers": [1,2,3]})
    tests.append({"numbers": [2,2,2,2]})
    # random tests
    for _ in range(200):
        length = random.randint(0, 8)
        numbers = [random.randint(0, 10) for _ in range(length)]
        tests.append({"numbers": numbers})
    passed = 0
    for i,inst in enumerate(tests):
        try:
            ok = check_instance(inst)
        except Exception as e:
            print(f"Test {i} raised exception: {e}")
            ok = False
        if ok:
            passed += 1
        else:
            print(f"Test {i} failed. Instance: {inst}")
    total = len(tests)
    print(f"Passed {passed}/{total} tests")
    # write verdict
    verdict = {
        "verified": passed == total,
        "tests_run": total,
        "tests_passed": passed,
    }
    import json, pathlib
    pathlib.Path("verdict.json").write_text(json.dumps(verdict))
    sys.exit(0 if passed == total else 1)

if __name__ == "__main__":
    main()
