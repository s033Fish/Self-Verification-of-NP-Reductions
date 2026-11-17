import random
import json
from typing import List, Dict, Any

from reduce import reduce
from solve_three_sat import solve as solve_three_sat
from solve_exact_cover import solve as solve_exact_cover


def generate_instance(num_vars: int, num_clauses: int) -> Dict[str, Any]:
    clauses: List[List[int]] = []
    vars_list = list(range(1, num_vars + 1))
    for _ in range(num_clauses):
        # pick 3 distinct variables
        vars_in_clause = random.sample(vars_list, 3)
        clause = []
        for v in vars_in_clause:
            lit = v if random.choice([True, False]) else -v
            clause.append(lit)
        clauses.append(clause)
    return {"num_vars": num_vars, "clauses": clauses}


def run_tests(num_trials: int = 200) -> Dict[str, Any]:
    """Run a number of random tests and report how many were executed and passed.

    The original implementation counted *num_trials* as the number of tests
    run, even when a generated instance was skipped because it violated the
    pre‑condition that a clause needs at least three distinct variables.  This
    caused the ``verified`` flag to be ``false`` despite all *actually executed*
    tests succeeding.  The function now counts only the instances that are
    processed.
    """
    passed = 0
    executed = 0
    for _ in range(num_trials):
        # random size
        num_vars = random.randint(0, 4)
        # decide number of clauses
        if num_vars == 0:
            num_clauses = 0
        else:
            num_clauses = random.randint(0, 5)
            if num_clauses > 0 and num_vars < 3:
                # need at least 3 vars for clauses; skip this trial
                continue
        instance = generate_instance(num_vars, num_clauses)
        executed += 1
        # solve original
        ans_three = solve_three_sat(instance)
        # reduce
        red = reduce(instance)
        # solve reduced
        ans_exact = solve_exact_cover(red)
        if ans_three == ans_exact:
            passed += 1
        else:
            print("Mismatch!", instance, red, ans_three, ans_exact)
            break
    return {"tests_run": executed, "tests_passed": passed}

if __name__ == "__main__":
    result = run_tests(200)
    verified = result["tests_passed"] == result["tests_run"]
    verdict = {"verified": verified, "tests_run": result["tests_run"], "tests_passed": result["tests_passed"]}
    with open("verdict.json", "w") as f:
        json.dump(verdict, f)
    print(json.dumps(verdict, indent=2))
