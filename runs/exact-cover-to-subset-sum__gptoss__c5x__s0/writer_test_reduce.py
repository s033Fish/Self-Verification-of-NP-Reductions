import random
import sys
from itertools import combinations

from problems import ExactCover, SubsetSum
from reduce import reduce


def exact_cover_bruteforce(instance):
    u = instance["universe_size"]
    sets = instance["sets"]
    m = len(sets)
    # Edge case u=0 always yes
    if u == 0:
        return True
    # Enumerate subsets of sets
    for r in range(1, m + 1):
        for idxs in combinations(range(m), r):
            chosen = [sets[i] for i in idxs]
            # check pairwise disjoint and cover all elements
            seen = set()
            ok = True
            for s in chosen:
                for e in s:
                    if e in seen:
                        ok = False
                        break
                    seen.add(e)
                if not ok:
                    break
            if ok and len(seen) == u:
                return True
    return False


def subset_sum_bruteforce(instance):
    numbers = instance["numbers"]
    target = instance["target"]
    n = len(numbers)
    # Edge cases handled by brute force as well
    for r in range(n + 1):
        for idxs in combinations(range(n), r):
            s = sum(numbers[i] for i in idxs)
            if s == target:
                return True
    return False


def random_exact_cover_instance(max_u=4, max_sets=5):
    u = random.randint(0, max_u)
    sets = []
    for _ in range(random.randint(0, max_sets)):
        # generate a random subset of universe
        subset = [i for i in range(u) if random.choice([True, False])]
        # ensure distinct elements already
        sets.append(subset)
    return {"universe_size": u, "sets": sets}


def run_tests(num_tests=200):
    for i in range(num_tests):
        inst = random_exact_cover_instance()
        # validate source
        ExactCover.validate(inst)
        reduced = reduce(inst)
        SubsetSum.validate(reduced)
        ans_src = exact_cover_bruteforce(inst)
        ans_tgt = subset_sum_bruteforce(reduced)
        if ans_src != ans_tgt:
            print("Mismatch on test", i)
            print("Source", inst)
            print("Reduced", reduced)
            print("src ans", ans_src, "tgt ans", ans_tgt)
            sys.exit(1)
    print("All", num_tests, "tests passed.")
    return num_tests

if __name__ == "__main__":
    total = run_tests()
    # write verdict
    import json
    verdict = {"verified": True, "tests_run": total, "tests_passed": total}
    with open('verdict.json', 'w') as f:
        json.dump(verdict, f)
