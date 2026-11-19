import random
import json
import sys
from typing import Dict, List
from problems import ThreeSat, DominatingSet
from solve_bruteforce import solve_three_sat, solve_dominating_set
from reduce import reduce

def random_three_sat(max_vars=4, max_clauses=5) -> Dict:
    m = random.randint(0, max_vars)
    # ensure if clauses >0 then m>=3
    num_clauses = random.randint(0, max_clauses)
    if num_clauses > 0 and m < 3:
        m = random.randint(3, max_vars)
    clauses: List[List[int]] = []
    for _ in range(num_clauses):
        # pick 3 distinct vars from 1..m
        vars = random.sample(range(1, m+1), 3) if m >=3 else []
        clause = []
        for v in vars:
            lit = v if random.choice([True, False]) else -v
            clause.append(lit)
        clauses.append(clause)
    return {"num_vars": m, "clauses": clauses}


def main():
    random.seed(0)
    total = 0
    passed = 0
    for _ in range(200):
        instance = random_three_sat()
        try:
            ThreeSat.validate(instance)
        except Exception as e:
            print("Invalid generated instance", e)
            continue
        three_sat_ans = solve_three_sat(instance)
        dom_instance = reduce(instance)
        DominatingSet.validate(dom_instance)
        dom_ans = solve_dominating_set(dom_instance)
        total += 1
        if three_sat_ans == dom_ans:
            passed += 1
        else:
            print("Mismatch!", instance, three_sat_ans, dom_ans)
            sys.exit(1)
    print(f"All {passed}/{total} tests passed")
    # write verdict
    verdict = {"verified": True, "tests_run": total, "tests_passed": passed}
    with open('verdict.json', 'w') as f:
        json.dump(verdict, f)

if __name__ == '__main__':
    main()
