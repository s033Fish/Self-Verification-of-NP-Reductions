import random
import itertools
import json
import sys
from problems import OneInThreeSat, ExactCover, InvalidInstance
from reduce import reduce

def solve_one_in_three(instance):
    m = instance['num_vars']
    clauses = instance['clauses']
    for assign in itertools.product([0,1], repeat=m):
        ok = True
        for clause in clauses:
            cnt = sum(assign[v-1] for v in clause)
            if cnt != 1:
                ok = False
                break
        if ok:
            return True
    return True if not clauses else False

def solve_exact_cover(instance):
    u = instance['universe_size']
    sets = instance['sets']
    n = len(sets)
    # try all subsets of sets (2^n)
    for mask in range(1<<n):
        covered = [0]*u
        ok = True
        for i in range(n):
            if mask>>i & 1:
                for e in sets[i]:
                    if covered[e]:
                        ok = False
                        break
                    covered[e] = 1
                if not ok:
                    break
        if ok and all(covered):
            return True
    # also handle u==0, empty cover is ok (mask=0)
    return u==0

def random_one_in_three(m, num_clauses):
    clauses = []
    vars_list = list(range(1, m+1))
    for _ in range(num_clauses):
        clause = random.sample(vars_list, 3)
        clauses.append(clause)
    return {'num_vars': m, 'clauses': clauses}

def run_tests(num_tests=200):
    passed = 0
    for _ in range(num_tests):
        # generate random instance
        m = random.randint(0,4)
        # ensure if clauses exist m>=3 per spec, but we can still generate
        max_clauses = 5
        num_clauses = random.randint(0, max_clauses)
        if num_clauses>0 and m<3:
            m = 3
        instance = random_one_in_three(m, num_clauses)
        # validate
        try:
            OneInThreeSat.validate(instance)
        except InvalidInstance as e:
            print('Invalid generated instance', e)
            continue
        red = reduce(instance)
        ExactCover.validate(red)
        ans_src = solve_one_in_three(instance)
        ans_red = solve_exact_cover(red)
        if ans_src == ans_red:
            passed += 1
        else:
            print('Mismatch!')
            print('src', instance)
            print('src ans', ans_src)
            print('red', red)
            print('red ans', ans_red)
            return passed, False
    return passed, True

if __name__ == '__main__':
    total, ok = run_tests(500)
    result = {
        'verified': ok,
        'tests_run': 500,
        'tests_passed': total,
    }
    print(json.dumps(result))
    sys.exit(0 if ok else 1)
