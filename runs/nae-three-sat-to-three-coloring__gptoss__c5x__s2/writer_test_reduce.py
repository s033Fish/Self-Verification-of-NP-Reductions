import json
import random
import sys
from itertools import product, combinations

import problems
from reduce import reduce, naesat_bruteforce

# Brute-force solver for NAE-3-SAT (same as helper)
def solve_naesat(inst):
    m = inst["num_vars"]
    clauses = inst["clauses"]
    for assign in product([False, True], repeat=m):
        ok = True
        for clause in clauses:
            vals = []
            for lit in clause:
                var = abs(lit) - 1
                val = assign[var]
                vals.append(val if lit > 0 else not val)
            if all(vals) or not any(vals):
                ok = False
                break
        if ok:
            return True
    return False

# Brute-force solver for 3-Coloring
def solve_threecoloring(inst):
    n = inst["n"]
    edges = [(u, v) for u, v in inst["edges"]]
    for coloring in product(range(3), repeat=n):
        good = True
        for u, v in edges:
            if coloring[u] == coloring[v]:
                good = False
                break
        if good:
            return True
    return False

def random_naesat_instance(max_vars=4, max_clauses=5):
    m = random.randint(0, max_vars)
    # ensure at least 3 vars if there will be clauses
    if m < 3:
        # allow zero clauses only
        return {"num_vars": m, "clauses": []}
    num_clauses = random.randint(0, max_clauses)
    clauses = []
    for _ in range(num_clauses):
        vars_in_clause = random.sample(range(1, m+1), 3)
        clause = []
        for v in vars_in_clause:
            lit = v if random.choice([True, False]) else -v
            clause.append(lit)
        clauses.append(clause)
    return {"num_vars": m, "clauses": clauses}

def main():
    tests = 200
    passed = 0
    for i in range(tests):
        inst = random_naesat_instance()
        # validate
        problems.NaeThreeSat.validate(inst)
        reduced = reduce(inst)
        problems.ThreeColoring.validate(reduced)
        ans1 = solve_naesat(inst)
        ans2 = solve_threecoloring(reduced)
        if ans1 == ans2:
            passed += 1
        else:
            print("Mismatch on instance", inst, "reduced", reduced, file=sys.stderr)
            break
    verdict = {"verified": passed == tests, "tests_run": tests, "tests_passed": passed}
    with open('verdict.json', 'w') as f:
        json.dump(verdict, f)
    print(json.dumps(verdict))

if __name__ == '__main__':
    main()
