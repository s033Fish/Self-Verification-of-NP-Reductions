import json
import random
import sys
from pathlib import Path

# Import the modules from the repository
sys.path.append(str(Path('.').resolve()))
from problems import OneInThreeSat, ThreeSat
from reduce import reduce as reduce_instance
from solver import solve_one_in_three_sat, solve_three_sat


def generate_random_instance(max_vars=4, max_clauses=3):
    """Generate a *valid* OneInThreeSat instance.

    The function ensures the instance conforms to the validation rules so
    that the test harness does not need to skip invalid cases.
    """
    # Choose number of variables; allow 0.
    m = random.randint(0, max_vars)
    # If we want to generate clauses we need at least 3 variables.
    if m < 3:
        # With probability 0.7 we produce an empty‑clause instance (always valid).
        if random.random() < 0.7:
            return {"num_vars": m, "clauses": []}
        else:
            m = 3
    num_clauses = random.randint(0, max_clauses)
    clauses = []
    for _ in range(num_clauses):
        clause = random.sample(range(1, m + 1), 3)
        clauses.append(clause)
    return {"num_vars": m, "clauses": clauses}


def main():
    random.seed(0)
    total = 0
    passed = 0
    failures = []

    # Explicit edge‑case instances.
    edge_cases = [
        {"num_vars": 0, "clauses": []},  # no variables, no clauses
        {"num_vars": 3, "clauses": []},  # variables but empty formula
        {"num_vars": 3, "clauses": [[1, 2, 3]]},  # single clause
        {"num_vars": 4, "clauses": [[1, 2, 3], [2, 3, 4]]},
    ]

    for src in edge_cases + [generate_random_instance() for _ in range(200)]:
        total += 1
        # Validation should succeed for all generated instances.
        OneInThreeSat.validate(src)
        tgt = reduce_instance(src)
        ThreeSat.validate(tgt)
        src_ans = solve_one_in_three_sat(src)
        tgt_ans = solve_three_sat(tgt)
        if src_ans == tgt_ans:
            passed += 1
        else:
            failures.append((src, src_ans, tgt_ans))

    verdict = {
        "verified": passed == total,
        "tests_run": total,
        "tests_passed": passed,
    }
    print(json.dumps(verdict, indent=2))
    Path('verdict.json').write_text(json.dumps(verdict))
    if failures:
        print("Failures:")
        for f in failures[:5]:
            print(f)
        sys.exit(1)

if __name__ == "__main__":
    main()
