import random
import json
import itertools
import sys
from problems import OneInThreeSat, ThreeSat, InvalidInstance
from reduce import reduce

def solve_one_in_three(inst):
    m = inst['num_vars']
    clauses = inst['clauses']
    for bits in itertools.product([0,1], repeat=m):
        ok = True
        for a,b,c in clauses:
            cnt = bits[a-1] + bits[b-1] + bits[c-1]
            if cnt != 1:
                ok = False
                break
        if ok:
            return True
    return False

def solve_three_sat(inst):
    m = inst['num_vars']
    clauses = inst['clauses']
    for bits in itertools.product([0,1], repeat=m):
        ok = True
        for l1,l2,l3 in clauses:
            def lit_true(l):
                v = abs(l)-1
                val = bits[v]
                return val if l>0 else (1-val)
            if not (lit_true(l1) or lit_true(l2) or lit_true(l3)):
                ok = False
                break
        if ok:
            return True
    return False

def random_instance(max_vars=5, max_clauses=5):
    m = random.randint(0, max_vars)
    # ensure at least 3 vars if there are clauses
    num_clauses = random.randint(0, max_clauses)
    if num_clauses>0 and m<3:
        m = 3
    clauses = []
    for _ in range(num_clauses):
        # pick 3 distinct vars from 1..m
        vars = random.sample(range(1, m+1), 3)
        clauses.append(vars)
    return {'num_vars': m, 'clauses': clauses}

def main():
    random.seed(0)
    tests = 200
    passed = 0
    for i in range(tests):
        inst = random_instance()
        # validate source
        try:
            OneInThreeSat.validate(inst)
        except InvalidInstance as e:
            print('Invalid source instance generated', e)
            continue
        red = reduce(inst)
        # validate target
        ThreeSat.validate(red)
        ans_src = solve_one_in_three(inst)
        ans_tgt = solve_three_sat(red)
        if ans_src == ans_tgt:
            passed += 1
        else:
            print('Mismatch on test', i)
            print('src', inst)
            print('red', red)
            print('src ans', ans_src, 'tgt ans', ans_tgt)
            break
    # Edge cases
    edge_cases = [
        {'num_vars':0, 'clauses':[]},
        {'num_vars':3, 'clauses':[]},
    ]
    for ec in edge_cases:
        OneInThreeSat.validate(ec)
        red = reduce(ec)
        ThreeSat.validate(red)
        if solve_one_in_three(ec) != solve_three_sat(red):
            print('Edge case mismatch', ec)
            sys.exit(1)
        passed += 1
    total = tests + len(edge_cases)
    result = {
        "verified": passed == total,
        "tests_run": total,
        "tests_passed": passed,
    }
    with open('verdict.json','w') as f:
        json.dump(result, f)
    print('Result:', result)

if __name__ == '__main__':
    main()
