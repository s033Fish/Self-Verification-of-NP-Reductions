import random
from typing import List, Dict, Any
from problems import Sat, ThreeSat
from reduce import reduce

def sat_bruteforce(inst: Dict[str, Any]) -> bool:
    m = inst['num_vars']
    clauses = inst['clauses']
    for bits in product([False, True], repeat=m):
        assign = {i+1: bits[i] for i in range(m)}
        ok = True
        for clause in clauses:
            if len(clause) == 0:
                ok = False
                break
            clause_ok = any((lit > 0 and assign.get(abs(lit), False)) or (lit < 0 and not assign.get(abs(lit), False)) for lit in clause)
            if not clause_ok:
                ok = False
                break
        if ok:
            return True
    return False

def three_sat_bruteforce(inst: Dict[str, Any]) -> bool:
    m = inst['num_vars']
    clauses = inst['clauses']
    for bits in product([False, True], repeat=m):
        assign = {i+1: bits[i] for i in range(m)}
        ok = True
        for clause in clauses:
            clause_ok = any((lit > 0 and assign.get(abs(lit), False)) or (lit < 0 and not assign.get(abs(lit), False)) for lit in clause)
            if not clause_ok:
                ok = False
                break
        if ok:
            return True
    return False

from itertools import product

def random_sat_instance(max_vars=3, max_clauses=3) -> Dict[str, Any]:
    m = random.randint(0, max_vars)
    clauses = []
    for _ in range(random.randint(0, max_clauses)):
        k = random.randint(0, max_vars)  # clause length may be 0
        clause = []
        for _ in range(k):
            if m == 0:
                continue
            var = random.randint(1, m)
            lit = var if random.choice([True, False]) else -var
            clause.append(lit)
        clauses.append(clause)
    return {'num_vars': m, 'clauses': clauses}

def main():
    tests = 200
    passed = 0
    for _ in range(tests):
        inst = random_sat_instance()
        # validate
        Sat.validate(inst)
        sat_res = sat_bruteforce(inst)
        red = reduce(inst)
        ThreeSat.validate(red)
        three_res = three_sat_bruteforce(red)
        if sat_res == three_res:
            passed += 1
        else:
            print('FAIL')
            print('orig', inst)
            print('sat_res', sat_res)
            print('red', red)
            print('three_res', three_res)
            break
    print('tests run', tests, 'passed', passed)
    # write verdict
    import json
    verdict = {'verified': passed == tests, 'tests_run': tests, 'tests_passed': passed}
    with open('verdict.json', 'w') as f:
        json.dump(verdict, f)

if __name__ == '__main__':
    main()
