import random
import itertools
import json
from problems import OneInThreeSat, ExactCover
from reduce import reduce

def solve_one_in_three_sat(instance):
    OneInThreeSat.validate(instance)
    m = instance['num_vars']
    clauses = instance['clauses']
    for bits in itertools.product([False, True], repeat=m):
        ok = True
        for clause in clauses:
            true_cnt = sum(bits[var-1] for var in clause)
            if true_cnt != 1:
                ok = False
                break
        if ok:
            return True
    return False

def solve_exact_cover(instance):
    ExactCover.validate(instance)
    u = instance['universe_size']
    sets = instance['sets']
    n = len(sets)
    universe = set(range(u))
    for mask in range(1<<n):
        chosen = []
        covered = set()
        ok = True
        for i in range(n):
            if mask>>i & 1:
                s = set(sets[i])
                if covered & s:
                    ok = False
                    break
                covered |= s
                chosen.append(i)
        if ok and covered == universe:
            return True
    return False

def random_one_in_three_instance(max_vars=4, max_clauses=5):
    m = random.randint(0, max_vars)
    # ensure at least 3 vars if there are clauses
    if max_clauses>0 and random.random()<0.7:
        num_clauses = random.randint(1, max_clauses)
        if m < 3:
            m = 3
        clauses = []
        for _ in range(num_clauses):
            clause = random.sample(range(1, m+1), 3)
            clauses.append(clause)
    else:
        clauses = []
    return {'num_vars': m, 'clauses': clauses}


def run_tests(num_tests=200):
    passed = 0
    for _ in range(num_tests):
        inst = random_one_in_three_instance()
        src_ans = solve_one_in_three_sat(inst)
        red = reduce(inst)
        tgt_ans = solve_exact_cover(red)
        if src_ans == tgt_ans:
            passed += 1
        else:
            print('FAIL')
            print('instance', json.dumps(inst))
            print('reduced', json.dumps(red))
            print('src', src_ans, 'tgt', tgt_ans)
            break
    return passed, num_tests

if __name__ == '__main__':
    passed, total = run_tests()
    print(f'Passed {passed}/{total}')
