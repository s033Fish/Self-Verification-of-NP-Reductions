import itertools, random, json, sys
from problems import ThreeSat, OneInThreeSat
from reduce import reduce

def solve_three_sat(instance):
    m = instance['num_vars']
    clauses = instance['clauses']
    for assign in itertools.product([False, True], repeat=m):
        ok = True
        for cl in clauses:
            sat = False
            for lit in cl:
                var = abs(lit) - 1
                val = assign[var]
                if (lit > 0 and val) or (lit < 0 and not val):
                    sat = True
                    break
            if not sat:
                ok = False
                break
        if ok:
            return True
    return False

def solve_one_in_three_sat(instance):
    m = instance['num_vars']
    clauses = instance['clauses']
    for assign in itertools.product([0,1], repeat=m):
        ok = True
        for cl in clauses:
            cnt = sum(assign[i-1] for i in cl)
            if cnt != 1:
                ok = False
                break
        if ok:
            return True
    return False

def random_three_sat(max_vars=5, max_clauses=5):
    m = random.randint(0, max_vars)
    # ensure at least 3 vars if there are clauses
    have_clause = random.choice([True, False])
    clauses = []
    if have_clause:
        if m < 3:
            m = 3
        num_clauses = random.randint(1, max_clauses)
        for _ in range(num_clauses):
            vars = random.sample(range(1, m+1), 3)
            clause = []
            for v in vars:
                lit = v if random.choice([True, False]) else -v
                clause.append(lit)
            clauses.append(clause)
    return {"num_vars": m, "clauses": clauses}

random.seed(0)
tests = 0
passed = 0
for _ in range(200):
    inst = random_three_sat()
    # validate
    ThreeSat.validate(inst)
    reduced = reduce(inst)
    OneInThreeSat.validate(reduced)
    ans_src = solve_three_sat(inst)
    ans_tgt = solve_one_in_three_sat(reduced)
    tests += 1
    if ans_src == ans_tgt:
        passed += 1
    else:
        print('FAIL')
        print('src', inst)
        print('reduced', reduced)
        print('src ans', ans_src, 'tgt ans', ans_tgt)
        sys.exit(1)

verdict = {"verified": passed == tests, "tests_run": tests, "tests_passed": passed}
with open('verdict.json', 'w') as f:
    json.dump(verdict, f)
print('All tests passed', passed, '/', tests)
