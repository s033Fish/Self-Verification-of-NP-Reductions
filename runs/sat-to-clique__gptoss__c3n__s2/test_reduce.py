import itertools
import json
import random
import sys
from typing import List

from problems import Sat, Clique
from reduce import reduce


def sat_bruteforce(instance) -> bool:
    Sat.validate(instance)
    m = instance["num_vars"]
    clauses: List[List[int]] = instance["clauses"]
    # Edge cases handled naturally
    for bits in itertools.product([False, True], repeat=m):
        assignment = {i+1: bits[i] for i in range(m)}
        ok = True
        for clause in clauses:
            # empty clause -> unsatisfied
            if len(clause) == 0:
                ok = False
                break
            clause_sat = any((lit > 0 and assignment[abs(lit)]) or (lit < 0 and not assignment[abs(lit)]) for lit in clause)
            if not clause_sat:
                ok = False
                break
        if ok:
            return True
    # also handle case of no clauses -> vacuously true
    return len(clauses) == 0


def clique_bruteforce(instance) -> bool:
    Clique.validate(instance)
    n = instance["n"]
    edges_set = {frozenset(e) for e in instance["edges"]}
    k = instance["k"]
    if k <= 0:
        return True
    if k == 1:
        return n >= 1
    if k > n:
        return False
    # check subsets of size >= k
    vertices = list(range(n))
    for size in range(k, n+1):
        for subset in itertools.combinations(vertices, size):
            good = True
            for u, v in itertools.combinations(subset, 2):
                if frozenset((u, v)) not in edges_set:
                    good = False
                    break
            if good:
                return True
    return False


def random_sat_instance(max_vars=4, max_clauses=4, max_lits=3):
    m = random.randint(0, max_vars)
    num_clauses = random.randint(0, max_clauses)
    clauses = []
    for _ in range(num_clauses):
        lit_count = random.randint(0, max_lits)
        clause = []
        for _ in range(lit_count):
            if m == 0:
                continue
            var = random.randint(1, m)
            lit = var if random.choice([True, False]) else -var
            clause.append(lit)
        clauses.append(clause)
    return {"num_vars": m, "clauses": clauses}


def run_tests(num_tests=200):
    passed = 0
    for i in range(num_tests):
        sat_inst = random_sat_instance()
        try:
            sat_inst = Sat.validate(sat_inst) or sat_inst
        except Exception as e:
            print("Invalid SAT instance generated", e)
            continue
        clique_inst = reduce(sat_inst)
        sat_ans = sat_bruteforce(sat_inst)
        clique_ans = clique_bruteforce(clique_inst)
        if sat_ans == clique_ans:
            passed += 1
        else:
            print("Mismatch on test", i)
            print("SAT", json.dumps(sat_inst))
            print("Clique", json.dumps(clique_inst))
            print("SAT ans", sat_ans, "Clique ans", clique_ans)
            break
    return passed, num_tests

if __name__ == "__main__":
    passed, total = run_tests()
    print(f"Passed {passed}/{total} tests")
    # write verdict
    verdict = {
        "verified": passed == total,
        "tests_run": total,
        "tests_passed": passed,
    }
    with open("verdict.json", "w") as f:
        json.dump(verdict, f)
    sys.exit(0 if passed == total else 1)

