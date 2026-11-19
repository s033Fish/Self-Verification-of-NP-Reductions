import itertools, random, json, sys
from problems import ThreeSat, Clique
from reduce import reduce


def solve_three_sat(inst):
    m = inst['num_vars']
    clauses = inst['clauses']
    # assignments as tuple of bools for variables 1..m
    for bits in itertools.product([False, True], repeat=m):
        ok = True
        for clause in clauses:
            clause_ok = False
            for lit in clause:
                var = abs(lit) - 1
                val = bits[var]
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


def solve_clique(inst):
    n = inst['n']
    edges_set = {frozenset(e) for e in inst['edges']}
    k = inst['k']
    if k <= 0:
        return True
    if k > n:
        return False
    # check all subsets of size k up to n
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


def random_three_sat_instance(max_vars=4, max_clauses=5):
    m = random.randint(0, max_vars)
    # ensure at least 3 vars if we have clauses
    if m < 3:
        # allow zero clauses only
        return {'num_vars': m, 'clauses': []}
    num_clauses = random.randint(0, max_clauses)
    clauses = []
    for _ in range(num_clauses):
        vars_in_clause = random.sample(range(1, m+1), 3)
        clause = []
        for v in vars_in_clause:
            lit = v if random.choice([True, False]) else -v
            clause.append(lit)
        clauses.append(clause)
    return {'num_vars': m, 'clauses': clauses}


def main():
    random.seed(0)
    tests = 200
    passed = 0
    for _ in range(tests):
        inst = random_three_sat_instance()
        # validate
        ThreeSat.validate(inst)
        reduced = reduce(inst)
        Clique.validate(reduced)
        ans_src = solve_three_sat(inst)
        ans_tgt = solve_clique(reduced)
        if ans_src == ans_tgt:
            passed += 1
        else:
            print('FAIL')
            print('src', inst)
            print('reduced', reduced)
            print('src ans', ans_src, 'tgt ans', ans_tgt)
            sys.exit(1)
    print('All tests passed:', passed, '/', tests)
    # write verdict
    verdict = {'verified': True, 'tests_run': tests, 'tests_passed': passed}
    with open('verdict.json', 'w') as f:
        json.dump(verdict, f)

if __name__ == '__main__':
    main()
