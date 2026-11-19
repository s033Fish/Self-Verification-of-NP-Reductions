import itertools
import random
import json
from problems import Sat, ThreeSat
from reduce import reduce

def sat_bruteforce(instance):
    Sat.validate(instance)
    m = instance["num_vars"]
    clauses = instance["clauses"]
    for c in clauses:
        if len(c) == 0:
            return False
    for assign in itertools.product([False, True], repeat=m):
        ok = True
        for clause in clauses:
            clause_ok = False
            for lit in clause:
                var = abs(lit) - 1
                val = assign[var]
                if lit > 0 and val:
                    clause_ok = True
                    break
                if lit < 0 and not val:
                    clause_ok = True
                    break
            if not clause_ok:
                ok = False
                break
        if ok:
            return True
    return False

def three_sat_bruteforce(instance):
    ThreeSat.validate(instance)
    m = instance["num_vars"]
    clauses = instance["clauses"]
    for assign in itertools.product([False, True], repeat=m):
        ok = True
        for clause in clauses:
            clause_ok = any((lit > 0 and assign[abs(lit)-1]) or (lit < 0 and not assign[abs(lit)-1]) for lit in clause)
            if not clause_ok:
                ok = False
                break
        if ok:
            return True
    return False

def random_sat_instance(max_vars=5, max_clauses=5, max_lits=4):
    m = random.randint(0, max_vars)
    clauses = []
    for _ in range(random.randint(0, max_clauses)):
        k = random.randint(0, max_lits)
        clause = []
        for _ in range(k):
            if m == 0:
                break
            var = random.randint(1, m)
            lit = var if random.choice([True, False]) else -var
            clause.append(lit)
        clauses.append(clause)
    return {"num_vars": m, "clauses": clauses}

def test_random_instances(num_tests=200):
    for i in range(num_tests):
        inst = random_sat_instance()
        red = reduce(inst)
        # Skip instances that would cause huge brute‑force enumeration.
        if red["num_vars"] > 12:
            continue
        sat_res = sat_bruteforce(inst)
        three_res = three_sat_bruteforce(red)
        if sat_res != three_res:
            print("Mismatch on instance", json.dumps(inst))
            print("Reduction", json.dumps(red))
            print("sat", sat_res, "three", three_res)
            return False
    return True

if __name__ == "__main__":
    ok = test_random_instances(500)
    print("All tests passed?", ok)
