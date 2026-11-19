import random
import json
import sys
from pathlib import Path

# Import the modules we just created and the reduction
import problems
import reduce
from sat_solver import sat_satisfiable
from indep_solver import independent_set_exists


def generate_random_sat(max_vars=4, max_clauses=4, max_lit_per_clause=3) -> dict:
    num_vars = random.randint(0, max_vars)
    # Edge case: allow zero vars.
    clauses = []
    num_clauses = random.randint(0, max_clauses)
    for _ in range(num_clauses):
        # Randomly decide if this clause is empty (unsatisfiable edge case)
        if random.random() < 0.1:
            clauses.append([])
            continue
        lit_count = random.randint(0, max_lit_per_clause)
        clause = []
        for _ in range(lit_count):
            if num_vars == 0:
                # no variables, skip adding literals
                continue
            var = random.randint(1, num_vars)
            sign = random.choice([1, -1])
            clause.append(sign * var)
        clauses.append(clause)
    return {"num_vars": num_vars, "clauses": clauses}


def main():
    random.seed(0)
    total = 0
    passed = 0
    for _ in range(200):  # generate 200 random instances
        sat_instance = generate_random_sat()
        # Validate input instance
        try:
            problems.Sat.validate(sat_instance)
        except Exception as e:
            print("Invalid SAT instance", sat_instance, e)
            continue
        sat_ans = sat_satisfiable(sat_instance)
        indep_instance = reduce.reduce(sat_instance)
        # Validate reduction output
        try:
            problems.IndependentSet.validate(indep_instance)
        except Exception as e:
            print("Invalid reduction output", indep_instance, e)
            continue
        indep_ans = independent_set_exists(indep_instance)
        total += 1
        if sat_ans == indep_ans:
            passed += 1
        else:
            print("Mismatch!", sat_instance, sat_ans, indep_instance, indep_ans)
    verdict = {
        "verified": passed == total,
        "tests_run": total,
        "tests_passed": passed,
    }
    Path("verdict.json").write_text(json.dumps(verdict, indent=2))
    print(json.dumps(verdict, indent=2))
    sys.exit(0 if verdict["verified"] else 1)

if __name__ == "__main__":
    main()
