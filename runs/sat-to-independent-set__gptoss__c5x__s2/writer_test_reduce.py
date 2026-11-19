import random
import itertools
import json
from problems import Sat, IndependentSet
from reduce import reduce

def sat_solver(instance):
    m = instance['num_vars']
    clauses = instance['clauses']
    # Edge cases handled automatically
    for bits in itertools.product([False, True], repeat=m):
        assignment = {i+1: bits[i] for i in range(m)}
        ok = True
        for clause in clauses:
            # empty clause -> unsatisfied
            if len(clause) == 0:
                ok = False
                break
            clause_ok = False
            for lit in clause:
                var = abs(lit)
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

def independent_set_solver(instance):
    n = instance['n']
    edges = set()
    for u, v in instance['edges']:
        edges.add(frozenset((u, v)))
    k = instance['k']
    if k <= 0:
        return True
    if k > n:
        return False
    # try all subsets of size >= k
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

def random_sat_instance(max_vars=3, max_clauses=3, max_lits=3):
    m = random.randint(0, max_vars)
    num_clauses = random.randint(0, max_clauses)
    clauses = []
    for _ in range(num_clauses):
        lits = []
        num_lits = random.randint(0, max_lits)
        for __ in range(num_lits):
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
        sat_inst = random_sat_instance()
        # Validate
        Sat.validate(sat_inst)
        red = reduce(sat_inst)
        IndependentSet.validate(red)
        sat_ans = sat_solver(sat_inst)
        ind_ans = independent_set_solver(red)
        if sat_ans == ind_ans:
            passed += 1
        else:
            print('FAIL')
            print('SAT instance', json.dumps(sat_inst))
            print('Reduced', json.dumps(red))
            print('SAT ans', sat_ans, 'IS ans', ind_ans)
            break
    return passed, num_tests

if __name__ == '__main__':
    passed, total = run_tests()
    verdict = {
        "verified": passed == total,
        "tests_run": total,
        "tests_passed": passed,
    }
    print(json.dumps(verdict))
    with open('verdict.json', 'w') as f:
        json.dump(verdict, f)
