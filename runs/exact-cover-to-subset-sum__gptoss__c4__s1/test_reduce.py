import random
import itertools
import json
from problems import ExactCover, SubsetSum
from reduce import reduce


def exact_cover_bruteforce(instance):
    u = instance["universe_size"]
    sets = instance["sets"]
    n = len(sets)
    # iterate over all subsets of indices
    for r in range(1 << n):
        chosen = []
        covered = set()
        ok = True
        for i in range(n):
            if r & (1 << i):
                s = sets[i]
                # check disjointness
                for e in s:
                    if e in covered:
                        ok = False
                        break
                if not ok:
                    break
                covered.update(s)
                chosen.append(s)
        if not ok:
            continue
        if len(covered) == u:
            return True
    # also handle u=0 (empty universe) which is always yes
    if u == 0:
        return True
    return False


def subset_sum_bruteforce(instance):
    numbers = instance["numbers"]
    target = instance["target"]
    if target == 0:
        return True
    if target < 0:
        return False
    n = len(numbers)
    for r in range(1 << n):
        s = 0
        for i in range(n):
            if r & (1 << i):
                s += numbers[i]
        if s == target:
            return True
    return False


def random_exact_cover_instance(max_u=4, max_sets=5, max_set_size=4):
    u = random.randint(0, max_u)
    sets = []
    for _ in range(random.randint(0, max_sets)):
        size = random.randint(0, max_set_size)
        # pick distinct elements from 0..u-1
        elems = random.sample(range(u), min(size, u))
        sets.append(elems)
    return {"universe_size": u, "sets": sets}


def run_tests(num_tests=200):
    passed = 0
    for _ in range(num_tests):
        inst = random_exact_cover_instance()
        ExactCover.validate(inst)
        red = reduce(inst)
        SubsetSum.validate(red)
        ans_src = exact_cover_bruteforce(inst)
        ans_tgt = subset_sum_bruteforce(red)
        if ans_src == ans_tgt:
            passed += 1
        else:
            print("Mismatch!", inst, red, ans_src, ans_tgt)
            break
    return passed, num_tests

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
