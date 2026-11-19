import itertools
import random
import json
import sys
from typing import List, Dict

import problems
from reduce import reduce


def solve_three_sat(instance: Dict) -> bool:
    m = instance["num_vars"]
    clauses: List[List[int]] = instance["clauses"]
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


def solve_vertex_cover(instance: Dict) -> bool:
    n = instance["n"]
    edges = [tuple(e) for e in instance["edges"]]
    k = instance["k"]
    if k < 0:
        return False
    # If k >= n, always yes
    if k >= n:
        return True
    # brute force subsets up to k
    vertices = list(range(n))
    for r in range(k + 1):
        for subset in itertools.combinations(vertices, r):
            covered = True
            s = set(subset)
            for u, v in edges:
                if u not in s and v not in s:
                    covered = False
                    break
            if covered:
                return True
    return False


def random_three_sat(max_vars=4, max_clauses=5):
    m = random.randint(0, max_vars)
    # ensure at least 3 vars if there are clauses
    if m < 3:
        # may still have zero clauses; if we generate clauses we need >=3
        pass
    # generate random number of clauses
    c = random.randint(0, max_clauses)
    clauses = []
    for _ in range(c):
        # ensure we have at least 3 vars for a clause
        if m < 3:
            # increase m to 3
            m = 3
        vars_in_clause = random.sample(range(1, m + 1), 3)
        clause = []
        for v in vars_in_clause:
            lit = v if random.choice([True, False]) else -v
            clause.append(lit)
        clauses.append(clause)
    return {"num_vars": m, "clauses": clauses}


def run_tests(num_tests=200):
    passed = 0
    for i in range(num_tests):
        inst = random_three_sat()
        # validate source
        try:
            problems.ThreeSat.validate(inst)
        except Exception as e:
            print("Invalid source instance", inst, e)
            continue
        sat = solve_three_sat(inst)
        red = reduce(inst)
        # validate target
        problems.VertexCover.validate(red)
        vc = solve_vertex_cover(red)
        if sat == vc:
            passed += 1
        else:
            print("Mismatch on test", i)
            print("instance", inst)
            print("sat", sat, "vc", vc)
            print("reduced", red)
            break
    return passed, num_tests

if __name__ == "__main__":
    passed, total = run_tests()
    result = {
        "verified": passed == total,
        "tests_run": total,
        "tests_passed": passed,
    }
    print(json.dumps(result, indent=2))
    with open("verdict.json", "w") as f:
        json.dump(result, f)
