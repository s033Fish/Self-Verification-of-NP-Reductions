import itertools
import json
import os
import random
from typing import List, Dict

from problems import ThreeSat, IndependentSet
from reduce import reduce


def three_sat_bruteforce(instance: Dict) -> bool:
    m = instance["num_vars"]
    clauses = instance["clauses"]
    # iterate over all assignments of m variables (True/False)
    for bits in itertools.product([False, True], repeat=m):
        ok = True
        for clause in clauses:
            satisfied = False
            for lit in clause:
                var = abs(lit) - 1
                val = bits[var]
                if lit > 0 and val:
                    satisfied = True
                if lit < 0 and not val:
                    satisfied = True
                if satisfied:
                    break
            if not satisfied:
                ok = False
                break
        if ok:
            return True
    return False


def independent_set_bruteforce(instance: Dict) -> bool:
    n = instance["n"]
    edges = set()
    for u, v in instance["edges"]:
        edges.add(frozenset((u, v)))
    k = instance["k"]
    # any subset of vertices of size >= k that is independent
    for size in range(k, n + 1):
        for subset in itertools.combinations(range(n), size):
            ok = True
            for u, v in itertools.combinations(subset, 2):
                if frozenset((u, v)) in edges:
                    ok = False
                    break
            if ok:
                return True
    return False


def random_three_sat(max_vars=4, max_clauses=5) -> Dict:
    m = random.randint(0, max_vars)
    # ensure at least 3 vars if there are clauses
    if m < 3:
        num_clauses = 0
    else:
        num_clauses = random.randint(0, max_clauses)
    clauses = []
    for _ in range(num_clauses):
        vars_used = random.sample(range(1, m + 1), 3)
        clause = []
        for v in vars_used:
            lit = v if random.choice([True, False]) else -v
            clause.append(lit)
        clauses.append(clause)
    return {"num_vars": m, "clauses": clauses}


def run_tests(num_tests=200):
    passed = 0
    for i in range(num_tests):
        src = random_three_sat()
        # validate source
        ThreeSat.validate(src)
        tgt = reduce(src)
        IndependentSet.validate(tgt)
        ans_src = three_sat_bruteforce(src)
        ans_tgt = independent_set_bruteforce(tgt)
        if ans_src == ans_tgt:
            passed += 1
        else:
            print("Mismatch!", src, tgt, ans_src, ans_tgt)
            break
    return passed, num_tests

if __name__ == "__main__":
    passed, total = run_tests()
    verdict = {
        "verified": passed == total,
        "tests_run": total,
        "tests_passed": passed,
    }
    print(json.dumps(verdict, indent=2))
    with open("verdict.json", "w") as f:
        json.dump(verdict, f)
