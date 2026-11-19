import random
import itertools
import sys
from problems import Sat, ThreeSat
from reduce import reduce

def sat_bruteforce(instance):
    Sat.validate(instance)
    m = instance['num_vars']
    clauses = instance['clauses']
    for assign in itertools.product([False, True], repeat=m):
        ok = True
        for clause in clauses:
            # empty clause unsat
            if len(clause) == 0:
                ok = False
                break
            sat_clause = False
            for lit in clause:
                var = abs(lit) - 1
                val = assign[var]
                if (lit > 0 and val) or (lit < 0 and not val):
                    sat_clause = True
                    break
            if not sat_clause:
                ok = False
                break
        if ok:
            return True
    return False

def three_sat_bruteforce(instance):
    ThreeSat.validate(instance)
    return sat_bruteforce(instance)  # same logic works

def random_sat_instance(num_vars, max_clauses, max_clause_len):
    clauses = []
    for _ in range(random.randint(0, max_clauses)):
        k = random.randint(0, max_clause_len)
        clause = []
        for _ in range(k):
            var = random.randint(1, num_vars)
            sign = random.choice([1, -1])
            clause.append(sign * var)
        clauses.append(clause)
    return {'num_vars': num_vars, 'clauses': clauses}

def run_tests(num_tests=200):
    passed = 0
    for _ in range(num_tests):
        num_vars = random.randint(0, 4)  # small for brute force
        inst = random_sat_instance(num_vars, max_clauses=5, max_clause_len=4)
        # compute answers
        ans_src = sat_bruteforce(inst)
        red = reduce(inst)
        ans_tgt = three_sat_bruteforce(red)
        if ans_src != ans_tgt:
            print('Mismatch!')
            print('Source:', inst)
            print('Reduced:', red)
            print('src ans', ans_src, 'tgt ans', ans_tgt)
            sys.exit(1)
        passed += 1
    print('All', passed, 'tests passed')
    return passed

if __name__ == '__main__':
    run_tests()
