import random
import itertools
import json
from problems import ThreeSat, IndependentSet
from reduce import reduce


def solve_three_sat(instance):
    m = instance['num_vars']
    clauses = instance['clauses']
    # iterate all assignments
    for bits in range(1 << m):
        ok = True
        for clause in clauses:
            clause_ok = False
            for lit in clause:
                var = abs(lit) - 1  # zero-index
                val = (bits >> var) & 1
                if lit > 0 and val == 1:
                    clause_ok = True
                if lit < 0 and val == 0:
                    clause_ok = True
                if clause_ok:
                    break
            if not clause_ok:
                ok = False
                break
        if ok:
            return True
    return False


def solve_independent_set(instance):
    n = instance['n']
    edges = set()
    for u, v in instance['edges']:
        if u > v:
            u, v = v, u
        edges.add((u, v))
    k = instance['k']
    # check all subsets
    for r in range(k, n + 1):
        for subset in itertools.combinations(range(n), r):
            good = True
            for i in range(len(subset)):
                for j in range(i + 1, len(subset)):
                    a, b = subset[i], subset[j]
                    if a > b:
                        a, b = b, a
                    if (a, b) in edges:
                        good = False
                        break
                if not good:
                    break
            if good:
                return True
    return False


def random_three_sat_instance(max_vars=4, max_clauses=4):
    m = random.randint(0, max_vars)
    # ensure m>=3 if there are clauses, else allow any
    if m < 3:
        # may still generate clauses only if m>=3, so set clauses empty
        clauses = []
    else:
        num_clauses = random.randint(0, max_clauses)
        clauses = []
        for _ in range(num_clauses):
            vars_in_clause = random.sample(range(1, m + 1), 3)
            clause = []
            for v in vars_in_clause:
                lit = v if random.choice([True, False]) else -v
                clause.append(lit)
            clauses.append(clause)
    return {'num_vars': m, 'clauses': clauses}


def run_tests(num_tests=200):
    passed = 0
    for _ in range(num_tests):
        src = random_three_sat_instance()
        # validate source
        ThreeSat.validate(src)
        tgt = reduce(src)
        IndependentSet.validate(tgt)
        ans_src = solve_three_sat(src)
        ans_tgt = solve_independent_set(tgt)
        if ans_src == ans_tgt:
            passed += 1
        else:
            print('Mismatch!')
            print('src', src)
            print('tgt', tgt)
            print('src ans', ans_src, 'tgt ans', ans_tgt)
            break
    return passed, num_tests

if __name__ == '__main__':
    passed, total = run_tests(500)
    result = {
        'verified': passed == total,
        'tests_run': total,
        'tests_passed': passed,
    }
    print(json.dumps(result))
    with open('verdict.json', 'w') as f:
        json.dump(result, f)
