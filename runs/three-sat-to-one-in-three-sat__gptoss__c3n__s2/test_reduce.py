import random
import itertools
import json
from reduce import reduce, _solve_three_sat, _solve_one_in_three_sat

def random_three_sat_instance(num_vars, num_clauses):
    clauses = []
    vars_list = list(range(1, num_vars + 1))
    for _ in range(num_clauses):
        # pick 3 distinct vars
        vars_in_clause = random.sample(vars_list, 3)
        clause = []
        for v in vars_in_clause:
            lit = v if random.choice([True, False]) else -v
            clause.append(lit)
        # ensure not both v and -v (already distinct vars) and length 3
        clauses.append(clause)
    return {"num_vars": num_vars, "clauses": clauses}


def run_tests(num_trials=200):
    passed = 0
    for _ in range(num_trials):
        m = random.randint(0, 4)  # allow 0 vars
        # ensure if clauses exist, m>=3 per spec, else skip
        max_clauses = 5
        c = random.randint(0, max_clauses)
        if c > 0 and m < 3:
            m = 3
        instance = random_three_sat_instance(m, c)
        # compute answers
        three_ans = _solve_three_sat(instance)
        red = reduce(instance)
        one_ans = _solve_one_in_three_sat(red)
        if three_ans == one_ans:
            passed += 1
        else:
            print("FAIL", instance, three_ans, red, one_ans)
            break
    return passed, num_trials

if __name__ == "__main__":
    passed, total = run_tests()
    result = {"verified": passed == total, "tests_run": total, "tests_passed": passed}
    print(json.dumps(result))
    with open("verdict.json", "w") as f:
        json.dump(result, f)
