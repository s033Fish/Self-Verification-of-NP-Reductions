import random
import json
import itertools
from problems import Sat, ThreeSat
from reduce import reduce


def sat_bruteforce(instance):
    m = instance["num_vars"]
    clauses = instance["clauses"]
    # edge cases
    if not clauses:
        return True
    for c in clauses:
        if len(c) == 0:
            return False
    for bits in itertools.product([False, True], repeat=m):
        assign = {i+1: bits[i] for i in range(m)}
        ok = True
        for clause in clauses:
            clause_ok = False
            for lit in clause:
                var = abs(lit)
                val = assign[var]
                if (lit > 0 and val) or (lit < 0 and not val):
                    clause_ok = True
                    break
            if not clause_ok:
                ok = False
                break
        if ok:
            return True
    return False


def three_sat_bruteforce(instance):
    m = instance["num_vars"]
    clauses = instance["clauses"]
    if not clauses:
        return True
    for bits in itertools.product([False, True], repeat=m):
        assign = {i+1: bits[i] for i in range(m)}
        ok = True
        for clause in clauses:
            clause_ok = False
            for lit in clause:
                var = abs(lit)
                val = assign[var]
                if (lit > 0 and val) or (lit < 0 and not val):
                    clause_ok = True
                    break
            if not clause_ok:
                ok = False
                break
        if ok:
            return True
    return False


def random_sat_instance(max_vars=4, max_clauses=5, max_lits=3):
    m = random.randint(0, max_vars)
    clauses = []
    for _ in range(random.randint(0, max_clauses)):
        clause_len = random.randint(0, max_lits)
        clause = []
        for _ in range(clause_len):
            if m == 0:
                continue
            var = random.randint(1, m)
            lit = var if random.choice([True, False]) else -var
            clause.append(lit)
        clauses.append(clause)
    return {"num_vars": m, "clauses": clauses}


def run_tests(num=200):
    passed = 0
    for _ in range(num):
        inst = random_sat_instance()
        # validate
        Sat.validate(inst)
        sat_res = sat_bruteforce(inst)
        reduced = reduce(inst)
        ThreeSat.validate(reduced)
        three_res = three_sat_bruteforce(reduced)
        if sat_res == three_res:
            passed += 1
        else:
            print("FAIL", json.dumps(inst), json.dumps(reduced), sat_res, three_res)
            break
    return passed, num

if __name__ == "__main__":
    passed, total = run_tests(500)
    print(f"Tests passed: {passed}/{total}")
