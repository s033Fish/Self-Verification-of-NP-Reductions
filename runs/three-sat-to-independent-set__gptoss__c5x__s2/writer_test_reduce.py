import itertools
import random
import json
from problems import ThreeSat, IndependentSet, InvalidInstance
from reduce import reduce

def solve_three_sat(instance):
    m = instance['num_vars']
    clauses = instance['clauses']
    # iterate over all assignments 0..(1<<m)-1
    for mask in range(1 << m):
        ok = True
        for clause in clauses:
            clause_ok = False
            for lit in clause:
                var = abs(lit) - 1  # zero-indexed
                val = (mask >> var) & 1
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

def solve_independent_set(instance):
    n = instance['n']
    edges = set()
    for u, v in instance['edges']:
        if u > v:
            u, v = v, u
        edges.add((u, v))
    k = instance['k']
    # quick yes for k<=0
    if k <= 0:
        return True
    if k > n:
        return False
    # check all subsets of size >=k
    vertices = list(range(n))
    for r in range(k, n+1):
        for subset in itertools.combinations(vertices, r):
            independent = True
            for u, v in itertools.combinations(subset, 2):
                if (min(u, v), max(u, v)) in edges:
                    independent = False
                    break
            if independent:
                return True
    return False

def random_three_sat(max_vars=4, max_clauses=4):
    m = random.randint(0, max_vars)
    # ensure if clauses>0 then m>=3 per spec, but we can allow smaller for testing.
    # generate clauses ensuring distinct vars per clause.
    clauses = []
    num_clauses = random.randint(0, max_clauses)
    for _ in range(num_clauses):
        # pick 3 distinct variables from 1..max(3,m)
        vars_pool = list(range(1, max(3, m)+1))
        if len(vars_pool) < 3:
            vars_pool = [1,2,3]
        chosen = random.sample(vars_pool, 3)
        clause = []
        for v in chosen:
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
        # validate source
        try:
            ThreeSat.validate(inst)
        except InvalidInstance as e:
            continue  # skip malformed (should be rare)
        reduced = reduce(inst)
        # validate target
        IndependentSet.validate(reduced)
        ans_src = solve_three_sat(inst)
        ans_tgt = solve_independent_set(reduced)
        total += 1
        if ans_src == ans_tgt:
            passed += 1
        else:
            print('Mismatch')
            print('Source:', inst)
            print('Reduced:', reduced)
            print('src ans', ans_src, 'tgt ans', ans_tgt)
            break
    print('tested', total, 'passed', passed)
    # write verdict
    verdict = {'verified': passed == total, 'tests_run': total, 'tests_passed': passed}
    with open('verdict.json', 'w') as f:
        json.dump(verdict, f)
    print('Verdict written')

if __name__ == '__main__':
    main()
