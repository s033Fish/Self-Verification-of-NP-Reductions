import random
import itertools
import json
from problems import ThreeSat, OneInThreeSat
from reduce import reduce

def solve_three_sat(inst):
    ThreeSat.validate(inst)
    m = inst['num_vars']
    clauses = inst['clauses']
    for assign in itertools.product([False, True], repeat=m):
        ok = True
        for clause in clauses:
            if not any((lit > 0) == assign[abs(lit)-1] for lit in clause):
                ok = False
                break
        if ok:
            return True
    return False

def solve_one_in_three(inst):
    OneInThreeSat.validate(inst)
    m = inst['num_vars']
    clauses = inst['clauses']
    for assign in itertools.product([False, True], repeat=m):
        ok = True
        for clause in clauses:
            true_cnt = sum(assign[v-1] for v in clause)
            if true_cnt != 1:
                ok = False
                break
        if ok:
            return True
    return False

def random_three_sat(m, max_clauses=5):
    # generate random clauses respecting constraints
    clauses = []
    vars_list = list(range(1, m+1))
    for _ in range(random.randint(0, max_clauses)):
        # pick 3 distinct vars
        chosen = random.sample(vars_list, 3)
        clause = []
        for v in chosen:
            lit = v if random.choice([True, False]) else -v
            clause.append(lit)
        clauses.append(clause)
    return {'num_vars': m, 'clauses': clauses}

def run_tests(num_tests=200):
    passed = 0
    for _ in range(num_tests):
        m = random.randint(0, 4)  # allow 0 vars
        # ensure if clauses exist m>=3 per spec, but our generator may create clauses even if m<3 -> skip those
        if m < 3:
            inst = {'num_vars': m, 'clauses': []}
        else:
            inst = random_three_sat(m, max_clauses=4)
        # compute answers
        ans_src = solve_three_sat(inst)
        red = reduce(inst)
        ans_tgt = solve_one_in_three(red)
        if ans_src == ans_tgt:
            passed += 1
        else:
            print('FAIL', inst, ans_src, ans_tgt)
            break
    return passed, num_tests

if __name__ == '__main__':
    passed, total = run_tests(500)
    result = {
        'verified': passed == total,
        'tests_run': total,
        'tests_passed': passed,
    }
    print(json.dumps(result))
    with open('verdict.json', 'w') as f:
        json.dump(result, f)
