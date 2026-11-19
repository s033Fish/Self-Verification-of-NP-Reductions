import random
import itertools
import json
import sys
from problems import ExactCover, Sat
from reduce import reduce

def exact_cover_bruteforce(instance):
    ExactCover.validate(instance)
    u = instance["universe_size"]
    sets = instance["sets"]
    k = len(sets)
    # Edge case u=0 always yes
    if u == 0:
        return True
    # iterate over subsets of set indices
    for mask in range(1 << k):
        covered = [0] * u
        ok = True
        for i in range(k):
            if mask >> i & 1:
                for e in sets[i]:
                    if covered[e]:
                        ok = False
                        break
                    covered[e] = 1
                if not ok:
                    break
        if ok and all(covered):
            return True
    return False

def sat_bruteforce(instance):
    Sat.validate(instance)
    m = instance["num_vars"]
    clauses = instance["clauses"]
    # empty clause => unsat
    for clause in clauses:
        if len(clause) == 0:
            return False
    # iterate over assignments
    for bits in range(1 << m):
        assignment = [(bits >> i) & 1 == 1 for i in range(m)]  # index i => var i+1
        satisfied = True
        for clause in clauses:
            clause_sat = False
            for lit in clause:
                var = abs(lit) - 1
                val = assignment[var]
                if (lit > 0 and val) or (lit < 0 and not val):
                    clause_sat = True
                    break
            if not clause_sat:
                satisfied = False
                break
        if satisfied:
            return True
    return False

def random_exact_cover_instance(max_u=4, max_sets=5, max_set_size=4):
    u = random.randint(0, max_u)
    sets = []
    for _ in range(random.randint(0, max_sets)):
        size = random.randint(0, min(max_set_size, u))
        elems = random.sample(range(u), size) if u>0 else []
        sets.append(elems)
    return {"universe_size": u, "sets": sets}

def run_tests(num=200):
    passed = 0
    for _ in range(num):
        inst = random_exact_cover_instance()
        try:
            exact = exact_cover_bruteforce(inst)
            sat_inst = reduce(inst)
            sat_res = sat_bruteforce(sat_inst)
            if exact != sat_res:
                print("Mismatch!", json.dumps(inst), "=>", exact, sat_res)
                print("SAT instance", json.dumps(sat_inst))
                return False, passed
        except Exception as e:
            print("Error", e, inst)
            return False, passed
        passed += 1
    return True, passed

if __name__ == "__main__":
    ok, count = run_tests(200)
    result = {"verified": ok, "tests_run": count, "tests_passed": count if ok else 0}
    print(json.dumps(result))
    sys.exit(0 if ok else 1)
