import random
import itertools
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
    # No clauses => sat
    if not clauses:
        return True
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
    edges = set()
    for u, v in instance['edges']:
        edges.add((u, v))
        edges.add((v, u))
    k = instance['k']
    # edge cases
    if k <= 0:
        return True
    if k == 1:
        return n >= 1
    if k > n:
        return False
    # check any subset of size k forms clique
    for subset in itertools.combinations(range(n), k):
        good = True
        for i in range(k):
            for j in range(i + 1, k):
                if (subset[i], subset[j]) not in edges:
                    good = False
                    break
            if not good:
                break
        if good:
            return True
    return False


def random_sat_instance(max_vars=4, max_clauses=4, max_lits_per_clause=3):
    m = random.randint(0, max_vars)
    num_clauses = random.randint(0, max_clauses)
    clauses = []
    for _ in range(num_clauses):
        lits = []
        num_lits = random.randint(0, max_lits_per_clause)
        for _ in range(num_lits):
            if m == 0:
                continue
            var = random.randint(1, m)
            sign = random.choice([1, -1])
            lits.append(sign * var)
        clauses.append(lits)
    return {"num_vars": m, "clauses": clauses}


def run_tests(num_trials=200):
    passed = 0
    for _ in range(num_trials):
        inst = random_sat_instance()
        # validate
        Sat.validate(inst)
        sat_res = sat_bruteforce(inst)
        clique_inst = reduce(inst)
        Clique.validate(clique_inst)
        clique_res = clique_bruteforce(clique_inst)
        if sat_res == clique_res:
            passed += 1
        else:
            print('Mismatch!')
            print('SAT instance:', json.dumps(inst))
            print('SAT result:', sat_res)
            print('Clique instance:', json.dumps(clique_inst))
            print('Clique result:', clique_res)
            break
    return passed, num_trials

if __name__ == '__main__':
    passed, total = run_tests(500)
    print(f'Passed {passed}/{total} tests')
    verdict = {
        "verified": passed == total,
        "tests_run": total,
        "tests_passed": passed,
    }
    with open('verdict.json', 'w') as f:
        json.dump(verdict, f)
    print('Verdict written to verdict.json')
