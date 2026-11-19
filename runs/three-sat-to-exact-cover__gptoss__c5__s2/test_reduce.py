import json
import random
import sys

from problems import ThreeSat, ExactCover
import reduce
from three_sat_solver import solve_three_sat
from exact_cover_solver import solve_exact_cover


def random_three_sat(max_vars=4, max_clauses=5):
    m = random.randint(0, max_vars)
    # Ensure if there are clauses, m >= 3 as per edge case requirement.
    if m < 3:
        # we may still generate clauses with fewer vars? but spec says formula with clauses needs m>=3.
        # To keep valid instances, if we decide to have clauses, set m >=3.
        have_clauses = random.choice([True, False])
        if have_clauses:
            m = random.randint(3, max_vars)
    num_clauses = random.randint(0, max_clauses)
    clauses = []
    for _ in range(num_clauses):
        # pick 3 distinct variables from 1..m
        if m == 0:
            # cannot have clause, break
            break
        vars = random.sample(range(1, m + 1), 3) if m >= 3 else []
        if not vars:
            continue
        clause = []
        for v in vars:
            lit = v if random.choice([True, False]) else -v
            clause.append(lit)
        clauses.append(clause)
    return {"num_vars": m, "clauses": clauses}


def main():
    total = 200
    passed = 0
    for i in range(total):
        inst = random_three_sat()
        # Validate source
        try:
            ThreeSat.validate(inst)
        except Exception as e:
            print(f"Invalid generated instance: {e}", file=sys.stderr)
            continue
        sat_three = solve_three_sat(inst)
        reduced = reduce.reduce(inst)
        # Validate target
        ExactCover.validate(reduced)
        sat_exact = solve_exact_cover(reduced)
        if sat_three == sat_exact:
            passed += 1
        else:
            print("Mismatch on instance", inst, "reduced", reduced, file=sys.stderr)
    verdict = {
        "verified": passed == total,
        "tests_run": total,
        "tests_passed": passed,
    }
    with open('verdict.json', 'w') as f:
        json.dump(verdict, f, indent=2)
    print(json.dumps(verdict, indent=2))

if __name__ == '__main__':
    main()
