import random
import itertools
import json
from typing import List, Dict

from solver_one_in_three_sat import is_satisfiable
from solver_exact_cover import is_exact_cover
from reduce import reduce


def random_instance(max_vars=4, max_clauses=4) -> Dict:
    m = random.randint(0, max_vars)
    # ensure if clauses >0 then m>=3 per spec, but we can still generate with m<3 and zero clauses.
    if m < 3:
        # force zero clauses
        clauses = []
    else:
        num_clauses = random.randint(0, max_clauses)
        clauses = []
        for _ in range(num_clauses):
            # pick 3 distinct vars from 1..m
            clause = random.sample(range(1, m+1), 3)
            clauses.append(clause)
    return {"num_vars": m, "clauses": clauses}


def test_random(num_trials=200):
    passed = 0
    for _ in range(num_trials):
        inst = random_instance()
        sat = is_satisfiable(inst)
        red = reduce(inst)
        ec = is_exact_cover(red)
        if sat == ec:
            passed += 1
        else:
            print("FAIL", json.dumps(inst), "sat", sat, "ec", ec)
            return False
    print(f"All {passed}/{num_trials} random tests passed")
    return True


def test_exhaustive_small():
    # Exhaustively test all instances with m up to 3 and up to 2 clauses
    for m in range(0,4):
        # generate all possible clause sets up to 2 clauses
        vars_range = list(range(1,m+1))
        possible_clauses = []
        if m >= 3:
            for combo in itertools.combinations(vars_range,3):
                possible_clauses.append(list(combo))
        # generate all multiset of clauses of size 0..2
        for num in range(0,3):
            for clauses in itertools.product(possible_clauses, repeat=num):
                inst = {"num_vars": m, "clauses": [list(c) for c in clauses]}
                sat = is_satisfiable(inst)
                red = reduce(inst)
                ec = is_exact_cover(red)
                if sat != ec:
                    print("FAIL", inst, sat, ec)
                    return False
    print("Exhaustive small tests passed")
    return True

if __name__ == "__main__":
    ok = test_exhaustive_small() and test_random(200)
    import json, os
    result = {"verified": ok, "tests_run": 200 + 1, "tests_passed": 200 + 1 if ok else 0}
    with open("verdict.json", "w") as f:
        json.dump(result, f)
    exit(0 if ok else 1)
