import itertools
import json
import random
from typing import Dict, List

from problems import ThreeSat, ThreeColoring
from reduce import reduce


def sat_bruteforce(instance: Dict) -> bool:
    m = instance["num_vars"]
    clauses: List[List[int]] = instance["clauses"]
    for bits in itertools.product([False, True], repeat=m):
        ok = True
        for clause in clauses:
            clause_ok = False
            for lit in clause:
                var = abs(lit) - 1
                val = bits[var]
                if (lit > 0 and val) or (lit < 0 and not val):
                    clause_ok = True
                    break
            if not clause_ok:
                ok = False
                break
        if ok:
            return True
    return False


def coloring_bruteforce(instance: Dict) -> bool:
    n = instance["n"]
    edges = instance["edges"]
    for colors in itertools.product([0, 1, 2], repeat=n):
        good = True
        for u, v in edges:
            if colors[u] == colors[v]:
                good = False
                break
        if good:
            return True
    return False


def generate_all_sat_instances(max_vars=3, max_clauses=3) -> List[Dict]:
    instances = []
    for m in range(0, max_vars + 1):
        # generate all possible clauses respecting 3 distinct vars
        vars_range = list(range(1, m + 1))
        possible_clauses = []
        if m >= 3:
            for combo in itertools.combinations(vars_range, 3):
                # each variable can be positive or negative
                for signs in itertools.product([1, -1], repeat=3):
                    clause = [signs[i] * combo[i] for i in range(3)]
                    possible_clauses.append(clause)
        # include empty clause list case
        for num_clauses in range(0, max_clauses + 1):
            for clauses in itertools.combinations_with_replacement(possible_clauses, num_clauses):
                instance = {"num_vars": m, "clauses": [list(c) for c in clauses]}
                instances.append(instance)
    return instances


def test_random():
    # random small instances
    for _ in range(100):
        m = random.randint(0, 4)
        # ensure at least 3 vars if we add clauses
        num_clauses = random.randint(0, 4)
        clauses = []
        if m >= 3:
            for _ in range(num_clauses):
                vars_sel = random.sample(range(1, m + 1), 3)
                signs = [random.choice([1, -1]) for _ in range(3)]
                clauses.append([signs[i] * vars_sel[i] for i in range(3)])
        instance = {"num_vars": m, "clauses": clauses}
        yield instance


def run_tests():
    total = 0
    passed = 0
    # test exhaustive for tiny sizes
    for inst in generate_all_sat_instances(max_vars=3, max_clauses=2):
        total += 1
        ThreeSat.validate(inst)
        sat = sat_bruteforce(inst)
        red = reduce(inst)
        ThreeColoring.validate(red)
        col = coloring_bruteforce(red)
        if sat == col:
            passed += 1
        else:
            print("FAIL", inst, sat, col, red)
    # random tests larger vars up to 5
    for inst in test_random():
        total += 1
        ThreeSat.validate(inst)
        sat = sat_bruteforce(inst)
        red = reduce(inst)
        ThreeColoring.validate(red)
        col = coloring_bruteforce(red)
        if sat == col:
            passed += 1
        else:
            print("FAIL RANDOM", inst, sat, col, red)
    print(f"Tests run: {total}, passed: {passed}")
    return total, passed

if __name__ == "__main__":
    total, passed = run_tests()
    import json, os
    verdict = {"verified": passed == total, "tests_run": total, "tests_passed": passed}
    with open("verdict.json", "w") as f:
        json.dump(verdict, f)
    print(json.dumps(verdict))
