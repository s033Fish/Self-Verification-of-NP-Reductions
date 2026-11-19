import random
import json
import sys
from itertools import product

import problems
from reduce import reduce as reduce_instance

from three_sat_solver import solve as solve_three_sat
from dominating_set_solver import solve as solve_dom_set


def random_three_sat(max_vars=4, max_clauses=5):
    m = random.randint(0, max_vars)
    # ensure at least 0 vars allowed, but clauses need m>=3 if any clause
    clauses = []
    num_clauses = random.randint(0, max_clauses)
    for _ in range(num_clauses):
        if m < 3:
            # cannot create a valid clause, break
            break
        # pick 3 distinct variables
        vars_ = random.sample(range(1, m + 1), 3)
        clause = []
        for v in vars_:
            lit = v if random.choice([True, False]) else -v
            clause.append(lit)
        clauses.append(clause)
    return {"num_vars": m, "clauses": clauses}


def run_tests(num_tests=200):
    passed = 0
    for i in range(num_tests):
        instance = random_three_sat()
        # validate source
        try:
            problems.ThreeSat.validate(instance)
        except Exception as e:
            print(f"Invalid source instance generated: {e}", file=sys.stderr)
            continue
        # solve source
        src_ans = solve_three_sat(instance)
        # reduce
        try:
            target = reduce_instance(instance)
        except Exception as e:
            print(f"Reduction raised error on test {i}: {e}", file=sys.stderr)
            continue
        # validate target
        try:
            problems.DominatingSet.validate(target)
        except Exception as e:
            print(f"Invalid target instance on test {i}: {e}", file=sys.stderr)
            continue
        # solve target
        tgt_ans = solve_dom_set(target)
        # according to reduction, formula satisfiable iff dominating set <= k
        if src_ans == tgt_ans:
            passed += 1
        else:
            print(f"Mismatch on test {i}: src={src_ans}, tgt={tgt_ans}")
    result = {"verified": passed == num_tests, "tests_run": num_tests, "tests_passed": passed}
    with open('verdict.json', 'w') as f:
        json.dump(result, f)
    print(json.dumps(result))

if __name__ == '__main__':
    run_tests()
