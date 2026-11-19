import random
import itertools
import json
from reduce import reduce
from problems import OneInThreeSat, ThreeSat

def solve_one_in_three(instance):
    m = instance['num_vars']
    clauses = instance['clauses']
    for bits in itertools.product([False, True], repeat=m):
        ok = True
        for a, b, c in clauses:
            cnt = bits[a-1] + bits[b-1] + bits[c-1]
            if cnt != 1:
                ok = False
                break
        if ok:
            return True
    return False

def solve_three_sat(instance):
    m = instance['num_vars']
    clauses = instance['clauses']
    for bits in itertools.product([False, True], repeat=m):
        ok = True
        for l1, l2, l3 in clauses:
            def lit_true(lit):
                v = abs(lit) - 1
                val = bits[v]
                return val if lit > 0 else (not val)
            if not (lit_true(l1) or lit_true(l2) or lit_true(l3)):
                ok = False
                break
        if ok:
            return True
    return False

def random_one_in_three_instance(max_vars=5, max_clauses=5):
    m = random.randint(0, max_vars)
    # ensure at least 3 vars if clauses exist
    if m < 3:
        # either zero clauses or adjust later
        pass
    num_clauses = random.randint(0, max_clauses)
    clauses = []
    for _ in range(num_clauses):
        if m < 3:
            # create dummy vars by setting m=3
            m = 3
        vars = random.sample(range(1, m+1), 3)
        clauses.append(vars)
    return {"num_vars": m, "clauses": clauses}

random.seed(0)
tests = 0
passed = 0
for _ in range(200):
    inst = random_one_in_three_instance()
    # validate source
    OneInThreeSat.validate(inst)
    src_ans = solve_one_in_three(inst)
    red = reduce(inst)
    ThreeSat.validate(red)
    tgt_ans = solve_three_sat(red)
    tests += 1
    if src_ans == tgt_ans:
        passed += 1
    else:
        print("Mismatch!", inst, src_ans, tgt_ans)
        break
print(f"Tests run: {tests}, passed: {passed}")
with open('verdict.json', 'w') as f:
    json.dump({"verified": passed==tests, "tests_run": tests, "tests_passed": passed}, f)
