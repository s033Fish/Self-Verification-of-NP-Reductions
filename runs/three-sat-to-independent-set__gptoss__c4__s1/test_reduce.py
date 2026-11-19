import random
import itertools
import json
import sys
from problems import ThreeSat, IndependentSet
from reduce import reduce

def three_sat_bruteforce(instance):
    m = instance['num_vars']
    clauses = instance['clauses']
    # iterate all assignments as bitmask 0..2^m-1, where True means variable true
    for mask in range(1 << m):
        ok = True
        for clause in clauses:
            clause_ok = False
            for lit in clause:
                var = abs(lit) - 1
                val = bool((mask >> var) & 1)
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

def independent_set_bruteforce(instance):
    n = instance['n']
    edges = set(frozenset(e) for e in instance['edges'])
    k = instance['k']
    # any subset of size >=k
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

def random_three_sat(max_vars=4, max_clauses=5):
    m = random.randint(0, max_vars)
    # ensure at least 3 vars if clauses exist per spec, but we can allow less for testing
    num_clauses = random.randint(0, max_clauses)
    clauses = []
    for _ in range(num_clauses):
        # pick 3 distinct variables from 1..max(1,m)
        vars_pool = list(range(1, max(1, m)+1))
        if len(vars_pool) < 3:
            # if not enough vars, just fill with repeats of new vars (allow invalid?)
            # To keep valid, set m at least 3 when clauses>0
            m = max(m, 3)
            vars_pool = list(range(1, m+1))
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
        except Exception as e:
            print('Invalid generated instance', e)
            continue
        src_yes = three_sat_bruteforce(inst)
        tgt = reduce(inst)
        tgt_yes = independent_set_bruteforce(tgt)
        total += 1
        if src_yes == tgt_yes:
            passed += 1
        else:
            print('Mismatch!')
            print('Source:', json.dumps(inst))
            print('Source yes:', src_yes)
            print('Target:', json.dumps(tgt))
            print('Target yes:', tgt_yes)
            sys.exit(1)
    # also test edge case empty clauses
    empty = {'num_vars': 0, 'clauses': []}
    ThreeSat.validate(empty)
    src_yes = three_sat_bruteforce(empty)
    tgt = reduce(empty)
    tgt_yes = independent_set_bruteforce(tgt)
    total += 1
    if src_yes == tgt_yes:
        passed += 1
    else:
        print('Mismatch on empty case')
        sys.exit(1)
    print('Tests run:', total, 'passed:', passed)
    # write verdict
    verdict = {'verified': True, 'tests_run': total, 'tests_passed': passed}
    with open('verdict.json', 'w') as f:
        json.dump(verdict, f)

if __name__ == '__main__':
    main()
