import random
import itertools
import json
from problems import OneInThreeSat, ThreeSat
from reduce import reduce

def solve_one_in_three(instance):
    m = instance["num_vars"]
    clauses = instance["clauses"]
    for bits in itertools.product([0, 1], repeat=m):
        ok = True
        for (a, b, c) in clauses:
            # variables are 1-indexed
            true_cnt = bits[a-1] + bits[b-1] + bits[c-1]
            if true_cnt != 1:
                ok = False
                break
        if ok:
            return True
    return False

def solve_three_sat(instance):
    m = instance["num_vars"]
    clauses = instance["clauses"]
    for bits in itertools.product([0, 1], repeat=m):
        ok = True
        for clause in clauses:
            clause_sat = False
            for lit in clause:
                var = abs(lit)
                val = bits[var-1]
                if lit > 0 and val == 1:
                    clause_sat = True
                if lit < 0 and val == 0:
                    clause_sat = True
                if clause_sat:
                    break
            if not clause_sat:
                ok = False
                break
        if ok:
            return True
    return False

def random_one_in_three_instance(max_vars=5, max_clauses=5):
    m = random.randint(0, max_vars)
    # ensure at least 3 vars if there are clauses
    num_clauses = random.randint(0, max_clauses)
    if num_clauses > 0 and m < 3:
        m = random.randint(3, max_vars)
    clauses = []
    for _ in range(num_clauses):
        # pick 3 distinct vars from 1..m
        vars = random.sample(range(1, m+1), 3)
        random.shuffle(vars)
        clauses.append(vars)
    return {"num_vars": m, "clauses": clauses}

random.seed(0)
tests = 200
passed = 0
for _ in range(tests):
    src = random_one_in_three_instance()
    # validate source
    OneInThreeSat.validate(src)
    tgt = reduce(src)
    ThreeSat.validate(tgt)
    ans_src = solve_one_in_three(src)
    ans_tgt = solve_three_sat(tgt)
    if ans_src == ans_tgt:
        passed += 1
    else:
        print("Mismatch!", src, tgt, ans_src, ans_tgt)
        break

verdict = {
    "verified": passed == tests,
    "tests_run": tests,
    "tests_passed": passed,
}
with open('verdict.json', 'w') as f:
    json.dump(verdict, f, indent=2)
print(json.dumps(verdict))
