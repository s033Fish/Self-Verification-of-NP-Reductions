import random
import itertools
import json
from problems import SubsetSum, Partition
from reduce import reduce

def subset_sum_bruteforce(instance):
    SubsetSum.validate(instance)
    nums = instance['numbers']
    t = instance['target']
    n = len(nums)
    # Edge cases
    if t == 0:
        return True
    if t < 0:
        return False
    for r in range(1, n+1):
        for combo in itertools.combinations(range(n), r):
            s = sum(nums[i] for i in combo)
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
    # subset sum to target
    for r in range(n+1):
        for combo in itertools.combinations(range(n), r):
            if sum(nums[i] for i in combo) == target:
                return True
    return False


def random_instance(max_len=6, max_val=10):
    length = random.randint(0, max_len)
    nums = [random.randint(0, max_val) for _ in range(length)]
    target = random.randint(-5, max_val*length + 5)
    return {"numbers": nums, "target": target}


def run_tests(num=200):
    passed = 0
    for _ in range(num):
        inst = random_instance()
        ss_ans = subset_sum_bruteforce(inst)
        red = reduce(inst)
        part_ans = partition_bruteforce(red)
        if ss_ans == part_ans:
            passed += 1
        else:
            print('FAIL')
            print('Original:', json.dumps(inst))
            print('Reduced:', json.dumps(red))
            print('SubsetSum answer:', ss_ans)
            print('Partition answer:', part_ans)
            break
    return passed, num

if __name__ == '__main__':
    passed, total = run_tests(500)
    print(f"Tests passed: {passed}/{total}")
    verdict = {
        "verified": passed == total,
        "tests_run": total,
        "tests_passed": passed
    }
    with open('verdict.json', 'w') as f:
        json.dump(verdict, f)
    print('Verdict written to verdict.json')
