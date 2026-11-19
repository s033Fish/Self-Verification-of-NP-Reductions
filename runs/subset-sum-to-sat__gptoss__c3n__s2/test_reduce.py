import random
import json
from typing import List, Dict

from problems import SubsetSum, Sat
from reduce import reduce


def subset_sum_bruteforce(numbers: List[int], target: int) -> bool:
    n = len(numbers)
    # iterate over all subsets
    for mask in range(1 << n):
        s = 0
        for i in range(n):
            if mask & (1 << i):
                s += numbers[i]
        if s == target:
            return True
    # empty subset case handled automatically
    return target == 0


def sat_bruteforce(instance: Dict) -> bool:
    m = instance["num_vars"]
    clauses = instance["clauses"]
    # If any clause is empty, unsatisfiable
    for clause in clauses:
        if len(clause) == 0:
            return False
    # iterate over all assignments
    for mask in range(1 << m):
        assignment = [(mask >> i) & 1 == 1 for i in range(m)]  # variable i+1
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
    # also handle case with no variables (m=0)
    if m == 0:
        return True
    return False


def run_tests(num_tests: int = 200) -> Dict:
    passed = 0
    for _ in range(num_tests):
        # generate random instance
        length = random.randint(0, 6)
        numbers = [random.randint(0, 10) for _ in range(length)]
        target = random.randint(-5, 20)
        ss_instance = {"numbers": numbers, "target": target}
        # validate
        SubsetSum.validate(ss_instance)
        # compute answers
        ss_yes = subset_sum_bruteforce(numbers, target)
        sat_instance = reduce(ss_instance)
        Sat.validate(sat_instance)
        sat_yes = sat_bruteforce(sat_instance)
        if ss_yes == sat_yes:
            passed += 1
        else:
            print("Mismatch!", ss_instance, ss_yes, sat_instance, sat_yes)
            break
    return {"tests_run": num_tests, "tests_passed": passed}

if __name__ == "__main__":
    result = run_tests()
    verified = result["tests_passed"] == result["tests_run"]
    verdict = {"verified": verified, "tests_run": result["tests_run"], "tests_passed": result["tests_passed"]}
    print(json.dumps(verdict))
    with open("verdict.json", "w") as f:
        json.dump(verdict, f)
