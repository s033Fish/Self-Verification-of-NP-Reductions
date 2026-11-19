import random
import json
import sys
from itertools import product
from problems import Sat, ThreeSat
from reduce import reduce as reduce_sat


def sat_bruteforce(instance):
    Sat.validate(instance)
    m = instance["num_vars"]
    clauses = instance["clauses"]
    # Edge: empty clause -> unsat
    for c in clauses:
        if len(c) == 0:
            return False
    for assignment in product([False, True], repeat=m):
        ok = True
        for clause in clauses:
            clause_ok = False
            for lit in clause:
                var = abs(lit) - 1
                val = assignment[var]
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
    for assignment in product([False, True], repeat=m):
        ok = True
        for clause in clauses:
            clause_ok = False
            for lit in clause:
                var = abs(lit) - 1
                val = assignment[var]
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


def random_sat_instance(max_vars=4, max_clauses=5, max_lits=4):
    m = random.randint(0, max_vars)
    clauses = []
    for _ in range(random.randint(0, max_clauses)):
        k = random.randint(0, max_lits)
        clause = []
        for __ in range(k):
            if m == 0:
                continue
            var = random.randint(1, m)
            lit = var if random.choice([True, False]) else -var
            clause.append(lit)
        clauses.append(clause)
    return {"num_vars": m, "clauses": clauses}


def run_tests(num=200):
    passed = 0
    for i in range(num):
        inst = random_sat_instance()
        # compute answers
        sat_ans = sat_bruteforce(inst)
        reduced = reduce_sat(inst)
        three_ans = three_sat_bruteforce(reduced)
        if sat_ans == three_ans:
            passed += 1
        else:
            print("Mismatch on instance", inst)
            print("Reduced", reduced)
            print("sat", sat_ans, "three", three_ans)
            break
    return passed, num

if __name__ == "__main__":
    passed, total = run_tests(500)
    result = {
        "verified": passed == total,
        "tests_run": total,
        "tests_passed": passed,
    }
    print(json.dumps(result, indent=2))
    with open("verdict.json", "w") as f:
        json.dump(result, f)
    sys.exit(0 if result["verified"] else 1)
