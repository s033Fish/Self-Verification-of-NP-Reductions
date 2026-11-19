import random
import itertools
import json
from problems import SubsetSum, Sat
from reduce import reduce


def solve_subset_sum(instance):
    numbers = instance["numbers"]
    target = instance["target"]
    n = len(numbers)
    if target == 0:
        return True
    if target < 0:
        return False
    for mask in range(1 << n):
        s = 0
        for i in range(n):
            if mask & (1 << i):
                s += numbers[i]
        if s == target:
            return True
    return False


def solve_sat(instance):
    m = instance["num_vars"]
    clauses = instance["clauses"]
    # Edge cases handled by brute force as well
    for vals in itertools.product([False, True], repeat=m):
        ok = True
        for clause in clauses:
            # empty clause -> unsatisfied
            if not clause:
                ok = False
                break
            sat_clause = False
            for lit in clause:
                var = abs(lit) - 1
                val = vals[var]
                if lit > 0 and val:
                    sat_clause = True
                    break
                if lit < 0 and not val:
                    sat_clause = True
                    break
            if not sat_clause:
                ok = False
                break
        if ok:
            return True
    return False


def random_subset_sum_instance(max_len=5, max_val=10, max_target=20):
    length = random.randint(0, max_len)
    numbers = [random.randint(0, max_val) for _ in range(length)]
    target = random.randint(-max_target, max_target)
    return {"numbers": numbers, "target": target}


def run_tests(num_tests=200):
    passed = 0
    for _ in range(num_tests):
        src = random_subset_sum_instance()
        # validate source
        SubsetSum.validate(src)
        src_ans = solve_subset_sum(src)
        red = reduce(src)
        Sat.validate(red)
        red_ans = solve_sat(red)
        if src_ans == red_ans:
            passed += 1
        else:
            print("FAIL", src, src_ans, red, red_ans)
            break
    return passed, num_tests

if __name__ == "__main__":
    passed, total = run_tests()
    verdict = {"verified": passed == total, "tests_run": total, "tests_passed": passed}
    print(json.dumps(verdict))
    with open("verdict.json", "w") as f:
        json.dump(verdict, f)
