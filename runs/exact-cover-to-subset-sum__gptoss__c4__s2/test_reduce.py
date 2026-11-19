import itertools
import random
import sys

from problems import ExactCover, SubsetSum
from reduce import reduce


def exact_cover_bruteforce(instance):
    ExactCover.validate(instance)
    u = instance["universe_size"]
    sets = instance["sets"]
    n = len(sets)
    # Represent each set as a bitmask
    masks = []
    for s in sets:
        mask = 0
        for e in s:
            mask |= 1 << e
        masks.append(mask)
    full = (1 << u) - 1
    # iterate over subsets of indices
    for r in range(n + 1):
        for combo in itertools.combinations(range(n), r):
            union = 0
            ok = True
            for idx in combo:
                if masks[idx] & union:
                    ok = False
                    break
                union |= masks[idx]
            if ok and union == full:
                return True
    return False


def subset_sum_bruteforce(instance):
    SubsetSum.validate(instance)
    numbers = instance["numbers"]
    target = instance["target"]
    if target == 0:
        return True
    if target < 0:
        return False
    n = len(numbers)
    for r in range(1, n + 1):
        for combo in itertools.combinations(range(n), r):
            s = sum(numbers[i] for i in combo)
            if s == target:
                return True
    return False


def random_exact_cover(u_max=4, set_count_max=5):
    u = random.randint(0, u_max)
    num_sets = random.randint(0, set_count_max)
    sets = []
    for _ in range(num_sets):
        # random subset of universe
        subset = [i for i in range(u) if random.choice([True, False])]
        sets.append(subset)
    return {"universe_size": u, "sets": sets}


def run_tests(num_trials=200):
    passed = 0
    for _ in range(num_trials):
        inst = random_exact_cover()
        ec = exact_cover_bruteforce(inst)
        red = reduce(inst)
        ss = subset_sum_bruteforce(red)
        if ec != ss:
            print("Mismatch!", inst, red, ec, ss)
            return passed, False
        passed += 1
    return passed, True

if __name__ == "__main__":
    passed, ok = run_tests()
    print(f"Tests run: {passed}, all passed: {ok}")
    # write verdict.json
    import json
    verdict = {"verified": ok, "tests_run": passed, "tests_passed": passed if ok else 0}
    with open("verdict.json", "w") as f:
        json.dump(verdict, f)
