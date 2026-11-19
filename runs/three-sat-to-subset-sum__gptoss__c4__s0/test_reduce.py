import random
import itertools
import sys
from problems import ThreeSat, SubsetSum
from reduce import reduce

def three_sat_bruteforce(instance):
    m = instance['num_vars']
    clauses = instance['clauses']
    for mask in range(1 << m):
        ok = True
        for clause in clauses:
            clause_ok = False
            for lit in clause:
                var = abs(lit) - 1
                val = (mask >> var) & 1
                if (lit > 0 and val == 1) or (lit < 0 and val == 0):
                    clause_ok = True
                    break
            if not clause_ok:
                ok = False
                break
        if ok:
            return True
    return False

def subset_sum_bruteforce(instance):
    nums = instance['numbers']
    target = instance['target']
    n = len(nums)
    # simple subset enumeration
    for r in range(n+1):
        for combo in itertools.combinations(range(n), r):
            s = sum(nums[i] for i in combo)
            if s == target:
                return True
    return False

def random_three_sat_instance(max_vars=4, max_clauses=5):
    m = random.randint(0, max_vars)
    # ensure at least 3 vars if there are clauses
    if m < 3:
        # maybe no clauses
        clauses = []
    else:
        num_clauses = random.randint(0, max_clauses)
        clauses = []
        for _ in range(num_clauses):
            # pick 3 distinct vars
            vars = random.sample(range(1, m+1), 3)
            clause = []
            for v in vars:
                lit = v if random.choice([True, False]) else -v
                clause.append(lit)
            clauses.append(clause)
    return {'num_vars': m, 'clauses': clauses}


def main():
    random.seed(0)
    tests = 200
    passed = 0
    for i in range(tests):
        inst = random_three_sat_instance()
        # validate source
        ThreeSat.validate(inst)
        ans1 = three_sat_bruteforce(inst)
        red = reduce(inst)
        # validate target
        SubsetSum.validate(red)
        ans2 = subset_sum_bruteforce(red)
        if ans1 != ans2:
            print('Mismatch on instance', inst)
            print('Reduced to', red)
            sys.exit(1)
        passed += 1
    print('All', passed, 'tests passed')

if __name__ == '__main__':
    main()
