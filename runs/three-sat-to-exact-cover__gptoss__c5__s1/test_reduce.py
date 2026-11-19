import random
import json
import sys
from typing import Dict, Any, List

sys.path.append('.')  # ensure local imports work

from problems import ThreeSat, ExactCover
from reduce import reduce as reduce_instance
from three_sat_solver import solve as solve_three_sat
from exact_cover_solver import solve as solve_exact_cover


def random_three_sat_instance(max_vars: int = 4, max_clauses: int = 5) -> Dict[str, Any]:
    num_vars = random.randint(0, max_vars)
    # If less than 3 vars, we cannot create valid 3-literal clauses, so produce no clauses.
    if num_vars < 3:
        clauses: List[List[int]] = []
    else:
        num_clauses = random.randint(0, max_clauses)
        clauses = []
        for _ in range(num_clauses):
            vars_in_clause = random.sample(range(1, num_vars + 1), 3)
            clause = []
            for v in vars_in_clause:
                lit = v if random.choice([True, False]) else -v
                clause.append(lit)
            clauses.append(clause)
    return {"num_vars": num_vars, "clauses": clauses}


def run_tests(num_trials: int = 200) -> Dict[str, int]:
    passed = 0
    total = 0
    for _ in range(num_trials):
        instance = random_three_sat_instance()
        # Validate source instance
        ThreeSat.validate(instance)
        three_sat_answer = solve_three_sat(instance)
        reduced = reduce_instance(instance)
        # Validate target instance
        ExactCover.validate(reduced)
        exact_cover_answer = solve_exact_cover(reduced)
        total += 1
        if three_sat_answer == exact_cover_answer:
            passed += 1
        else:
            # Print failing instance for debugging
            print("Mismatch!", instance, reduced, three_sat_answer, exact_cover_answer, file=sys.stderr)
    return {"tests_run": total, "tests_passed": passed}

if __name__ == "__main__":
    result = run_tests()
    verified = result["tests_passed"] == result["tests_run"]
    verdict = {"verified": verified, "tests_run": result["tests_run"], "tests_passed": result["tests_passed"]}
    print(json.dumps(verdict))
    # Also write to file for the final output
    with open('verdict.json', 'w') as f:
        json.dump(verdict, f)
