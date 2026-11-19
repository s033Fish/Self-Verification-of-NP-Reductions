import random
import json
import sys
from pathlib import Path

# Import problem definitions
import problems
from three_sat_solver import three_sat_solver
from clique_solver import clique_solver
from reduce import reduce as reduce_fn

def generate_random_three_sat(max_vars=4, max_clauses=4):
    m = random.randint(0, max_vars)  # allow 0 vars
    # ensure at least 3 vars if we have clauses
    if m < 3:
        # we may still generate clauses with fewer variables but that would violate validation
        # So if we want clauses, set m >=3
        pass
    # decide number of clauses
    num_clauses = random.randint(0, max_clauses)
    # ensure validity: if num_clauses>0 then m>=3
    if num_clauses > 0 and m < 3:
        m = random.randint(3, max_vars)
    clauses = []
    for _ in range(num_clauses):
        # pick 3 distinct variables from 1..m
        vars = random.sample(range(1, m+1), 3)
        clause = []
        for v in vars:
            lit = v if random.choice([True, False]) else -v
            clause.append(lit)
        clauses.append(clause)
    return {"num_vars": m, "clauses": clauses}


def run_test(num_tests=200):
    passed = 0
    for i in range(num_tests):
        instance = generate_random_three_sat()
        # validate source instance (may raise)
        try:
            problems.SOURCE.validate(instance)
        except Exception as e:
            print(f"Invalid generated instance: {e}", file=sys.stderr)
            continue
        sat = three_sat_solver(instance)
        reduced = reduce_fn(instance)
        # validate target instance
        try:
            problems.TARGET.validate(reduced)
        except Exception as e:
            print(f"Reduction produced invalid target instance: {e}", file=sys.stderr)
            continue
        clique = clique_solver(reduced)
        if sat == clique:
            passed += 1
        else:
            print("Mismatch!", instance, reduced, sat, clique, file=sys.stderr)
    return num_tests, passed

if __name__ == "__main__":
    total, passed = run_test()
    result = {"verified": passed == total, "tests_run": total, "tests_passed": passed}
    Path('verdict.json').write_text(json.dumps(result, indent=2))
    print(json.dumps(result))
