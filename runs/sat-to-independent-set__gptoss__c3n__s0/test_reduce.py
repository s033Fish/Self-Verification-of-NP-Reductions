import random
import itertools
import json
from problems import Sat, IndependentSet
from reduce import reduce

def sat_bruteforce(instance):
    m = instance["num_vars"]
    clauses = instance["clauses"]
    # Edge case: any empty clause -> unsat
    for clause in clauses:
        if len(clause) == 0:
            return False
    # No clauses -> sat
    if not clauses:
        return True
    for bits in range(1 << m):
        assignment = [(bits >> i) & 1 == 1 for i in range(m)]  # var i+1
        ok = True
        for clause in clauses:
            clause_ok = False
            for lit in clause:
                var = abs(lit) - 1
                val = assignment[var]
                if (lit > 0 and val) or (lit < 0 and not val):
                    clause_ok = True
                    break
            if not clause_ok:
                ok = False
                break
        if ok:
            return True
    return False

def indep_bruteforce(instance):
    n = instance["n"]
    edges = set()
    for u, v in instance["edges"]:
        if u > v:
            u, v = v, u
        edges.add((u, v))
    k = instance["k"]
    if k <= 0:
        return True
    if k > n:
        return False
    vertices = list(range(n))
    for size in range(k, n+1):
        for combo in itertools.combinations(vertices, size):
            ok = True
            for i in range(len(combo)):
                for j in range(i+1, len(combo)):
                    if (combo[i], combo[j]) in edges:
                        ok = False
                        break
                if not ok:
                    break
            if ok:
                return True
    return False

def random_sat_instance(max_vars=4, max_clauses=4, max_lits=3):
    """Generate a random SAT instance respecting validation rules."""
    m = random.randint(0, max_vars)
    c = random.randint(0, max_clauses)
    clauses = []
    for _ in range(c):
        l = random.randint(0, max_lits)
        clause = []
        for _ in range(l):
            if m == 0:
                continue
            var = random.randint(1, m)
            lit = var if random.choice([True, False]) else -var
            clause.append(lit)
        clauses.append(clause)
    return {"num_vars": m, "clauses": clauses}

def run_tests(num_trials=200):
    passed = 0
    for _ in range(num_trials):
        inst = random_sat_instance()
        Sat.validate(inst)
        sat_ans = sat_bruteforce(inst)
        red = reduce(inst)
        IndependentSet.validate(red)
        indep_ans = indep_bruteforce(red)
        if sat_ans == indep_ans:
            passed += 1
        else:
            print("FAIL", inst, red, sat_ans, indep_ans)
            return False, passed
    return True, passed

if __name__ == "__main__":
    ok, passed = run_tests()
    result = {"verified": ok, "tests_run": 200, "tests_passed": passed}
    print(json.dumps(result))
    with open("verdict.json", "w") as f:
        json.dump(result, f)
