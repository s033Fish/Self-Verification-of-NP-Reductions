import itertools
import random
import json
from typing import List, Dict

from reduce import reduce
from problems import ThreeSat, IndependentSet


def sat_bruteforce(instance: Dict) -> bool:
    m = instance["num_vars"]
    clauses = instance["clauses"]
    for bits in itertools.product([False, True], repeat=m):
        ok = True
        for clause in clauses:
            clause_ok = False
            for lit in clause:
                var = abs(lit) - 1
                val = bits[var]
                if lit > 0 and val:
                    clause_ok = True
                if lit < 0 and not val:
                    clause_ok = True
            if not clause_ok:
                ok = False
                break
        if ok:
            return True
    return False


def indep_set_bruteforce(instance: Dict) -> bool:
    n = instance["n"]
    edges = {frozenset(e) for e in instance["edges"]}
    k = instance["k"]
    # any subset of size >= k that is independent
    for size in range(k, n + 1):
        for subset in itertools.combinations(range(n), size):
            independent = True
            for u, v in itertools.combinations(subset, 2):
                if frozenset((u, v)) in edges:
                    independent = False
                    break
            if independent:
                return True
    return False


def random_three_sat(max_vars=4, max_clauses=4) -> Dict:
    m = random.randint(0, max_vars)
    # ensure at least 3 vars if there are clauses
    num_clauses = random.randint(0, max_clauses)
    if num_clauses > 0 and m < 3:
        m = 3
    clauses: List[List[int]] = []
    for _ in range(num_clauses):
        # pick 3 distinct vars
        vars = random.sample(range(1, m + 1), 3)
        clause = []
        for v in vars:
            lit = v if random.choice([True, False]) else -v
            clause.append(lit)
        clauses.append(clause)
    return {"num_vars": m, "clauses": clauses}

def main():
    random.seed(0)
    tests = 200
    passed = 0
    for i in range(tests):
        inst = random_three_sat()
        # validate source
        ThreeSat.validate(inst)
        sat = sat_bruteforce(inst)
        red = reduce(inst)
        IndependentSet.validate(red)
        indep = indep_set_bruteforce(red)
        if sat == indep:
            passed += 1
        else:
            print("FAIL on instance", inst)
            print("sat", sat, "indep", indep)
            print("reduction", red)
            break
    print(f"{passed}/{tests} tests passed")
    # write verdict
    verdict = {"verified": passed == tests, "tests_run": tests, "tests_passed": passed}
    with open('verdict.json', 'w') as f:
        json.dump(verdict, f)

if __name__ == "__main__":
    main()
