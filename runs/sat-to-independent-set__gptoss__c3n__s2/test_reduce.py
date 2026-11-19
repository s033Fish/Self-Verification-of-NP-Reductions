import itertools
import json
import sys
from problems import Sat, IndependentSet
from reduce import reduce

def sat_bruteforce(instance):
    m = instance['num_vars']
    clauses = instance['clauses']
    # Edge cases handled by general loop
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
    edges = {frozenset(e) for e in instance['edges']}
    k = instance['k']
    if k <= 0:
        return True
    if k > n:
        return False
    # iterate subsets of size >= k
    for r in range(k, n+1):
        for subset in itertools.combinations(range(n), r):
            good = True
            for u, v in itertools.combinations(subset, 2):
                if frozenset((u, v)) in edges:
                    good = False
                    break
            if good:
                return True
    return False

def generate_sat_instances(max_vars=3, max_clauses=3, max_clause_len=2):
    instances = []
    for m in range(max_vars+1):  # include 0 vars
        # generate all possible clauses up to max_clause_len (including empty)
        literals = []
        for v in range(1, m+1):
            literals.extend([v, -v])
        # include empty clause
        possible_clauses = [[]]
        # generate all combinations of literals with repetition allowed? For simplicity, use combinations without repetition.
        for l in range(1, max_clause_len+1):
            for combo in itertools.combinations(literals, l):
                possible_clauses.append(list(combo))
        # now generate up to max_clauses clauses (allow repetitions)
        for num_clauses in range(max_clauses+1):
            for clause_list in itertools.product(possible_clauses, repeat=num_clauses):
                instances.append({"num_vars": m, "clauses": [list(c) for c in clause_list]})
    return instances


def main():
    tests = 0
    passed = 0
    for inst in generate_sat_instances():
        # validate
        Sat.validate(inst)
        sat_ans = sat_bruteforce(inst)
        red = reduce(inst)
        IndependentSet.validate(red)
        indep_ans = indep_set_bruteforce(red)
        tests += 1
        if sat_ans == indep_ans:
            passed += 1
        else:
            print('Mismatch!')
            print('SAT instance:', json.dumps(inst))
            print('SAT answer:', sat_ans)
            print('Reduced:', json.dumps(red))
            print('IS answer:', indep_ans)
            sys.exit(1)
    print('All tests passed:', passed, '/', tests)
    # write verdict
    verdict = {"verified": True, "tests_run": tests, "tests_passed": passed}
    with open('verdict.json', 'w') as f:
        json.dump(verdict, f)

if __name__ == '__main__':
    main()
