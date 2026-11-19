import random
from typing import List, Dict, Any

from problems import ThreeSat, SubsetSum
from reduce import reduce


def solve_three_sat(instance: Dict[str, Any]) -> bool:
    m = instance["num_vars"]
    clauses: List[List[int]] = instance["clauses"]
    for mask in range(1 << m):
        ok = True
        for clause in clauses:
            clause_sat = False
            for lit in clause:
                var = abs(lit) - 1
                val = (mask >> var) & 1
                if (lit > 0 and val == 1) or (lit < 0 and val == 0):
                    clause_sat = True
                    break
            if not clause_sat:
                ok = False
                break
        if ok:
            return True
    return False


def solve_subset_sum(instance: Dict[str, Any]) -> bool:
    numbers: List[int] = instance["numbers"]
    target: int = instance["target"]
    n = len(numbers)
    # simple DP for non-negative numbers
    if target < 0:
        return False
    dp = {0}
    for num in numbers:
        new_dp = set(dp)
        for s in dp:
            new_dp.add(s + num)
        dp = new_dp
    return target in dp


def random_three_sat(max_vars=4, max_clauses=5) -> Dict[str, Any]:
    m = random.randint(0, max_vars)
    if m < 3:
        # allow zero clauses only
        return {"num_vars": m, "clauses": []}
    num_clauses = random.randint(0, max_clauses)
    clauses = []
    for _ in range(num_clauses):
        vars_in_clause = random.sample(range(1, m+1), 3)
        clause = []
        for v in vars_in_clause:
            lit = v if random.choice([True, False]) else -v
            clause.append(lit)
        clauses.append(clause)
    return {"num_vars": m, "clauses": clauses}


def main():
    tests = 0
    passed = 0
    for _ in range(200):
        inst = random_three_sat()
        # validate
        ThreeSat.validate(inst)
        src_ans = solve_three_sat(inst)
        red_inst = reduce(inst)
        SubsetSum.validate(red_inst)
        tgt_ans = solve_subset_sum(red_inst)
        tests += 1
        if src_ans == tgt_ans:
            passed += 1
        else:
            print("Mismatch!", inst, src_ans, red_inst, tgt_ans)
    print(tests, passed)
    # write verdict
    import json
    verdict = {"verified": passed == tests, "tests_run": tests, "tests_passed": passed}
    with open('verdict.json', 'w') as f:
        json.dump(verdict, f)

if __name__ == "__main__":
    main()
