import random
import itertools
import json
from problems import ExactCover, SubsetSum
from reduce import reduce

def exact_cover_bruteforce(instance):
    ExactCover.validate(instance)
    u = instance["universe_size"]
    sets = instance["sets"]
    n = len(sets)
    # Try all subsets of sets
    for mask in range(1 << n):
        covered = set()
        ok = True
        for i in range(n):
            if mask >> i & 1:
                s = sets[i]
                # check overlap
                for e in s:
                    if e in covered:
                        ok = False
                        break
                    covered.add(e)
                if not ok:
                    break
        if ok and covered == set(range(u)):
            return True
    # Edge case u=0 always yes
    return u == 0

def subset_sum_bruteforce(instance):
    SubsetSum.validate(instance)
    numbers = instance["numbers"]
    target = instance["target"]
    if target < 0:
        return False
    n = len(numbers)
    for mask in range(1 << n):
        s = 0
        for i in range(n):
            if mask >> i & 1:
                s += numbers[i]
        if s == target:
            return True
    return target == 0

def random_exact_cover_instance(max_u=4, max_sets=5):
    u = random.randint(0, max_u)
    sets = []
    for _ in range(random.randint(0, max_sets)):
        # random subset of universe
        subset = [i for i in range(u) if random.choice([True, False])]
        # ensure distinct elements already by construction
        sets.append(subset)
    return {"universe_size": u, "sets": sets}

def run_tests(num_trials=200):
    passed = 0
    for _ in range(num_trials):
        inst = random_exact_cover_instance()
        # compute answers
        ans_src = exact_cover_bruteforce(inst)
        inst_tgt = reduce(inst)
        ans_tgt = subset_sum_bruteforce(inst_tgt)
        if ans_src != ans_tgt:
            print("Mismatch!", inst, inst_tgt, ans_src, ans_tgt)
            return False, passed
        passed += 1
    return True, passed

if __name__ == "__main__":
    ok, cnt = run_tests(500)
    verdict = {"verified": ok, "tests_run": cnt, "tests_passed": cnt if ok else 0}
    print(json.dumps(verdict))
    with open('verdict.json', 'w') as f:
        json.dump(verdict, f)
