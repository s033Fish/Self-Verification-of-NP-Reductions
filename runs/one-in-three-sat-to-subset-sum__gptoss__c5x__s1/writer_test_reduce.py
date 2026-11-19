import random
import itertools
import json
from problems import OneInThreeSat, SubsetSum
from reduce import reduce


def solve_one_in_three_sat(instance):
    m = instance["num_vars"]
    clauses = instance["clauses"]
    # Edge case: no clauses -> yes
    if not clauses:
        return True
    for assignment in itertools.product([False, True], repeat=m):
        ok = True
        for clause in clauses:
            true_count = sum(assignment[var-1] for var in clause)
            if true_count != 1:
                ok = False
                break
        if ok:
            return True
    return False


def solve_subset_sum(instance):
    numbers = instance["numbers"]
    target = instance["target"]
    if target == 0:
        return True
    if target < 0:
        return False
    n = len(numbers)
    # simple DP subset sum for non-negative numbers
    reachable = {0}
    for num in numbers:
        new = set()
        for s in reachable:
            ns = s + num
            if ns == target:
                return True
            if ns < target:
                new.add(ns)
        reachable.update(new)
    return target in reachable


def random_instance(max_vars=4, max_clauses=4):
    m = random.randint(0, max_vars)
    # ensure at least 0 vars allowed
    num_clauses = random.randint(0, max_clauses)
    clauses = []
    for _ in range(num_clauses):
        if m < 3:
            # cannot create clause, break
            break
        vars_in_clause = random.sample(range(1, m+1), 3)
        clauses.append(vars_in_clause)
    return {"num_vars": m, "clauses": clauses}


def run_tests(num_tests=200):
    passed = 0
    for _ in range(num_tests):
        src = random_instance()
        # validate source
        try:
            OneInThreeSat.validate(src)
        except Exception as e:
            # skip invalid generated instances (e.g., m<3 but clauses exist)
            continue
        tgt = reduce(src)
        # validate target
        SubsetSum.validate(tgt)
        src_ans = solve_one_in_three_sat(src)
        tgt_ans = solve_subset_sum(tgt)
        if src_ans == tgt_ans:
            passed += 1
        else:
            print("Mismatch!", src, tgt, src_ans, tgt_ans)
            return False, passed
    return True, passed

if __name__ == "__main__":
    ok, passed = run_tests(500)
    result = {"verified": ok, "tests_run": 500, "tests_passed": passed}
    with open("verdict.json", "w") as f:
        json.dump(result, f)
    print(json.dumps(result))
