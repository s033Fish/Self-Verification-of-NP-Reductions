import itertools
import json
import sys
from typing import List, Dict

from reduce import reduce
from problems import Sat, Clique


def sat_bruteforce(instance: Dict) -> bool:
    m = instance["num_vars"]
    clauses: List[List[int]] = instance["clauses"]
    for assignment in range(1 << m):
        ok = True
        for clause in clauses:
            clause_sat = False
            for lit in clause:
                var = abs(lit) - 1
                val = (assignment >> var) & 1
                if lit > 0 and val == 1:
                    clause_sat = True
                    break
                if lit < 0 and val == 0:
                    clause_sat = True
                    break
            if not clause_sat:
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
    for size in range(k, n + 1):
        for subset in itertools.combinations(range(n), size):
            all_edges = True
            for u, v in itertools.combinations(subset, 2):
                if frozenset((u, v)) not in edges_set:
                    all_edges = False
                    break
            if all_edges:
                return True
    return False


def generate_random_sat(max_vars=3, max_clauses=3, max_lits=3):
    import random
    m = random.randint(0, max_vars)
    num_clauses = random.randint(0, max_clauses)
    clauses = []
    for _ in range(num_clauses):
        if m == 0:
            clause_len = 0
        else:
            clause_len = random.randint(0, max_lits)
        clause = []
        for _ in range(clause_len):
            var = random.randint(1, m)
            sign = random.choice([1, -1])
            clause.append(sign * var)
        clauses.append(clause)
    return {"num_vars": m, "clauses": clauses}


def run_tests(num_tests=200):
    passed = 0
    for i in range(num_tests):
        inst = generate_random_sat()
        Sat.validate(inst)
        sat_ans = sat_bruteforce(inst)
        red = reduce(inst)
        Clique.validate(red)
        clique_ans = clique_bruteforce(red)
        if sat_ans == clique_ans:
            passed += 1
        else:
            print("Mismatch on instance", i)
            print(json.dumps(inst, indent=2))
            print("Reduction", json.dumps(red, indent=2))
            print("SAT ans", sat_ans, "Clique ans", clique_ans)
            return passed, i
    return passed, num_tests

if __name__ == "__main__":
    passed, total = run_tests()
    print(f"Tests passed: {passed}/{total}")
    verdict = {
        "verified": passed == total,
        "tests_run": total,
        "tests_passed": passed,
    }
    with open("verdict.json", "w") as f:
        json.dump(verdict, f)
    sys.exit(0 if passed == total else 1)
