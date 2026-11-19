import random
import itertools
import json
from problems import Sat, Clique
from reduce import reduce

def sat_bruteforce(instance):
    m = instance["num_vars"]
    clauses = instance["clauses"]
    # Edge case: empty clause => unsat
    for cl in clauses:
        if len(cl) == 0:
            return False
    # No clauses => sat
    if not clauses:
        return True
    for bits in range(1 << m):
        assignment = [(bits >> i) & 1 == 1 for i in range(m)]  # var i+1
        ok = True
        for cl in clauses:
            clause_ok = False
            for lit in cl:
                var = abs(lit) - 1
                sign = lit > 0
                if assignment[var] == sign:
                    clause_ok = True
                    break
            if not clause_ok:
                ok = False
                break
        if ok:
            return True
    return False

def clique_bruteforce(instance):
    n = instance["n"]
    edges_set = {frozenset(e) for e in instance["edges"]}
    k = instance["k"]
    # Edge cases handled by definition
    if k <= 0:
        return True
    if k == 1:
        return n >= 1
    if k > n:
        return False
    # check all subsets of size >=k
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
    num_clauses = random.randint(0, max_clauses)
    clauses = []
    for _ in range(num_clauses):
        lits = []
        num_lits = random.randint(0, max_lits_per_clause)
        for _ in range(num_lits):
            if m == 0:
                continue
            var = random.randint(1, m)
            sign = random.choice([True, False])
            lit = var if sign else -var
            lits.append(lit)
        clauses.append(lits)
    return {"num_vars": m, "clauses": clauses}

def run_tests(num_trials=200):
    passed = 0
    for _ in range(num_trials):
        sat_inst = random_sat_instance()
        # validate
        Sat.validate(sat_inst)
        red = reduce(sat_inst)
        Clique.validate(red)
        sat_ans = sat_bruteforce(sat_inst)
        clique_ans = clique_bruteforce(red)
        if sat_ans == clique_ans:
            passed += 1
        else:
            print("Mismatch!", json.dumps(sat_inst), json.dumps(red), sat_ans, clique_ans)
            break
    return passed, num_trials

if __name__ == "__main__":
    passed, total = run_tests()
    print(f"Tests passed: {passed}/{total}")
    verdict = {"verified": passed == total, "tests_run": total, "tests_passed": passed}
    with open("verdict.json", "w") as f:
        json.dump(verdict, f)
