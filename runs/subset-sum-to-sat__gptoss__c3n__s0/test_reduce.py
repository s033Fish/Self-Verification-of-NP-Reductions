import random
import sys
import json
from typing import List, Dict, Any

from problems import SubsetSum, Sat
import reduce


def subset_sum_bruteforce(instance: Dict[str, Any]) -> bool:
    numbers = instance["numbers"]
    target = instance["target"]
    # Edge cases
    if target == 0:
        return True
    if target < 0:
        return False
    n = len(numbers)
    for mask in range(1 << n):
        s = 0
        for i in range(n):
            if mask & (1 << i):
                s += numbers[i]
        if s == target:
            return True
    return False


def sat_bruteforce(instance: Dict[str, Any]) -> bool:
    m = instance["num_vars"]
    clauses = instance["clauses"]
    # Empty clause makes formula unsatisfiable
    for mask in range(1 << m):
        assignment = [(mask >> i) & 1 == 1 for i in range(m)]  # var i+1
        ok = True
        for clause in clauses:
            clause_ok = False
            for lit in clause:
                var = abs(lit) - 1
                val = assignment[var]
                if lit > 0 and val:
                    clause_ok = True
                    break
                if lit < 0 and not val:
                    clause_ok = True
                    break
            if not clause_ok:
                ok = False
                break
        if ok:
            return True
    return False


def run_tests(num_tests: int = 200) -> None:
    passed = 0
    for _ in range(num_tests):
        # generate random SubsetSum instance
        n = random.randint(0, 5)
        numbers = [random.randint(0, 10) for _ in range(n)]
        target = random.randint(-5, 20)
        instance = {"numbers": numbers, "target": target}
        # validate
        SubsetSum.validate(instance)
        # compute answers
        ans_src = subset_sum_bruteforce(instance)
        red = reduce.reduce(instance)
        Sat.validate(red)
        ans_tgt = sat_bruteforce(red)
        if ans_src == ans_tgt:
            passed += 1
        else:
            print("Mismatch!", instance, ans_src, red, ans_tgt, file=sys.stderr)
            break
    print(json.dumps({"tests_run": num_tests, "tests_passed": passed, "verified": passed == num_tests}))

if __name__ == "__main__":
    run_tests()
