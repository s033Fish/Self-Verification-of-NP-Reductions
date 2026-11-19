import random
import itertools
import json
from problems import ExactCover, SubsetSum
from reduce import reduce


def exact_cover_bruteforce(instance):
    u = instance["universe_size"]
    sets = instance["sets"]
    m = len(sets)
    # Preprocess sets as frozensets for speed
    set_frozen = [frozenset(s) for s in sets]
    universe = set(range(u))
    for mask in range(1 << m):
        chosen = []
        covered = set()
        ok = True
        for i in range(m):
            if mask >> i & 1:
                s = set_frozen[i]
                # check disjointness
                if covered & s:
                    ok = False
                    break
                covered |= s
                chosen.append(s)
        if ok and covered == universe:
            return True
    return False


def subset_sum_bruteforce(instance):
    numbers = instance["numbers"]
    target = instance["target"]
    n = len(numbers)
    for mask in range(1 << n):
        s = 0
        for i in range(n):
            if mask >> i & 1:
                s += numbers[i]
        if s == target:
            return True
    return False


def random_exact_cover_instance(max_u=4, max_m=5):
    u = random.randint(0, max_u)
    m = random.randint(0, max_m)
    sets = []
    for _ in range(m):
        # each set is a random subset of universe
        s = [i for i in range(u) if random.choice([True, False])]
        # ensure distinct elements (already) and random order
        random.shuffle(s)
        sets.append(s)
    return {"universe_size": u, "sets": sets}


def run_tests(num_cases=200):
    passed = 0
    for _ in range(num_cases):
        src = random_exact_cover_instance()
        # validate source
        ExactCover.validate(src)
        tgt = reduce(src)
        SubsetSum.validate(tgt)
        ans_src = exact_cover_bruteforce(src)
        ans_tgt = subset_sum_bruteforce(tgt)
        if ans_src == ans_tgt:
            passed += 1
        else:
            print("Mismatch!", json.dumps(src), json.dumps(tgt), ans_src, ans_tgt)
            break
    return passed, num_cases

if __name__ == "__main__":
    passed, total = run_tests(500)
    print(f"Tests passed: {passed}/{total}")
    # write verdict.json
    verdict = {
        "verified": passed == total,
        "tests_run": total,
        "tests_passed": passed,
    }
    with open("verdict.json", "w") as f:
        json.dump(verdict, f)
