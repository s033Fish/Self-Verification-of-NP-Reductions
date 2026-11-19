import random
from typing import List, Dict, Any

from problems import ThreeSat, OneInThreeSat
from reduce import reduce, solve_three_sat, solve_one_in_three_sat


def random_three_sat_instance(max_vars: int = 4, max_clauses: int = 5) -> Dict[str, Any]:
    m = random.randint(0, max_vars)  # allow zero vars for edge case
    # ensure if there are clauses then m>=3
    if m < 3:
        # either no clauses or set m to 3
        if random.random() < 0.5:
            return {"num_vars": m, "clauses": []}
        else:
            m = 3
    clauses: List[List[int]] = []
    num_clauses = random.randint(0, max_clauses)
    vars_range = list(range(1, m + 1))
    for _ in range(num_clauses):
        # pick 3 distinct vars
        vars_selected = random.sample(vars_range, 3)
        clause = []
        for v in vars_selected:
            lit = v if random.choice([True, False]) else -v
            clause.append(lit)
        clauses.append(clause)
    return {"num_vars": m, "clauses": clauses}


def test_random_instances(num_tests: int = 200):
    passed = 0
    for i in range(num_tests):
        inst = random_three_sat_instance()
        # validate
        ThreeSat.validate(inst)
        # compute answers
        ans_src = solve_three_sat(inst)
        red = reduce(inst)
        # validate target instance
        OneInThreeSat.validate(red)
        ans_tgt = solve_one_in_three_sat(red)
        if ans_src == ans_tgt:
            passed += 1
        else:
            print("Mismatch on instance", inst)
            print("Reduced to", red)
            print("src", ans_src, "tgt", ans_tgt)
            break
    return passed, num_tests

if __name__ == "__main__":
    passed, total = test_random_instances(200)
    print(f"Passed {passed}/{total} tests")
