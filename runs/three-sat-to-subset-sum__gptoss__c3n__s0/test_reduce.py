import random
import itertools
import json
from typing import List, Dict, Any

from problems import ThreeSat, SubsetSum
from reduce import reduce


def solve_three_sat(instance: Dict[str, Any]) -> bool:
    m = instance["num_vars"]
    clauses = instance["clauses"]
    for mask in range(1 << m):
        assignment = [(mask >> i) & 1 == 1 for i in range(m)]
        ok = True
        for clause in clauses:
            clause_ok = False
            for lit in clause:
                var = abs(lit) - 1
                val = assignment[var]
                if (lit > 0 and val) or (lit < 0 and not val):
                    clause_ok = True
                    break
            if not clause_ok:
                ok = False
                break
        if ok:
            return True
    return False


def solve_subset_sum(instance: Dict[str, Any]) -> bool:
    numbers = instance["numbers"]
    target = instance["target"]
    n = len(numbers)
    # simple subset enumeration
    for r in range(n + 1):
        for combo in itertools.combinations(range(n), r):
            s = sum(numbers[i] for i in combo)
            if s == target:
                return True
    return False


def random_three_sat(max_vars=4, max_clauses=5) -> Dict[str, Any]:
    m = random.randint(0, max_vars)
    # ensure at least 3 vars if there are clauses
    if m < 3:
        # allow zero clauses case
        clauses = []
        return {"num_vars": m, "clauses": clauses}
    num_clauses = random.randint(0, max_clauses)
    clauses = []
    for _ in range(num_clauses):
        # pick 3 distinct variables
        vars = random.sample(range(1, m + 1), 3)
        clause = []
        for v in vars:
            lit = v if random.choice([True, False]) else -v
            clause.append(lit)
        clauses.append(clause)
    return {"num_vars": m, "clauses": clauses}


def main():
    random.seed(0)
    tests = 200
    passed = 0
    for i in range(tests):
        inst = random_three_sat()
        # validate input
        ThreeSat.validate(inst)
        reduced = reduce(inst)
        SubsetSum.validate(reduced)
        sat = solve_three_sat(inst)
        ss = solve_subset_sum(reduced)
        if sat == ss:
            passed += 1
        else:
            print("Mismatch on instance", i, inst, "reduced", reduced, sat, ss)
            break
    result = {"verified": passed == tests, "tests_run": tests, "tests_passed": passed}
    with open('verdict.json', 'w') as f:
        json.dump(result, f)
    print(json.dumps(result))

if __name__ == '__main__':
    main()
