import itertools
import random
import json
from problems import Sat, Clique
from reduce import reduce


def sat_bruteforce(instance):
    m = instance["num_vars"]
    clauses = instance["clauses"]
    # Edge cases handled naturally
    for bits in range(1 << m):
        assignment = [(bits >> i) & 1 == 1 for i in range(m)]  # index 0 -> var1
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


def clique_bruteforce(instance):
    n = instance["n"]
    edges_set = {frozenset(e) for e in instance["edges"]}
    k = instance["k"]
    if k <= 0:
        return True
    if k == 1:
        return n >= 1
    if k > n:
        return False
    # check subsets of size k up to n
    for size in range(k, n + 1):
        for subset in itertools.combinations(range(n), size):
            good = True
            for u, v in itertools.combinations(subset, 2):
                if frozenset((u, v)) not in edges_set:
                    good = False
                    break
            if good:
                return True
    return False


def random_sat_instance(max_vars=4, max_clauses=4, max_lits=3):
    num_vars = random.randint(0, max_vars)
    clauses = []
    for _ in range(random.randint(0, max_clauses)):
        clause = []
        for _ in range(random.randint(0, max_lits)):
            if num_vars == 0:
                continue
            var = random.randint(1, num_vars)
            lit = var if random.choice([True, False]) else -var
            clause.append(lit)
        clauses.append(clause)
    return {"num_vars": num_vars, "clauses": clauses}


def run_tests(num_tests=200):
    passed = 0
    for _ in range(num_tests):
        sat_inst = random_sat_instance()
        # validate
        Sat.validate(sat_inst)
        sat_ans = sat_bruteforce(sat_inst)
        clique_inst = reduce(sat_inst)
        Clique.validate(clique_inst)
        clique_ans = clique_bruteforce(clique_inst)
        if sat_ans == clique_ans:
            passed += 1
        else:
            print("Mismatch!", json.dumps(sat_inst), json.dumps(clique_inst), sat_ans, clique_ans)
            break
    return passed, num_tests

if __name__ == "__main__":
    passed, total = run_tests()
    print(f"{passed}/{total} tests passed")
