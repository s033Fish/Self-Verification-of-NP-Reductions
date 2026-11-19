import random
import json
from typing import List, Dict, Any

from problems import ThreeSat, SubsetSum
from reduce import reduce


def solve_three_sat(instance: Dict[str, Any]) -> bool:
    m = instance["num_vars"]
    clauses = instance["clauses"]
    if not clauses:
        return True
    for mask in range(1 << m):
        ok = True
        for clause in clauses:
            clause_ok = False
            for lit in clause:
                var = abs(lit) - 1
                val = (mask >> var) & 1
                if lit > 0 and val == 1:
                    clause_ok = True
                    break
                if lit < 0 and val == 0:
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
    # simple DP using set of reachable sums (since numbers non-negative)
    reachable = {0}
    for num in numbers:
        new = set()
        for s in reachable:
            new.add(s + num)
        reachable.update(new)
    return target in reachable


def random_three_sat(max_vars: int = 4, max_clauses: int = 5) -> Dict[str, Any]:
    m = random.randint(0, max_vars)
    # Ensure if there are clauses then m>=3 per spec, but we can still generate
    # with smaller m; validation will accept as long as literals within range.
    # To keep valid, if m < 3 and we want clauses, set m=3.
    if random.random() < 0.7:
        # generate some clauses
        if m < 3:
            m = 3
        num_clauses = random.randint(1, max_clauses)
        clauses = []
        for _ in range(num_clauses):
            vars = random.sample(range(1, m+1), 3)
            clause = []
            for v in vars:
                lit = v if random.choice([True, False]) else -v
                clause.append(lit)
            clauses.append(clause)
    else:
        clauses = []
    return {"num_vars": m, "clauses": clauses}


def main():
    tests = 100
    passed = 0
    for i in range(tests):
        inst = random_three_sat()
        # validate source
        ThreeSat.validate(inst)
        sat = solve_three_sat(inst)
        red = reduce(inst)
        SubsetSum.validate(red)
        ss = solve_subset_sum(red)
        if sat == ss:
            passed += 1
        else:
            print("FAIL", i, inst, sat, red, ss)
            break
    # Edge cases
    edge_cases = [
        {"num_vars": 0, "clauses": []},
        {"num_vars": 3, "clauses": []},
        {"num_vars": 3, "clauses": [[1,2,3]]},
        {"num_vars": 3, "clauses": [[1,2,3], [-1,-2,-3]]},
    ]
    for ec in edge_cases:
        ThreeSat.validate(ec)
        sat = solve_three_sat(ec)
        red = reduce(ec)
        SubsetSum.validate(red)
        ss = solve_subset_sum(red)
        if sat == ss:
            passed += 1
        else:
            print("EDGE FAIL", ec, sat, red, ss)
            break
    total = tests + len(edge_cases)
    result = {"verified": passed == total, "tests_run": total, "tests_passed": passed}
    print(json.dumps(result))
    with open("verdict.json", "w") as f:
        json.dump(result, f)

if __name__ == "__main__":
    main()
