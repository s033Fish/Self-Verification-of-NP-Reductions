import itertools
import random
import json
from problems import OneInThreeSat, SubsetSum
from reduce import reduce

def solve_one_in_three(instance):
    m = instance["num_vars"]
    clauses = instance["clauses"]
    # iterate over all boolean assignments
    for bits in itertools.product([0,1], repeat=m):
        ok = True
        for clause in clauses:
            cnt = sum(bits[var-1] for var in clause)
            if cnt != 1:
                ok = False
                break
        if ok:
            return True
    return False

def solve_subset_sum(instance):
    numbers = instance["numbers"]
    target = instance["target"]
    n = len(numbers)
    # brute force all subsets
    for mask in range(1<<n):
        s = 0
        for i in range(n):
            if mask>>i & 1:
                s += numbers[i]
        if s == target:
            return True
    return False

def random_one_in_three(max_vars=5, max_clauses=5):
    m = random.randint(0, max_vars)
    # ensure at least 3 vars if clauses exist
    if m < 3:
        # allow zero clauses
        clauses = []
    else:
        c = random.randint(0, max_clauses)
        clauses = []
        for _ in range(c):
            clause = random.sample(range(1, m+1), 3)
            clauses.append(clause)
    return {"num_vars": m, "clauses": clauses}

def main():
    random.seed(0)
    total = 0
    passed = 0
    for _ in range(200):
        inst = random_one_in_three()
        # validate source
        OneInThreeSat.validate(inst)
        reduced = reduce(inst)
        # validate target
        SubsetSum.validate(reduced)
        ans_src = solve_one_in_three(inst)
        ans_tgt = solve_subset_sum(reduced)
        total += 1
        if ans_src == ans_tgt:
            passed += 1
        else:
            print("Mismatch!", inst, reduced, ans_src, ans_tgt)
            break
    print(f"Tests run: {total}, passed: {passed}")
    # write verdict
    verdict = {"verified": passed==total, "tests_run": total, "tests_passed": passed}
    with open('verdict.json','w') as f:
        json.dump(verdict, f)

if __name__ == '__main__':
    main()
