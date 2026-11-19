import itertools
import random
import json
from problems import SubsetSum, Partition
from reduce import reduce

def subset_sum_bruteforce(instance):
    numbers = instance['numbers']
    target = instance['target']
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
    numbers = instance['numbers']
    total = sum(numbers)
    if total % 2 != 0:
        return False
    half = total // 2
    n = len(numbers)
    # try all subsets
    for r in range(n+1):
        for combo in itertools.combinations(range(n), r):
            if sum(numbers[i] for i in combo) == half:
                return True
    return False

def random_instance(max_len=6, max_val=10):
    length = random.randint(0, max_len)
    numbers = [random.randint(0, max_val) for _ in range(length)]
    target = random.randint(-5, sum(numbers)+5)
    return {"numbers": numbers, "target": target}

def test_random_trials(trials=200):
    for _ in range(trials):
        src = random_instance()
        # validate source
        SubsetSum.validate(src)
        src_ans = subset_sum_bruteforce(src)
        tgt = reduce(src)
        Partition.validate(tgt)
        tgt_ans = partition_bruteforce(tgt)
        if src_ans != tgt_ans:
            print('Mismatch!')
            print('Source:', src)
            print('Reduced:', tgt)
            print('src_ans', src_ans, 'tgt_ans', tgt_ans)
            return False
    return True

if __name__ == '__main__':
    ok = test_random_trials(500)
    print('All tests passed' if ok else 'Failed')
