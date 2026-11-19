import itertools
import random
import json
from problems import Sat, Clique, InvalidInstance
from reduce import reduce

def sat_bruteforce(instance):
    # Returns True if satisfiable
    Sat.validate(instance)
    m = instance["num_vars"]
    clauses = instance["clauses"]
    # Edge cases handled naturally
    for bits in itertools.product([False, True], repeat=m):
        assignment = {i+1: bits[i] for i in range(m)}
        ok = True
        for clause in clauses:
            # empty clause => unsatisfied
            if not clause:
                ok = False
                break
            clause_sat = False
            for lit in clause:
                var = abs(lit)
                val = assignment[var]
                if lit > 0 and val:
                    clause_sat = True
                    break
                if lit < 0 and not val:
                    clause_sat = True
                    break
            if not clause_sat:
                ok = False
                break
        if ok:
            return True
    return False

def clique_bruteforce(instance):
    Clique.validate(instance)
    n = instance["n"]
    edges_set = {frozenset(e) for e in instance["edges"]}
    k = instance["k"]
    if k <= 0:
        return True
    if k == 1:
        return n >= 1
    if k > n:
        return False
    # check subsets of size >= k
    for size in range(k, n+1):
        for subset in itertools.combinations(range(n), size):
            good = True
            for u, v in itertools.combinations(subset, 2):
                if frozenset((u, v)) not in edges_set:
                    good = False
                    break
            if good:
                return True
    return False

def random_sat_instance(max_vars=4, max_clauses=4, max_lits_per_clause=3):
    m = random.randint(0, max_vars)
    c = random.randint(0, max_clauses)
    clauses = []
    for _ in range(c):
        l = random.randint(0, max_lits_per_clause)
        clause = []
        for _ in range(l):
            var = random.randint(1, max(1, m))
            lit = var if random.choice([True, False]) else -var
            clause.append(lit)
        clauses.append(clause)
    return {"num_vars": m, "clauses": clauses}

def run_tests(num=200):
    passed = 0
    for _ in range(num):
        inst = random_sat_instance()
        # ensure valid (Sat.validate will raise if invalid)
        try:
            Sat.validate(inst)
        except InvalidInstance:
            continue
        sat_ans = sat_bruteforce(inst)
        clique_inst = reduce(inst)
        clique_ans = clique_bruteforce(clique_inst)
        if sat_ans == clique_ans:
            passed += 1
        else:
            print("Mismatch!", inst, "sat", sat_ans, "clique", clique_ans)
            print("Reduced", clique_inst)
            break
    return passed, num

if __name__ == "__main__":
    passed, total = run_tests(500)
    verdict = {
        "verified": passed == total,
        "tests_run": total,
        "tests_passed": passed,
    }
    print(json.dumps(verdict))
    with open("verdict.json", "w") as f:
        json.dump(verdict, f)
