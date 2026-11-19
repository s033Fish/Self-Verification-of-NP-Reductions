import random
import itertools
import json
from typing import List, Dict

from problems import ThreeSat, Clique
from reduce import reduce


def three_sat_bruteforce(instance: Dict) -> bool:
    m = instance["num_vars"]
    clauses: List[List[int]] = instance["clauses"]
    # iterate over all assignments 0..(1<<m)-1, where bit i corresponds to var i+1
    for mask in range(1 << m):
        ok = True
        for clause in clauses:
            clause_ok = False
            for lit in clause:
                var = abs(lit) - 1
                val = (mask >> var) & 1  # 1 means true
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


def clique_bruteforce(instance: Dict) -> bool:
    n = instance["n"]
    edges_set = {frozenset(e) for e in instance["edges"]}
    k = instance["k"]
    if k <= 0:
        return True
    if k == 1:
        return n >= 1
    if k > n:
        return False
    # check all subsets of size k (larger cliques also suffice, but if any size k exists it's enough)
    for subset in itertools.combinations(range(n), k):
        ok = True
        for u, v in itertools.combinations(subset, 2):
            if frozenset((u, v)) not in edges_set:
                ok = False
                break
        if ok:
            return True
    return False


def random_three_sat_instance(max_vars=4, max_clauses=5) -> Dict:
    m = random.randint(0, max_vars)
    # ensure at least 3 vars if there are clauses, per spec
    if m < 3:
        # allow zero clauses only
        num_clauses = 0
    else:
        num_clauses = random.randint(0, max_clauses)
    clauses = []
    for _ in range(num_clauses):
        # pick 3 distinct variables from 1..m
        vars_ = random.sample(range(1, m + 1), 3)
        clause = []
        for v in vars_:
            lit = v if random.choice([True, False]) else -v
            clause.append(lit)
        clauses.append(clause)
    return {"num_vars": m, "clauses": clauses}


def run_tests(num_tests=200):
    passed = 0
    for _ in range(num_tests):
        inst = random_three_sat_instance()
        # validate source
        ThreeSat.validate(inst)
        src_ans = three_sat_bruteforce(inst)
        red = reduce(inst)
        # validate target
        Clique.validate(red)
        tgt_ans = clique_bruteforce(red)
        if src_ans == tgt_ans:
            passed += 1
        else:
            print("Mismatch!")
            print(json.dumps(inst, indent=2))
            print("Reduction:", json.dumps(red, indent=2))
            print("src", src_ans, "tgt", tgt_ans)
            break
    return passed, num_tests

if __name__ == "__main__":
    passed, total = run_tests(500)
    result = {"verified": passed == total, "tests_run": total, "tests_passed": passed}
    print(json.dumps(result, indent=2))
    with open("verdict.json", "w") as f:
        json.dump(result, f)
