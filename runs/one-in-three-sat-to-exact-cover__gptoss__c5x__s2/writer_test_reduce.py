import itertools
import random
import json
from typing import List, Dict, Any

import problems
from reduce import reduce


def solve_one_in_three_sat(instance: Dict[str, Any]) -> bool:
    problems.OneInThreeSat.validate(instance)
    m = instance["num_vars"]
    clauses = instance["clauses"]
    for assign in range(1 << m):
        ok = True
        for clause in clauses:
            true_cnt = 0
            for var in clause:
                if (assign >> (var - 1)) & 1:
                    true_cnt += 1
            if true_cnt != 1:
                ok = False
                break
        if ok:
            return True
    return False


def solve_exact_cover(instance: Dict[str, Any]) -> bool:
    problems.ExactCover.validate(instance)
    u = instance["universe_size"]
    sets = instance["sets"]
    n = len(sets)
    # enumerate all subsets of sets (2^n), but limit for small n
    for mask in range(1 << n):
        covered = [0] * u
        ok = True
        for i in range(n):
            if (mask >> i) & 1:
                for e in sets[i]:
                    covered[e] += 1
                    if covered[e] > 1:
                        ok = False
                        break
                if not ok:
                    break
        if not ok:
            continue
        if all(c == 1 for c in covered):
            return True
    return False


def random_one_in_three_instance(max_vars=4, max_clauses=4) -> Dict[str, Any]:
    m = random.randint(0, max_vars)
    # ensure at least 3 vars if there are clauses
    num_clauses = random.randint(0, max_clauses)
    if num_clauses > 0 and m < 3:
        m = 3
    clauses = []
    for _ in range(num_clauses):
        vars_in_clause = random.sample(range(1, m + 1), 3)
        clauses.append(vars_in_clause)
    return {"num_vars": m, "clauses": clauses}


def run_tests(num_tests=200):
    passed = 0
    for _ in range(num_tests):
        src = random_one_in_three_instance()
        tgt = reduce(src)
        src_ans = solve_one_in_three_sat(src)
        tgt_ans = solve_exact_cover(tgt)
        if src_ans == tgt_ans:
            passed += 1
        else:
            print("FAIL")
            print("src", src)
            print("tgt", tgt)
            print(src_ans, tgt_ans)
            break
    return passed, num_tests

if __name__ == "__main__":
    passed, total = run_tests()
    verdict = {"verified": passed == total, "tests_run": total, "tests_passed": passed}
    print(json.dumps(verdict))
    with open("verdict.json", "w") as f:
        json.dump(verdict, f)
