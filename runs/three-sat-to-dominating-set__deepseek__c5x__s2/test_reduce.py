import json
import random
import sys
from pathlib import Path

# Import problem definitions and reduction
sys.path.append(str(Path('.').resolve()))
import problems
import reduce
from three_sat_solver import solve as solve_3sat
from dominating_set_solver import solve as solve_ds


def random_three_sat(max_vars=4, max_clauses=5):
    m = random.randint(0, max_vars)
    # ensure at least 0 vars allowed, but if m>0 need clauses with distinct vars
    clauses = []
    num_clauses = random.randint(0, max_clauses)
    for _ in range(num_clauses):
        if m == 0:
            # no variables, cannot create clause, break
            break
        # pick 3 distinct variables from 1..m
        vars = random.sample(range(1, m + 1), 3) if m >= 3 else []
        if len(vars) < 3:
            # can't create a proper clause, skip
            continue
        clause = []
        for v in vars:
            lit = v if random.choice([True, False]) else -v
            clause.append(lit)
        clauses.append(clause)
    return {"num_vars": m, "clauses": clauses}


def run_tests(num_tests=200):
    passed = 0
    for i in range(num_tests):
        instance = random_three_sat()
        # validate source instance
        try:
            problems.ThreeSat.validate(instance)
        except Exception as e:
            print(f"Invalid source instance generated: {e}")
            continue
        # solve source
        ans_src = solve_3sat(instance)
        # reduce
        red = reduce.reduce(instance)
        # validate target instance
        try:
            problems.DominatingSet.validate(red)
        except Exception as e:
            print(f"Reduced instance invalid: {e}\nInstance: {instance}\nReduced: {red}")
            continue
        ans_tgt = solve_ds(red)
        # According to reduction, ans_src == ans_tgt
        if ans_src == ans_tgt:
            passed += 1
        else:
            print("Mismatch!", instance, red, ans_src, ans_tgt)
    return passed, num_tests

if __name__ == "__main__":
    passed, total = run_tests()
    result = {"verified": passed == total, "tests_run": total, "tests_passed": passed}
    print(json.dumps(result))
    Path('verdict.json').write_text(json.dumps(result))
