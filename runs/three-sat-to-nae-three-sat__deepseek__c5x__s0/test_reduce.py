import random
import sys
import json
from pathlib import Path

# Import problem definitions and reduction
import problems
import reduce

# Import our brute-force solvers
from solver_three_sat import solve_three_sat
from solver_nae_three_sat import solve_nae_three_sat


def generate_random_three_sat(max_vars=5, max_clauses=5):
    num_vars = random.randint(0, max_vars)
    # ensure if clauses >0 then num_vars >=3 per spec, but we can still generate with fewer vars; validation will allow? The problem spec says need m>=3 if clauses exist, but validation does not enforce that. We'll respect spec.
    if num_vars < 3:
        # allow only zero clauses
        clauses = []
    else:
        clauses = []
        for _ in range(random.randint(0, max_clauses)):
            # pick 3 distinct vars
            vars_ = random.sample(range(1, num_vars + 1), 3)
            # assign random signs
            clause = [v if random.choice([True, False]) else -v for v in vars_]
            clauses.append(clause)
    return {"num_vars": num_vars, "clauses": clauses}


def run_test(instance):
    # Validate source
    problems.ThreeSat.validate(instance)
    # Solve source
    src_ans = solve_three_sat(instance)
    # Reduce
    reduced = reduce.reduce(instance)
    # Validate target
    problems.NaeThreeSat.validate(reduced)
    # Solve target
    tgt_ans = solve_nae_three_sat(reduced)
    return src_ans == tgt_ans


def main():
    random.seed(0)
    total = 0
    passed = 0
    for _ in range(200):
        inst = generate_random_three_sat()
        total += 1
        try:
            if run_test(inst):
                passed += 1
        except Exception as e:
            print("Error on instance", inst, file=sys.stderr)
            raise
    # also test some edge cases explicitly
    edge_cases = [
        {"num_vars": 0, "clauses": []},
        {"num_vars": 3, "clauses": []},
    ]
    for inst in edge_cases:
        total += 1
        if run_test(inst):
            passed += 1
    verdict = {"verified": passed == total, "tests_run": total, "tests_passed": passed}
    Path("verdict.json").write_text(json.dumps(verdict))
    print(json.dumps(verdict))

if __name__ == "__main__":
    main()
