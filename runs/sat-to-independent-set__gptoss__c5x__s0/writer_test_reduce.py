import itertools
import random
import json
from problems import Sat, IndependentSet
from reduce import reduce

def sat_bruteforce(instance):
    m = instance['num_vars']
    clauses = instance['clauses']
    for bits in range(1 << m):
        assignment = [(bits >> i) & 1 == 1 for i in range(m)]
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
        a, b = min(u, v), max(u, v)
        edges.add((a, b))
    k = instance['k']
    if k <= 0:
        return True
    if k > n:
        return False
    for size in range(k, n+1):
        for subset in itertools.combinations(range(n), size):
            good = True
            for i in range(len(subset)):
                for j in range(i+1, len(subset)):
                    if (subset[i], subset[j]) in edges:
                        good = False
                        break
                if not good:
                    break
            if good:
                return True
    return False

def random_sat_instance(max_vars=4, max_clauses=4, max_lits=3):
    """Generate a random SAT instance that respects the validation rules.
    The original generator could produce literals referencing variables that do
    not exist (e.g., when ``num_vars`` is 0). This version ensures that literals
    are only created when ``num_vars`` > 0; otherwise all clauses are empty.
    """
    m = random.randint(0, max_vars)
    c = random.randint(0, max_clauses)
    clauses = []
    for _ in range(c):
        if m == 0:
            clauses.append([])
            continue
        l = random.randint(0, max_lits)
        clause = []
        for _ in range(l):
            var = random.randint(1, m)
            lit = var if random.choice([True, False]) else -var
            clause.append(lit)
        clauses.append(clause)
    return {"num_vars": m, "clauses": clauses}

def run_tests(num=200):
    passed = 0
    for i in range(num):
        inst = random_sat_instance()
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
            print('SAT answer', sat_ans)
            print('Reduced', json.dumps(red))
            print('Indep answer', indep_ans)
            break
    return passed, num

if __name__ == '__main__':
    passed, total = run_tests(500)
    print(f'Passed {passed}/{total}')
    verdict = {
        "verified": passed == total,
        "tests_run": total,
        "tests_passed": passed,
    }
    with open('verdict.json', 'w') as f:
        json.dump(verdict, f)
    print('Verdict written to verdict.json')
