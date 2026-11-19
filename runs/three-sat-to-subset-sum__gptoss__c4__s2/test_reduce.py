import random
import itertools
import json
from problems import ThreeSat, SubsetSum
from reduce import reduce

def solve_three_sat(instance):
    m = instance['num_vars']
    clauses = instance['clauses']
    for bits in range(1 << m):
        ok = True
        for clause in clauses:
            clause_ok = False
            for lit in clause:
                var = abs(lit) - 1
                val = (bits >> var) & 1
                if lit > 0 and val == 1:
                    clause_ok = True
                if lit < 0 and val == 0:
                    clause_ok = True
            if not clause_ok:
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

def random_three_sat(max_vars=4, max_clauses=5):
    m = random.randint(0, max_vars)
    # ensure if clauses >0 then m>=3 per spec, but we can still generate.
    k = random.randint(0, max_clauses)
    clauses = []
    for _ in range(k):
        # pick 3 distinct vars
        if m == 0:
            break
        vars = random.sample(range(1, m+1), min(3, m))
        # if less than 3 vars, repeat to fill? skip clause.
        if len(vars) < 3:
            continue
        clause = []
        for v in vars:
            lit = v if random.choice([True, False]) else -v
            clause.append(lit)
        clauses.append(clause)
    return {'num_vars': m, 'clauses': clauses}

def main():
    random.seed(0)
    total = 0
    passed = 0
    for _ in range(200):
        inst = random_three_sat()
        # validate
        ThreeSat.validate(inst)
        sat = solve_three_sat(inst)
        red = reduce(inst)
        SubsetSum.validate(red)
        ss = solve_subset_sum(red)
        if sat == ss:
            passed += 1
        else:
            print('Mismatch!')
            print('3SAT instance:', json.dumps(inst))
            print('Expected', sat, 'got', ss)
            print('Reduced:', red)
            break
        total += 1
    print('Tests run:', total, 'passed:', passed)
    # write verdict
    verdict = {'verified': total == passed, 'tests_run': total, 'tests_passed': passed}
    with open('verdict.json', 'w') as f:
        json.dump(verdict, f)

if __name__ == '__main__':
    main()
