import itertools
import json
import random
import sys
from typing import List, Dict

from problems import Sat, IndependentSet
from reduce import reduce


def sat_bruteforce(instance: Dict) -> bool:
    m = instance["num_vars"]
    clauses = instance["clauses"]
    # Edge cases handled automatically by checking assignments
    for bits in itertools.product([False, True], repeat=m):
        assignment = {i + 1: bits[i] for i in range(m)}
        ok = True
        for clause in clauses:
            # empty clause -> unsatisfied
            if not clause:
                ok = False
                break
            clause_sat = False
            for lit in clause:
                var = abs(lit)
                val = assignment[var]
                if lit > 0 and val:
                    clause_sat = True
                    break
                if lit < 0 and not val:
                    clause_sat = True
                    break
            if not clause_sat:
                ok = False
                break
        if ok:
            return True
    return False


def indep_bruteforce(instance: Dict) -> bool:
    n = instance["n"]
    edges = set()
    for u, v in instance["edges"]:
        edges.add(frozenset((u, v)))
    k = instance["k"]
    if k <= 0:
        return True
    if k > n:
        return False
    # iterate subsets of size >= k
    for size in range(k, n + 1):
        for subset in itertools.combinations(range(n), size):
            ok = True
            for i in range(len(subset)):
                for j in range(i + 1, len(subset)):
                    if frozenset((subset[i], subset[j])) in edges:
                        ok = False
                        break
                if not ok:
                    break
            if ok:
                return True
    return False


def random_sat_instance(max_vars=4, max_clauses=4, max_lits=3) -> Dict:
    m = random.randint(0, max_vars)
    num_clauses = random.randint(0, max_clauses)
    clauses: List[List[int]] = []
    for _ in range(num_clauses):
        lits = []
        num_lits = random.randint(0, max_lits)
        for _ in range(num_lits):
            if m == 0:
                continue
            var = random.randint(1, m)
            lit = var if random.choice([True, False]) else -var
            lits.append(lit)
        clauses.append(lits)
    return {"num_vars": m, "clauses": clauses}


def run_tests(num_tests=200):
    passed = 0
    for _ in range(num_tests):
        sat_inst = random_sat_instance()
        # validate
        Sat.validate(sat_inst)
        target_inst = reduce(sat_inst)
        IndependentSet.validate(target_inst)
        sat_ans = sat_bruteforce(sat_inst)
        indep_ans = indep_bruteforce(target_inst)
        if sat_ans == indep_ans:
            passed += 1
        else:
            print("Mismatch!", json.dumps(sat_inst), json.dumps(target_inst), sat_ans, indep_ans)
            break
    return num_tests, passed

if __name__ == "__main__":
    total, passed = run_tests()
    verdict = {"verified": passed == total, "tests_run": total, "tests_passed": passed}
    with open("verdict.json", "w") as f:
        json.dump(verdict, f)
    print(json.dumps(verdict))
