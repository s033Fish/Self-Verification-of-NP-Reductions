import itertools, random, json
from problems import OneInThreeSat, SubsetSum
from reduce import reduce

def solve_one_in_three_sat(instance):
    m = instance['num_vars']
    clauses = instance['clauses']
    # iterate over all assignments as bits 0/1
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
    numbers = instance['numbers']
    target = instance['target']
    n = len(numbers)
    # early cases
    if target == 0:
        return True
    if target < 0:
        return False
    for mask in range(1<<n):
        s = 0
        for i in range(n):
            if mask>>i & 1:
                s += numbers[i]
        if s == target:
            return True
    return False

def random_one_in_three_instance(max_vars=5, max_clauses=6):
    m = random.randint(0, max_vars)
    # ensure at least 3 vars if there are clauses
    k = random.randint(0, max_clauses)
    clauses = []
    if k>0:
        if m < 3:
            m = 3
        for _ in range(k):
            clause = random.sample(range(1, m+1), 3)
            clauses.append(clause)
    return {'num_vars': m, 'clauses': clauses}

def run_tests(num=200):
    passed = 0
    for _ in range(num):
        inst = random_one_in_three_instance()
        # validate source
        OneInThreeSat.validate(inst)
        src_ans = solve_one_in_three_sat(inst)
        red = reduce(inst)
        SubsetSum.validate(red)
        tgt_ans = solve_subset_sum(red)
        if src_ans == tgt_ans:
            passed += 1
        else:
            print('Mismatch!')
            print('src', inst, src_ans)
            print('red', red, tgt_ans)
            return False, passed
    return True, passed

if __name__ == '__main__':
    ok, passed = run_tests(500)
    verdict = {
        'verified': ok,
        'tests_run': 500,
        'tests_passed': passed
    }
    print(json.dumps(verdict))
    with open('verdict.json', 'w') as f:
        json.dump(verdict, f)
