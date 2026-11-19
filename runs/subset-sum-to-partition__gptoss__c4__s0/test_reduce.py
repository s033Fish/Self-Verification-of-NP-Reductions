import random
import itertools
import json
from problems import SubsetSum, Partition
from reduce import reduce

def subset_sum_bruteforce(instance):
    numbers = instance["numbers"]
    target = instance["target"]
    # Edge cases
    if target == 0:
        return True
    if target < 0:
        return False
    n = len(numbers)
    for r in range(1, n+1):
        for combo in itertools.combinations(range(n), r):
            s = sum(numbers[i] for i in combo)
            if s == target:
                return True
    return False

def partition_bruteforce(instance):
    numbers = instance["numbers"]
    total = sum(numbers)
    # Edge cases handled by brute force as well
    n = len(numbers)
    # try all subsets as one side
    for r in range(n+1):
        for combo in itertools.combinations(range(n), r):
            s = sum(numbers[i] for i in combo)
            if s * 2 == total:
                return True
    return False

def test_random(num_tests=200):
    for _ in range(num_tests):
        # generate small numbers
        length = random.randint(0, 6)
        numbers = [random.randint(0, 10) for _ in range(length)]
        target = random.randint(-5, sum(numbers)+5)
        src = {"numbers": numbers, "target": target}
        # validate
        SubsetSum.validate(src)
        # compute answers
        src_ans = subset_sum_bruteforce(src)
        red = reduce(src)
        Partition.validate(red)
        tgt_ans = partition_bruteforce(red)
        if src_ans != tgt_ans:
            print("Mismatch!", src, src_ans, red, tgt_ans)
            return False
    return True

if __name__ == "__main__":
    ok = test_random(500)
    verdict = {"verified": ok, "tests_run": 500, "tests_passed": 500 if ok else 0}
    print(json.dumps(verdict))
    with open('verdict.json', 'w') as f:
        json.dump(verdict, f)
