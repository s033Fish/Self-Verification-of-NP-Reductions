import random
import itertools
import json
from problems import Sat, IndependentSet
from reduce import reduce

def sat_bruteforce(instance):
    m = instance['num_vars']
    clauses = instance['clauses']
    # Edge cases handled naturally
    for bits in range(1 << m):
        assignment = [(bits >> i) & 1 == 1 for i in range(m)]  # var i+1
        ok = True
        for clause in clauses:
            clause_ok = False
            for lit in clause:
                var = abs(lit) - 1
                val = assignment[var]
                if lit > 0 and val:
                    clause_ok = True
                    break
                if lit < 0 and not val:
                    clause_ok = True
                    break
            if not clause_ok:
                ok = False
                break
        if ok:
            return True
    return False

def indep_set_bruteforce(instance):
    n = instance['n']
    edges = set()
    for u, v in instance['edges']:
        edges.add(frozenset((u, v)))
    k = instance['k']
    if k <= 0:
        return True
    if k > n:
        return False
    # iterate subsets of size >=k
    vertices = list(range(n))
    for size in range(k, n+1):
        for subset in itertools.combinations(vertices, size):
            good = True
            for u, v in itertools.combinations(subset, 2):
                if frozenset((u, v)) in edges:
                    good = False
                    break
            if good:
                return True
    return False

def random_sat_instance(max_vars=4, max_clauses=4, max_lits=3):
    m = random.randint(0, max_vars)
    num_clauses = random.randint(0, max_clauses)
    clauses = []
    for _ in range(num_clauses):
        lits = []
        num_lits = random.randint(0, max_lits)
        for _ in range(num_lits):
            if m == 0:
                continue
            var = random.randint(1, m)
            sign = random.choice([1, -1])
            lits.append(sign * var)
        clauses.append(lits)
    return {"num_vars": m, "clauses": clauses}

def run_tests(num_tests=200):
    passed = 0
    for _ in range(num_tests):
        inst = random_sat_instance()
        # validate
        Sat.validate(inst)
        sat_ans = sat_bruteforce(inst)
        red = reduce(inst)
        IndependentSet.validate(red)
        indep_ans = indep_set_bruteforce(red)
        if sat_ans == indep_ans:
            passed += 1
        else:
            print('FAIL')
            print('SAT instance', json.dumps(inst))
            print('SAT ans', sat_ans)
            print('Reduced', red)
            print('Indep ans', indep_ans)
            break
    return passed, num_tests

if __name__ == '__main__':
    passed, total = run_tests()
    print(f'Passed {passed}/{total} tests')
