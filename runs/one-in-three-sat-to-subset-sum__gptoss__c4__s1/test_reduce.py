import random
import itertools
import json
from problems import OneInThreeSat, SubsetSum
from reduce import reduce

def solve_one_in_three(instance):
    m = instance['num_vars']
    clauses = instance['clauses']
    for bits in range(1 << m):
        assignment = [(bits >> i) & 1 == 1 for i in range(m)]  # variable i+1
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
    numbers = instance['numbers']
    target = instance['target']
    n = len(numbers)
    for mask in range(1 << n):
        s = 0
        for i in range(n):
            if mask >> i & 1:
                s += numbers[i]
        if s == target:
            return True
    return False

def random_instance(max_vars=4, max_clauses=4):
    m = random.randint(0, max_vars)
    # ensure at least 0 vars, but if clauses >0 need m>=3
    # We'll generate clauses only if m>=3
    if m < 3:
        clauses = []
    else:
        c = random.randint(0, max_clauses)
        clauses = []
        for _ in range(c):
            clause = random.sample(range(1, m+1), 3)
            clauses.append(clause)
    return {'num_vars': m, 'clauses': clauses}

random.seed(0)
tests = []
passed = 0
for _ in range(200):
    inst = random_instance()
    # validate source
    OneInThreeSat.validate(inst)
    reduced = reduce(inst)
    SubsetSum.validate(reduced)
    ans_src = solve_one_in_three(inst)
    ans_tgt = solve_subset_sum(reduced)
    ok = (ans_src == ans_tgt)
    if ok:
        passed += 1
    else:
        print('FAIL')
        print('src', inst)
        print('reduced', reduced)
        print('src ans', ans_src, 'tgt ans', ans_tgt)
        break
    tests.append((inst, reduced, ans_src, ans_tgt))

verdict = {
    "verified": passed == len(tests),
    "tests_run": len(tests),
    "tests_passed": passed,
}
print('VERDICT', verdict)
with open('verdict.json', 'w') as f:
    json.dump(verdict, f)
