import random
import itertools
import json
from problems import OneInThreeSat, SubsetSum
from reduce import reduce

def solve_one_in_three(instance):
    m = instance["num_vars"]
    clauses = instance["clauses"]
    # Edge case: no clauses -> always yes
    if not clauses:
        return True
    for bits in range(1 << m):
        assignment = [(bits >> i) & 1 for i in range(m)]  # 0/1 for var i+1
        ok = True
        for clause in clauses:
            true_cnt = sum(assignment[var-1] for var in clause)
            if true_cnt != 1:
                ok = False
                break
        if ok:
            return True
    return False

def solve_subset_sum(instance):
    numbers = instance["numbers"]
    target = instance["target"]
    if target < 0:
        return False
    n = len(numbers)
    # simple subset enumeration
    for mask in range(1 << n):
        s = 0
        for i in range(n):
            if mask >> i & 1:
                s += numbers[i]
        if s == target:
            return True
    return False

def random_one_in_three(max_vars=5, max_clauses=5):
    m = random.randint(0, max_vars)
    # ensure if m>0 and we want clauses, m>=3 else no clauses
    if m < 3:
        clauses = []
    else:
        c = random.randint(0, max_clauses)
        clauses = []
        for _ in range(c):
            # pick 3 distinct vars
            vars = random.sample(range(1, m+1), 3)
            clauses.append(vars)
    return {"num_vars": m, "clauses": clauses}

def main():
    random.seed(0)
    tests = 200
    passed = 0
    for _ in range(tests):
        src = random_one_in_three()
        # validate source
        OneInThreeSat.validate(src)
        tgt = reduce(src)
        SubsetSum.validate(tgt)
        ans_src = solve_one_in_three(src)
        ans_tgt = solve_subset_sum(tgt)
        if ans_src == ans_tgt:
            passed += 1
        else:
            print("Mismatch!", src, tgt, ans_src, ans_tgt)
            break
    verdict = {
        "verified": passed == tests,
        "tests_run": tests,
        "tests_passed": passed,
    }
    with open("verdict.json", "w") as f:
        json.dump(verdict, f)
    print(json.dumps(verdict, indent=2))

if __name__ == "__main__":
    main()
