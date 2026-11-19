import random
import itertools
import sys
import json
from problems import Sat, Clique
from reduce import reduce

def sat_bruteforce(instance):
    m = instance['num_vars']
    clauses = instance['clauses']
    # Edge case: empty clause => unsat
    for clause in clauses:
        if len(clause) == 0:
            return False
    # Iterate over all assignments
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

def clique_bruteforce(instance):
    n = instance['n']
    edges_set = {frozenset(e) for e in instance['edges']}
    k = instance['k']
    if k <= 0:
        return True
    if k == 1:
        return n >= 1
    if k > n:
        return False
    # Check all subsets of size >= k
    vertices = list(range(n))
    for size in range(k, n+1):
        for subset in itertools.combinations(vertices, size):
            good = True
            for u, v in itertools.combinations(subset, 2):
                if frozenset((u, v)) not in edges_set:
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
        clause_len = random.randint(0, max_lits)
        clause = []
        for _ in range(clause_len):
            if m == 0:
                # no vars, but literals must be valid -> skip adding literals
                continue
            var = random.randint(1, m)
            sign = random.choice([1, -1])
            clause.append(sign * var)
        clauses.append(clause)
    return {"num_vars": m, "clauses": clauses}

def run_tests(num_tests=200):
    passed = 0
    for i in range(num_tests):
        sat_inst = random_sat_instance()
        # validate
        Sat.validate(sat_inst)
        sat_ans = sat_bruteforce(sat_inst)
        clique_inst = reduce(sat_inst)
        Clique.validate(clique_inst)
        clique_ans = clique_bruteforce(clique_inst)
        if sat_ans != clique_ans:
            print('Mismatch on test', i)
            print('SAT instance:', json.dumps(sat_inst))
            print('Reduced Clique:', json.dumps(clique_inst))
            print('SAT answer', sat_ans, 'Clique answer', clique_ans)
            sys.exit(1)
        passed += 1
    print('All', passed, 'tests passed')
    return passed

if __name__ == '__main__':
    total = run_tests()
    verdict = {"verified": True, "tests_run": total, "tests_passed": total}
    with open('verdict.json', 'w') as f:
        json.dump(verdict, f)
