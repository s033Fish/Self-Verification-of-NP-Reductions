import itertools
import random
import json
import sys

import problems
from reduce import reduce


def solve_one_in_three(instance):
    m = instance["num_vars"]
    clauses = instance["clauses"]
    # Edge: no clauses always yes
    for bits in itertools.product([False, True], repeat=m):
        ok = True
        for clause in clauses:
            true_cnt = sum(bits[v-1] for v in clause)
            if true_cnt != 1:
                ok = False
                break
        if ok:
            return True
    return False


def solve_three_sat(instance):
    m = instance["num_vars"]
    clauses = instance["clauses"]
    for bits in itertools.product([False, True], repeat=m):
        ok = True
        for clause in clauses:
            lit_true = False
            for lit in clause:
                var = abs(lit) - 1
                val = bits[var]
                if lit < 0:
                    val = not val
                if val:
                    lit_true = True
                    break
            if not lit_true:
                ok = False
                break
        if ok:
            return True
    return False


def random_one_in_three_instance(max_vars=5, max_clauses=6):
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


def main():
    random.seed(0)
    tests = 200
    passed = 0
    for i in range(tests):
        src = random_one_in_three_instance()
        # validate source
        problems.OneInThreeSat.validate(src)
        tgt = reduce(src)
        problems.ThreeSat.validate(tgt)
        src_ans = solve_one_in_three(src)
        tgt_ans = solve_three_sat(tgt)
        if src_ans == tgt_ans:
            passed += 1
        else:
            print("Mismatch on test", i)
            print("src", src)
            print("tgt", tgt)
            print(src_ans, tgt_ans)
            sys.exit(1)
    result = {"verified": True, "tests_run": tests, "tests_passed": passed}
    with open('verdict.json', 'w') as f:
        json.dump(result, f)
    print(json.dumps(result))

if __name__ == "__main__":
    main()
