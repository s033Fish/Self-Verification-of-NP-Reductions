import random
import itertools
import json
import sys

from problems import OneInThreeSat, ThreeSat
from reduce import reduce


def solve_one_in_three(instance):
    m = instance["num_vars"]
    clauses = instance["clauses"]
    for bits in itertools.product([0, 1], repeat=m):
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
    m = instance["num_vars"]
    clauses = instance["clauses"]
    for bits in itertools.product([0, 1], repeat=m):
        ok = True
        for l1, l2, l3 in clauses:
            def lit_val(l):
                v = abs(l) - 1
                val = bits[v]
                return val if l > 0 else 1 - val
            if not (lit_val(l1) or lit_val(l2) or lit_val(l3)):
                ok = False
                break
        if ok:
            return True
    return False


def generate_random_one_in_three(m, max_clauses=5):
    clauses = []
    num_clauses = random.randint(0, max_clauses)
    for _ in range(num_clauses):
        # pick 3 distinct vars
        vars = random.sample(range(1, m+1), 3) if m >= 3 else []
        if vars:
            clauses.append(vars)
    return {"num_vars": m, "clauses": clauses}


tests_run = 0
tests_passed = 0
random.seed(0)
for m in range(0, 5):
    # include edge case of no clauses
    for _ in range(20):
        inst = generate_random_one_in_three(m)
        # validate
        try:
            OneInThreeSat.validate(inst)
        except Exception as e:
            print("Invalid generated instance", inst, e)
            sys.exit(1)
        red = reduce(inst)
        # validate target
        ThreeSat.validate(red)
        ans_src = solve_one_in_three(inst)
        ans_tgt = solve_three_sat(red)
        tests_run += 1
        if ans_src == ans_tgt:
            tests_passed += 1
        else:
            print("Mismatch!", inst, red, ans_src, ans_tgt)
            sys.exit(1)

# write verdict
verdict = {
    "verified": tests_run == tests_passed,
    "tests_run": tests_run,
    "tests_passed": tests_passed,
}
with open('verdict.json', 'w') as f:
    json.dump(verdict, f)
print(json.dumps(verdict))
