import itertools
import random
import json
from problems import Sat, IndependentSet
from reduce import reduce


def sat_bruteforce(instance):
    m = instance["num_vars"]
    clauses = instance["clauses"]
    # Edge case: empty clause -> unsat
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


def independent_set_bruteforce(instance):
    n = instance["n"]
    edges = set()
    for u, v in instance["edges"]:
        edges.add((u, v))
        edges.add((v, u))
    k = instance["k"]
    if k <= 0:
        return True
    if k > n:
        return False
    for r in range(k, n + 1):
        for subset in itertools.combinations(range(n), r):
            ok = True
            for u, v in itertools.combinations(subset, 2):
                if (u, v) in edges:
                    ok = False
                    break
            if ok:
                return True
    return False


def random_sat_instance(max_vars=4, max_clauses=3, max_clause_len=3):
    """Generate a random SAT instance that respects the validation rules."""
    m = random.randint(0, max_vars)
    num_clauses = random.randint(0, max_clauses)
    clauses = []
    for _ in range(num_clauses):
        if m == 0:
            length = 0
        else:
            length = random.randint(0, max_clause_len)
        clause = []
        for _ in range(length):
            var = random.randint(1, m)
            lit = var if random.choice([True, False]) else -var
            clause.append(lit)
        clauses.append(clause)
    return {"num_vars": m, "clauses": clauses}


def run_tests(num_tests=200):
    passed = 0
    for i in range(num_tests):
        inst = random_sat_instance()
        Sat.validate(inst)
        sat_ans = sat_bruteforce(inst)
        red = reduce(inst)
        IndependentSet.validate(red)
        is_ans = independent_set_bruteforce(red)
        if sat_ans == is_ans:
            passed += 1
        else:
            print("FAIL on instance", inst)
            print("sat", sat_ans, "ind", is_ans)
            print("reduced", red)
            break
    return passed, num_tests

if __name__ == "__main__":
    passed, total = run_tests()
    result = {"verified": passed == total, "tests_run": total, "tests_passed": passed}
    print(json.dumps(result))
    with open("verdict.json", "w") as f:
        json.dump(result, f)
