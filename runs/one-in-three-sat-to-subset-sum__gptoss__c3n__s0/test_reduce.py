"""Test the reduction from OneInThreeSat to SubsetSum.
Runs a number of random small instances and checks that the reduction
preserves the answer.
"""
import random
import sys
from typing import Dict

from brute_solvers import solve_one_in_three_sat, solve_subset_sum
from reduce import reduce


def random_instance(max_vars: int = 5, max_clauses: int = 5) -> Dict:
    m = random.randint(0, max_vars)
    # ensure at least 3 vars if we create clauses
    num_clauses = random.randint(0, max_clauses)
    clauses = []
    for _ in range(num_clauses):
        if m < 3:
            # cannot create a valid clause, break
            break
        clause = random.sample(range(1, m + 1), 3)
        clauses.append(clause)
    return {"num_vars": m, "clauses": clauses}


def main():
    random.seed(0)
    tests = 200
    passed = 0
    for i in range(tests):
        inst = random_instance()
        # validate using problem classes (they will raise if invalid)
        try:
            from problems import OneInThreeSat, SubsetSum
            OneInThreeSat.validate(inst)
        except Exception as e:
            # skip invalid generated instances (e.g., m<3 with clauses)
            continue
        sat_ans = solve_one_in_three_sat(inst)
        red = reduce(inst)
        ss_ans = solve_subset_sum(red)
        if sat_ans == ss_ans:
            passed += 1
        else:
            print("Mismatch on instance:", inst)
            print("Reduction:", red)
            print("sat_ans", sat_ans, "ss_ans", ss_ans)
            sys.exit(1)
    # also test edge case: no clauses
    edge = {"num_vars": 0, "clauses": []}
    from problems import OneInThreeSat, SubsetSum
    OneInOneSat = OneInThreeSat
    OneInOneSat.validate(edge)
    sat_ans = solve_one_in_three_sat(edge)
    red = reduce(edge)
    ss_ans = solve_subset_sum(red)
    assert sat_ans == ss_ans
    passed += 1
    print(f"All {passed} tests passed.")
    # write verdict.json
    import json
    verdict = {"verified": True, "tests_run": passed, "tests_passed": passed}
    with open('verdict.json', 'w') as f:
        json.dump(verdict, f)

if __name__ == "__main__":
    main()
