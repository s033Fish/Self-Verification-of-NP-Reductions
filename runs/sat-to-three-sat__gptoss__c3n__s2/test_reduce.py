import random, itertools, sys, json
from problems import Sat, ThreeSat
from reduce import reduce

def sat_solver(instance):
    Sat.validate(instance)
    n = instance['num_vars']
    clauses = instance['clauses']
    for assign in itertools.product([False, True], repeat=n):
        ok = True
        for clause in clauses:
            if len(clause) == 0:
                ok = False
                break
            if not any(((lit > 0) == assign[abs(lit)-1] for lit in clause)):
                ok = False
                break
        if ok:
            return True
    return False

def three_sat_solver(instance):
    ThreeSat.validate(instance)
    n = instance['num_vars']
    clauses = instance['clauses']
    for assign in itertools.product([False, True], repeat=n):
        if all(any(((lit > 0) == assign[abs(lit)-1] for lit in clause) for clause in clauses):
            return True
    return False

def random_sat_instance(num_vars, num_clauses, min_len=3, max_len=5):
    clauses = []
    for _ in range(num_clauses):
        k = random.randint(min_len, max_len)
        lits = []
        for _ in range(k):
            v = random.randint(1, num_vars)
            sign = random.choice([1, -1])
            lits.append(sign * v)
        clauses.append(lits)
    return {'num_vars': num_vars, 'clauses': clauses}

def run_tests():
    total = 0
    passed = 0
    # random instances (clauses length >=3)
    for num_vars in range(1,5):
        for num_clauses in range(1,5):
            for _ in range(30):
                inst = random_sat_instance(num_vars, num_clauses)
                total += 1
                sat_res = sat_solver(inst)
                red = reduce(inst)
                three_res = three_sat_solver(red)
                if sat_res == three_res:
                    passed += 1
                else:
                    print('FAIL', inst, sat_res, three_res)
                    sys.exit(1)
    # empty clause case (unsatisfiable)
    inst = {'num_vars': 2, 'clauses': [[1], []]}
    total += 1
    sat_res = sat_solver(inst)
    red = reduce(inst)
    three_res = three_sat_solver(red)
    if sat_res == three_res:
        passed += 1
    else:
        print('FAIL empty clause', sat_res, three_res)
        sys.exit(1)
    verdict = {'verified': passed == total, 'tests_run': total, 'tests_passed': passed}
    with open('verdict.json', 'w') as f:
        json.dump(verdict, f)
    print('All tests passed', verdict)

if __name__ == '__main__':
    run_tests()
