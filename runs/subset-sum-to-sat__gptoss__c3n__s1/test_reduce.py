import random
import json
import sys
from itertools import product

from problems import SubsetSum, Sat
from reduce import reduce as reduce_instance


def subset_sum_bruteforce(instance):
    numbers = instance["numbers"]
    target = instance["target"]
    n = len(numbers)
    # Edge cases handled by brute force as well
    for mask in range(1 << n):
        s = 0
        for i in range(n):
            if (mask >> i) & 1:
                s += numbers[i]
        if s == target:
            return True
    return False


def sat_bruteforce(instance):
    m = instance["num_vars"]
    clauses = instance["clauses"]
    # If any empty clause, unsat
    for clause in clauses:
        if len(clause) == 0:
            return False
    # Try all assignments
    for vals in product([False, True], repeat=m):
        ok = True
        for clause in clauses:
            clause_ok = False
            for lit in clause:
                var = abs(lit) - 1
                sign = lit > 0
                if vals[var] == sign:
                    clause_ok = True
                    break
            if not clause_ok:
                ok = False
                break
        if ok:
            return True
    return False


def run_tests(num_tests=200):
    passed = 0
    for _ in range(num_tests):
        n = random.randint(0, 5)
        numbers = [random.randint(0, 10) for _ in range(n)]
        target = random.randint(-5, 20)
        ss_instance = {"numbers": numbers, "target": target}
        # Validate
        SubsetSum.validate(ss_instance)
        # Reduce
        sat_instance = reduce_instance(ss_instance)
        Sat.validate(sat_instance)
        # Compare answers
        ss_ans = subset_sum_bruteforce(ss_instance)
        sat_ans = sat_bruteforce(sat_instance)
        if ss_ans == sat_ans:
            passed += 1
        else:
            print("Mismatch!", ss_instance, sat_instance, ss_ans, sat_ans, file=sys.stderr)
            return passed, False
    return passed, True

if __name__ == "__main__":
    total = 200
    passed, ok = run_tests(total)
    result = {"verified": ok, "tests_run": total, "tests_passed": passed}
    with open("verdict.json", "w") as f:
        json.dump(result, f)
    print(json.dumps(result))
    sys.exit(0 if ok else 1)
