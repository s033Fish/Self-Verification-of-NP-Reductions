import random
import itertools
import json
import sys
from problems import Sat, Clique
from reduce import reduce


def sat_bruteforce(instance):
    m = instance['num_vars']
    clauses = instance['clauses']
    for bits in itertools.product([False, True], repeat=m):
        assignment = {i+1: bits[i] for i in range(m)}
        ok = True
        for clause in clauses:
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


def random_sat_instance(max_vars=4, max_clauses=3, max_lits_per_clause=3):
    m = random.randint(0, max_vars)
    num_clauses = random.randint(0, max_clauses)
    clauses = []
    for _ in range(num_clauses):
        lits = []
        num_lits = random.randint(0, max_lits_per_clause)
        for __ in range(num_lits):
            if m == 0:
                continue
            var = random.randint(1, m)
            lit = var if random.choice([True, False]) else -var
            lits.append(lit)
        clauses.append(lits)
    return {"num_vars": m, "clauses": clauses}


def run_tests(num_tests=200):
    passed = 0
    for i in range(num_tests):
        inst = random_sat_instance()
        Sat.validate(inst)
        sat_res = sat_bruteforce(inst)
        red = reduce(inst)
        Clique.validate(red)
        clique_res = clique_bruteforce(red)
        if sat_res == clique_res:
            passed += 1
        else:
            print('Mismatch!')
            print('SAT instance', json.dumps(inst))
            print('SAT result', sat_res)
            print('Reduced', json.dumps(red))
            print('Clique result', clique_res)
            break
    edge_cases = [
        {"num_vars": 0, "clauses": []},
        {"num_vars": 3, "clauses": []},
        {"num_vars": 2, "clauses": [[]]},
    ]
    for ec in edge_cases:
        Sat.validate(ec)
        sat_res = sat_bruteforce(ec)
        red = reduce(ec)
        Clique.validate(red)
        clique_res = clique_bruteforce(red)
        if sat_res != clique_res:
            print('Edge case mismatch', ec, sat_res, clique_res)
            break
        else:
            passed += 1
    total = num_tests + len(edge_cases)
    print(f'Passed {passed}/{total} tests')
    return passed == total

if __name__ == '__main__':
    ok = run_tests()
    result = {"verified": ok, "tests_run": 200 + 3, "tests_passed": 200 + 3 if ok else 0}
    with open('verdict.json', 'w') as f:
        json.dump(result, f)
    sys.exit(0 if ok else 1)
