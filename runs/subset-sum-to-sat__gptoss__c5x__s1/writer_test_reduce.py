import random
import json
import itertools
from problems import SubsetSum, Sat
from reduce import reduce


def subset_sum_bruteforce(instance):
    SubsetSum.validate(instance)
    nums = instance["numbers"]
    t = instance["target"]
    n = len(nums)
    for mask in range(1 << n):
        s = 0
        for i in range(n):
            if mask & (1 << i):
                s += nums[i]
        if s == t:
            return True
    return False


def sat_bruteforce(instance):
    Sat.validate(instance)
    m = instance["num_vars"]
    clauses = instance["clauses"]
    for cl in clauses:
        if len(cl) == 0:
            return False
    for assign in itertools.product([False, True], repeat=m):
        ok = True
        for cl in clauses:
            lit_true = False
            for lit in cl:
                var = abs(lit) - 1
                val = assign[var]
                if lit > 0 and val:
                    lit_true = True
                    break
                if lit < 0 and not val:
                    lit_true = True
                    break
            if not lit_true:
                ok = False
                break
        if ok:
            return True
    return False


def random_subset_instance(max_n=3, max_val=3):
    """Generate tiny instances so that the SAT reduction stays small."""
    n = random.randint(0, max_n)
    numbers = [random.randint(0, max_val) for _ in range(n)]
    t = random.randint(-3, sum(numbers) + 3)
    return {"numbers": numbers, "target": t}


def run_tests(num=200):
    passed = 0
    for i in range(num):
        src = random_subset_instance()
        src_ans = subset_sum_bruteforce(src)
        red = reduce(src)
        tgt_ans = sat_bruteforce(red)
        if src_ans == tgt_ans:
            passed += 1
        else:
            print("Mismatch!", src, src_ans, red, tgt_ans)
            break
    return passed, num

if __name__ == "__main__":
    passed, total = run_tests(200)
    result = {"verified": passed == total, "tests_run": total, "tests_passed": passed}
    with open('verdict.json', 'w') as f:
        json.dump(result, f)
    print(json.dumps(result))
