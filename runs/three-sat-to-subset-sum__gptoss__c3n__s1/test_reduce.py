import random
import itertools
import json
from problems import ThreeSat, SubsetSum
from reduce import reduce


def solve_three_sat(instance):
    m = instance['num_vars']
    clauses = instance['clauses']
    for mask in range(1 << m):
        ok = True
        for clause in clauses:
            clause_sat = False
            for lit in clause:
                var = abs(lit) - 1
                val = (mask >> var) & 1
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


def solve_subset_sum(instance):
    numbers = instance['numbers']
    target = instance['target']
    n = len(numbers)
    # simple subset enumeration
    for r in range(n+1):
        for combo in itertools.combinations(range(n), r):
            s = sum(numbers[i] for i in combo)
            if s == target:
                return True
    return False


def random_three_sat(max_vars=4, max_clauses=5):
    m = random.randint(0, max_vars)
    # ensure at least 3 vars if there are clauses
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


def run_tests(num_tests=200):
    passed = 0
    for _ in range(num_tests):
        src = random_three_sat()
        # validate source
        ThreeSat.validate(src)
        src_ans = solve_three_sat(src)
        red = reduce(src)
        SubsetSum.validate(red)
        tgt_ans = solve_subset_sum(red)
        if src_ans == tgt_ans:
            passed += 1
        else:
            print('FAIL', src, src_ans, red, tgt_ans)
            break
    return num_tests, passed

if __name__ == '__main__':
    total, passed = run_tests()
    result = {
        "verified": passed == total,
        "tests_run": total,
        "tests_passed": passed,
    }
    print(json.dumps(result, indent=2))
    with open('verdict.json', 'w') as f:
        json.dump(result, f)
