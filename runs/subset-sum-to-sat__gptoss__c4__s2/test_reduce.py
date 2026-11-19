import itertools
import json
import random
import sys
from problems import SubsetSum, Sat
import reduce

def subset_sum_bruteforce(numbers, target):
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

def sat_bruteforce(num_vars, clauses):
    # empty clause -> unsat
    for clause in clauses:
        if len(clause) == 0:
            return False
    # try all assignments
    for bits in range(1 << num_vars):
        assignment = [(bits >> i) & 1 == 1 for i in range(num_vars)]  # var i+1
        ok = True
        for clause in clauses:
            clause_ok = False
            for lit in clause:
                var = abs(lit) - 1
                sign = lit > 0
                if assignment[var] == sign:
                    clause_ok = True
                    break
            if not clause_ok:
                ok = False
                break
        if ok:
            return True
    return False

def generate_instances():
    instances = []
    # small numbers
    for length in range(0, 5):
        for numbers in itertools.product(range(0, 5), repeat=length):
            for target in range(-2, 11):
                instances.append({"numbers": list(numbers), "target": target})
    return instances

def main():
    instances = generate_instances()
    total = len(instances)
    passed = 0
    for inst in instances:
        # validate source
        SubsetSum.validate(inst)
        expected = subset_sum_bruteforce(inst["numbers"], inst["target"])
        reduced = reduce.reduce(inst)
        Sat.validate(reduced)
        got = sat_bruteforce(reduced["num_vars"], reduced["clauses"])
        if expected == got:
            passed += 1
        else:
            print("FAIL", inst, "expected", expected, "got", got, "reduced", reduced)
            sys.exit(1)
    print(f"All {passed}/{total} tests passed.")
    # write verdict
    verdict = {"verified": True, "tests_run": total, "tests_passed": passed}
    with open('verdict.json', 'w') as f:
        json.dump(verdict, f)

if __name__ == '__main__':
    main()
