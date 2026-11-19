import random
import itertools
import sys
from problems import OneInThreeSat, SubsetSum, InvalidInstance
from reduce import reduce

def solve_one_in_three_sat(instance):
    OneInThreeSat.validate(instance)
    m = instance['num_vars']
    clauses = instance['clauses']
    for bits in itertools.product([0,1], repeat=m):
        ok = True
        for clause in clauses:
            true_count = sum(bits[var-1] for var in clause)
            if true_count != 1:
                ok = False
                break
        if ok:
            return True
    return True if not clauses else False

def solve_subset_sum(instance):
    SubsetSum.validate(instance)
    nums = instance['numbers']
    target = instance['target']
    n = len(nums)
    for mask in range(1<<n):
        s = 0
        for i in range(n):
            if mask>>i &1:
                s += nums[i]
        if s == target:
            return True
    return False

def random_instance(max_vars=4, max_clauses=4):
    m = random.randint(0, max_vars)
    # ensure if m<3 and we add clauses, we still respect variable indices
    max_vars_for_clause = max(3, m)
    c = random.randint(0, max_clauses)
    clauses = []
    for _ in range(c):
        # pick 3 distinct vars from 1..max_vars_for_clause (ensure >=1)
        if max_vars_for_clause == 0:
            break
        vars_pool = list(range(1, max_vars_for_clause+1))
        if len(vars_pool) < 3:
            # duplicate vars not allowed, so skip clause creation
            continue
        clause = random.sample(vars_pool, 3)
        clauses.append(clause)
    return {"num_vars": m, "clauses": clauses}

def main():
    random.seed(0)
    total = 0
    passed = 0
    for _ in range(200):
        inst = random_instance()
        try:
            ans_src = solve_one_in_three_sat(inst)
        except InvalidInstance:
            continue
        red = reduce(inst)
        ans_tgt = solve_subset_sum(red)
        total += 1
        if ans_src == ans_tgt:
            passed += 1
        else:
            print('Mismatch!')
            print('src', inst, ans_src)
            print('red', red, ans_tgt)
            sys.exit(1)
    print('Tests run', total, 'passed', passed)
    # write verdict
    import json
    with open('verdict.json','w') as f:
        json.dump({"verified": passed==total, "tests_run": total, "tests_passed": passed}, f)

if __name__ == "__main__":
    main()
