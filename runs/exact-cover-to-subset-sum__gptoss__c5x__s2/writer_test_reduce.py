import random
import json
from problems import ExactCover, SubsetSum
from reduce import reduce


def exact_cover_bruteforce(instance):
    ExactCover.validate(instance)
    u = instance["universe_size"]
    sets = instance["sets"]
    n = len(sets)
    if u == 0:
        return True
    for mask in range(1 << n):
        covered = set()
        ok = True
        for i in range(n):
            if mask >> i & 1:
                s = sets[i]
                for e in s:
                    if e in covered:
                        ok = False
                        break
                    covered.add(e)
                if not ok:
                    break
        if ok and covered == set(range(u)):
            return True
    return False


def subset_sum_bruteforce(instance):
    SubsetSum.validate(instance)
    numbers = instance["numbers"]
    target = instance["target"]
    m = len(numbers)
    for mask in range(1 << m):
        s = 0
        for i in range(m):
            if mask >> i & 1:
                s += numbers[i]
        if s == target:
            return True
    return False


def random_exact_cover_instance(max_u=4, max_sets=5, max_elem_per_set=4):
    u = random.randint(0, max_u)
    sets = []
    for _ in range(random.randint(0, max_sets)):
        size = random.randint(0, min(max_elem_per_set, u)) if u > 0 else 0
        s = random.sample(range(u), size) if u > 0 else []
        sets.append(s)
    return {"universe_size": u, "sets": sets}


def run_tests(num_trials=200):
    passed = 0
    for _ in range(num_trials):
        src = random_exact_cover_instance()
        try:
            tgt = reduce(src)
        except Exception as e:
            print("Reduction raised exception on", src, e)
            return False, passed
        src_ans = exact_cover_bruteforce(src)
        tgt_ans = subset_sum_bruteforce(tgt)
        if src_ans != tgt_ans:
            print("Mismatch!", src, src_ans, tgt, tgt_ans)
            return False, passed
        passed += 1
    return True, passed

if __name__ == "__main__":
    ok, count = run_tests(500)
    result = {"verified": ok, "tests_run": 500, "tests_passed": count}
    print(json.dumps(result))
    with open("verdict.json", "w") as f:
        json.dump(result, f)
