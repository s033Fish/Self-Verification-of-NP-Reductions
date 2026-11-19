import itertools
import random
import json
from problems import Sat, Clique
from reduce import reduce

def sat_bruteforce(instance):
    m = instance['num_vars']
    clauses = instance['clauses']
    # if any empty clause -> unsat
    for cl in clauses:
        if len(cl) == 0:
            return False
    # iterate assignments
    for bits in range(1 << m):
        ok = True
        for cl in clauses:
            clause_sat = False
            for lit in cl:
                var = abs(lit) - 1
                val = (bits >> var) & 1  # 1 means true
                if lit > 0 and val == 1:
                    clause_sat = True
                    break
                if lit < 0 and val == 0:
                    clause_sat = True
                    break
            if not clause_sat:
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
    # check subsets of size >=k, but we can just check exactly k because larger includes
    for size in range(k, n+1):
        for subset in itertools.combinations(range(n), size):
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
        lits = []
        for _ in range(random.randint(0, max_lits)):
            if m == 0:
                continue
            var = random.randint(1, m)
            sign = random.choice([1, -1])
            lits.append(sign * var)
        clauses.append(lits)
    return {"num_vars": m, "clauses": clauses}

random.seed(0)
tests = 200
passed = 0
for _ in range(tests):
    sat_inst = random_sat_instance()
    # validate
    Sat.validate(sat_inst)
    sat_ans = sat_bruteforce(sat_inst)
    clique_inst = reduce(sat_inst)
    Clique.validate(clique_inst)
    clique_ans = clique_bruteforce(clique_inst)
    if sat_ans == clique_ans:
        passed += 1
    else:
        print('Mismatch!')
        print('SAT instance', sat_inst)
        print('SAT answer', sat_ans)
        print('Clique instance', clique_inst)
        print('Clique answer', clique_ans)
        break

verdict = {
    "verified": passed == tests,
    "tests_run": tests,
    "tests_passed": passed,
}
print(json.dumps(verdict))
with open('verdict.json', 'w') as f:
    json.dump(verdict, f)
