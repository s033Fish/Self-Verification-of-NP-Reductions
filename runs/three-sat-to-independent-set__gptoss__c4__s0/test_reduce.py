import itertools
import json
import sys
import random
from problems import ThreeSat, IndependentSet
from reduce import reduce

def solve_three_sat(instance):
    m = instance['num_vars']
    clauses = instance['clauses']
    for bits in itertools.product([False, True], repeat=m):
        ok = True
        for clause in clauses:
            clause_ok = False
            for lit in clause:
                var = abs(lit) - 1
                val = bits[var]
                if lit > 0 and val:
                    clause_ok = True
                if lit < 0 and not val:
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
    edges = set(frozenset(e) for e in instance['edges'])
    k = instance['k']
    if k <= 0:
        return True
    if k > n:
        return False
    vertices = list(range(n))
    for size in range(k, n+1):
        for subset in itertools.combinations(vertices, size):
            ok = True
            for u, v in itertools.combinations(subset, 2):
                if frozenset((u, v)) in edges:
                    ok = False
                    break
            if ok:
                return True
    return False

def random_three_sat(max_vars=4, max_clauses=5):
    """Generate a random 3‑SAT instance respecting constraints."""
    num_clauses = random.randint(0, max_clauses)
    if num_clauses == 0:
        m = random.randint(0, max_vars)
    else:
        m = random.randint(3, max_vars)
    clauses = []
    for _ in range(num_clauses):
        chosen = random.sample(range(1, m+1), 3)
        clause = []
        for v in chosen:
            lit = v if random.choice([True, False]) else -v
            clause.append(lit)
        clauses.append(clause)
    return {"num_vars": m, "clauses": clauses}

def main():
    tests = 200
    passed = 0
    for _ in range(tests):
        inst = random_three_sat()
        ThreeSat.validate(inst)
        reduced = reduce(inst)
        IndependentSet.validate(reduced)
        ans_src = solve_three_sat(inst)
        ans_tgt = solve_independent_set(reduced)
        if ans_src != ans_tgt:
            print('Mismatch')
            print('Instance', inst)
            print('Reduced', reduced)
            print('src', ans_src, 'tgt', ans_tgt)
            sys.exit(1)
        passed += 1
    verdict = {"verified": True, "tests_run": tests, "tests_passed": passed}
    with open('verdict.json', 'w') as f:
        json.dump(verdict, f)
    print('All tests passed')

if __name__ == '__main__':
    main()
