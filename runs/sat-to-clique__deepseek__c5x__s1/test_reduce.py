import random
import itertools
import json
import sys
from pathlib import Path

# Import the problem definitions and reduction
import problems
from reduce import reduce as reduce_sat_to_clique

# Import our brute-force solvers
from sat_solver import sat_satisfiable
from clique_solver import clique_has_at_least_k


def generate_random_sat(max_vars=3, max_clauses=3, max_lits=3):
    num_vars = random.randint(0, max_vars)
    clauses = []
    for _ in range(random.randint(0, max_clauses)):
        clause_len = random.randint(0, max_lits)
        clause = []
        for _ in range(clause_len):
            if num_vars == 0:
                # no variables, skip adding literals
                continue
            var = random.randint(1, num_vars)
            lit = var if random.choice([True, False]) else -var
            clause.append(lit)
        clauses.append(clause)
    return {"num_vars": num_vars, "clauses": clauses}


def run_test(num_trials=500):
    passed = 0
    for i in range(num_trials):
        instance = generate_random_sat()
        # Validate source instance
        try:
            problems.Sat.validate(instance)
        except Exception as e:
            print(f"Invalid SAT instance generated: {e}", file=sys.stderr)
            continue
        # Compute answers
        sat_ans = sat_satisfiable(instance)
        # Reduce
        reduced = reduce_sat_to_clique(instance)
        # Validate target instance
        try:
            problems.Clique.validate(reduced)
        except Exception as e:
            print(f"Reduction produced invalid Clique instance: {e}", file=sys.stderr)
            return passed, i
        clique_ans = clique_has_at_least_k(reduced)
        if sat_ans == clique_ans:
            passed += 1
        else:
            print("Mismatch!", json.dumps({"sat": instance, "reduced": reduced, "sat_ans": sat_ans, "clique_ans": clique_ans}), file=sys.stderr)
            break
    return passed, num_trials

if __name__ == "__main__":
    passed, total = run_test()
    print(json.dumps({"tests_run": total, "tests_passed": passed, "verified": passed == total}))
