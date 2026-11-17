import itertools
import random
import json
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
            def lit_true(lit):
                var = abs(lit) - 1
                val = bits[var]
                return val if lit > 0 else (1 - val)
            if not (lit_true(l1) or lit_true(l2) or lit_true(l3)):
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
        m = 3
    clauses = []
    for _ in range(num_clauses):
        # pick 3 distinct vars from 1..m
        vars = random.sample(range(1, m+1), 3)
        random.shuffle(vars)
        clauses.append(vars)
    return {"num_vars": m, "clauses": clauses}


def run_tests(num_trials=200):
    passed = 0
    for _ in range(num_trials):
        src = random_one_in_three_instance()
        # validate source
        OneInThreeSat.validate(src)
        src_ans = solve_one_in_three(src)
        red = reduce(src)
        ThreeSat.validate(red)
        red_ans = solve_three_sat(red)
        if src_ans == red_ans:
            passed += 1
        else:
            print("Mismatch!", src, src_ans, red, red_ans)
            return passed, False
    return passed, True

if __name__ == "__main__":
    trials = 200
    passed, ok = run_tests(trials)
    verdict = {"verified": ok, "tests_run": trials, "tests_passed": passed}
    print(json.dumps(verdict))
    with open("verdict.json", "w") as f:
        json.dump(verdict, f)
