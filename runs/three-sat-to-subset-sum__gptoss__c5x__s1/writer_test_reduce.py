import itertools
import random
import json
from problems import ThreeSat, SubsetSum
from reduce import reduce

def sat_bruteforce(instance):
    m = instance["num_vars"]
    clauses = instance["clauses"]
    for vals in itertools.product([False, True], repeat=m):
        ok = True
        for clause in clauses:
            clause_ok = False
            for lit in clause:
                var = abs(lit) - 1
                val = vals[var]
                if (lit > 0 and val) or (lit < 0 and not val):
                    clause_ok = True
                    break
            if not clause_ok:
                ok = False
                break
        if ok:
            return True
    return False

def subset_sum_bruteforce(instance):
    nums = instance["numbers"]
    target = instance["target"]
    n = len(nums)
    for mask in range(1 << n):
        s = 0
        for i in range(n):
            if mask >> i & 1:
                s += nums[i]
        if s == target:
            return True
    return False


def random_three_sat(max_vars=4, max_clauses=5):
    m = random.randint(0, max_vars)
    # ensure at least 3 vars if there are clauses
    if m < 3:
        num_clauses = 0
    else:
        num_clauses = random.randint(0, max_clauses)
    clauses = []
    for _ in range(num_clauses):
        # pick 3 distinct vars
        vars = random.sample(range(1, m+1), 3)
        clause = []
        for v in vars:
            lit = v if random.choice([True, False]) else -v
            clause.append(lit)
        clauses.append(clause)
    return {"num_vars": m, "clauses": clauses}


def run_tests(num=200):
    passed = 0
    for _ in range(num):
        inst = random_three_sat()
        ThreeSat.validate(inst)
        reduced = reduce(inst)
        SubsetSum.validate(reduced)
        ans1 = sat_bruteforce(inst)
        ans2 = subset_sum_bruteforce(reduced)
        if ans1 == ans2:
            passed += 1
        else:
            print("Mismatch!", inst, reduced, ans1, ans2)
            break
    return passed, num

if __name__ == "__main__":
    passed, total = run_tests(500)
    verdict = {
        "verified": passed == total,
        "tests_run": total,
        "tests_passed": passed,
    }
    print(json.dumps(verdict))
    with open('verdict.json', 'w') as f:
        json.dump(verdict, f)
