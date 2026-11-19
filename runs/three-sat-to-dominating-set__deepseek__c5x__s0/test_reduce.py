import random
import json
import sys
from pathlib import Path

# Import problem definitions and reduction
import problems
import reduce

# Import our brute-force solvers
from three_sat_solver import solve_three_sat
from dominating_set_solver import solve_dominating_set

def generate_instance(max_vars=4, max_clauses=4):
    m = random.randint(0, max_vars)
    # Ensure if there are clauses, m >= 3 as per spec, but we can still generate m<3 with zero clauses.
    if m < 3:
        # allow clauses only if m>=3, else set zero clauses
        num_clauses = 0
    else:
        num_clauses = random.randint(0, max_clauses)
    clauses = []
    for _ in range(num_clauses):
        # pick 3 distinct variables from 1..m
        vars_ = random.sample(range(1, m+1), 3)
        clause = []
        for v in vars_:
            lit = v if random.choice([True, False]) else -v
            clause.append(lit)
        clauses.append(clause)
    return {"num_vars": m, "clauses": clauses}


def main():
    total = 0
    passed = 0
    random.seed(0)
    for _ in range(200):
        instance = generate_instance()
        # Validate source instance
        try:
            problems.SOURCE.validate(instance)
        except Exception as e:
            print("Invalid source instance generated", e)
            continue
        # Compute answers
        ans_source = solve_three_sat(instance)
        # Reduce
        red = reduce.reduce(instance)
        # Validate target instance
        try:
            problems.TARGET.validate(red)
        except Exception as e:
            print("Reduced instance invalid", e)
            continue
        ans_target = solve_dominating_set(red)
        total += 1
        if ans_source == ans_target:
            passed += 1
        else:
            print("Mismatch!", instance, red, ans_source, ans_target)
    verdict = {
        "verified": passed == total,
        "tests_run": total,
        "tests_passed": passed,
    }
    Path("verdict.json").write_text(json.dumps(verdict))
    print(json.dumps(verdict))

if __name__ == "__main__":
    main()
