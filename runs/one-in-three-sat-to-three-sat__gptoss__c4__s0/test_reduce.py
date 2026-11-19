import random
import itertools
import json
import sys
from typing import List, Dict, Any

import problems
from reduce import reduce


def solve_one_in_three(instance: Dict[str, Any]) -> bool:
    m = instance["num_vars"]
    clauses: List[List[int]] = instance["clauses"]
    for bits in itertools.product([False, True], repeat=m):
        ok = True
        for clause in clauses:
            # clause vars are positive ints
            true_count = sum(bits[v-1] for v in clause)
            if true_count != 1:
                ok = False
                break
        if ok:
            return True
    return False


def solve_three_sat(instance: Dict[str, Any]) -> bool:
    m = instance["num_vars"]
    clauses: List[List[int]] = instance["clauses"]
    for bits in itertools.product([False, True], repeat=m):
        ok = True
        for clause in clauses:
            clause_ok = False
            for lit in clause:
                var = abs(lit) - 1
                val = bits[var]
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
    return False


def random_one_in_three_instance(max_vars=4, max_clauses=5) -> Dict[str, Any]:
    m = random.randint(0, max_vars)
    # ensure at least 3 vars if there are clauses
    num_clauses = random.randint(0, max_clauses)
    if num_clauses > 0 and m < 3:
        m = 3
    clauses = []
    for _ in range(num_clauses):
        # pick three distinct vars from 1..m
        vars = random.sample(range(1, m+1), 3)
        random.shuffle(vars)
        clauses.append(vars)
    return {"num_vars": m, "clauses": clauses}


def random_three_sat_instance_from_one_in_three(src: Dict[str, Any]) -> Dict[str, Any]:
    # just use the reduction to get a target instance
    return reduce(src)


def run_tests(num_tests=200):
    passed = 0
    for _ in range(num_tests):
        src = random_one_in_three_instance()
        # validate source
        problems.OneInThreeSat.validate(src)
        tgt = reduce(src)
        problems.ThreeSat.validate(tgt)
        src_ans = solve_one_in_three(src)
        tgt_ans = solve_three_sat(tgt)
        if src_ans == tgt_ans:
            passed += 1
        else:
            print("Mismatch!", src, tgt, src_ans, tgt_ans)
            return False, passed
    return True, passed

if __name__ == "__main__":
    ok, count = run_tests()
    verdict = {
        "verified": ok,
        "tests_run": 200,
        "tests_passed": count,
    }
    with open("verdict.json", "w") as f:
        json.dump(verdict, f)
    print(json.dumps(verdict))
    sys.exit(0 if ok else 1)
