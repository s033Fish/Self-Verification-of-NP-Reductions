import itertools
import random
import json
import sys
from typing import List, Dict

from problems import OneInThreeSat, SubsetSum
from reduce import reduce


def solve_one_in_three_sat(instance: Dict) -> bool:
    m = instance["num_vars"]
    clauses = instance["clauses"]
    # iterate all assignments
    for bits in itertools.product([0, 1], repeat=m):
        ok = True
        for clause in clauses:
            true_count = sum(bits[var-1] for var in clause)
            if true_count != 1:
                ok = False
                break
        if ok:
            return True
    return False


def solve_subset_sum(instance: Dict) -> bool:
    numbers = instance["numbers"]
    target = instance["target"]
    if target < 0:
        return False
    if target == 0:
        return True
    n = len(numbers)
    # simple DP using set of reachable sums
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


def random_instance(max_vars=5, max_clauses=5) -> Dict:
    m = random.randint(0, max_vars)
    # ensure m>=3 if we add clauses
    num_clauses = random.randint(0, max_clauses)
    clauses = []
    for _ in range(num_clauses):
        if m < 3:
            # generate dummy variables, will be caught by validator later
            clause = []
        else:
            clause = random.sample(range(1, m+1), 3)
        clauses.append(clause)
    return {"num_vars": m, "clauses": clauses}


def run_tests(num_tests=200):
    passed = 0
    for _ in range(num_tests):
        inst = random_instance()
        # validate source (skip invalid ones)
        try:
            OneInThreeSat.validate(inst)
        except Exception:
            continue
        src_ans = solve_one_in_three_sat(inst)
        red = reduce(inst)
        SubsetSum.validate(red)
        tgt_ans = solve_subset_sum(red)
        if src_ans == tgt_ans:
            passed += 1
        else:
            print('Mismatch!')
            print('source', inst)
            print('reduced', red)
            print('src_ans', src_ans, 'tgt_ans', tgt_ans)
            return passed, False
    return passed, True

if __name__ == '__main__':
    passed, ok = run_tests()
    total = passed
    result = {"verified": ok, "tests_run": total, "tests_passed": total if ok else passed}
    print(json.dumps(result))
    sys.exit(0 if ok else 1)
