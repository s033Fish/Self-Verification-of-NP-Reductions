import itertools
import random
import json
from problems import ThreeSat, Clique
from reduce import reduce


def solve_3sat(instance):
    m = instance["num_vars"]
    clauses = instance["clauses"]
    # iterate over all assignments
    for bits in range(1 << m):
        ok = True
        for clause in clauses:
            clause_ok = False
            for lit in clause:
                var = abs(lit) - 1
                val = (bits >> var) & 1  # 1 means true
                if lit > 0 and val == 1:
                    clause_ok = True
                if lit < 0 and val == 0:
                    clause_ok = True
                if clause_ok:
                    break
            if not clause_ok:
                ok = False
                break
        if ok:
            return True
    return False


def solve_clique(instance):
    n = instance["n"]
    edges = set()
    for u, v in instance["edges"]:
        if u > v:
            u, v = v, u
        edges.add((u, v))
    k = instance["k"]
    if k <= 0:
        return True
    if k == 1:
        return n >= 1
    if k > n:
        return False
    # check all subsets of size k
    for combo in itertools.combinations(range(n), k):
        good = True
        for i in range(k):
            for j in range(i+1, k):
                u, v = combo[i], combo[j]
                if u > v:
                    u, v = v, u
                if (u, v) not in edges:
                    good = False
                    break
            if not good:
                break
        if good:
            return True
    return False


def random_3sat_instance(num_vars, num_clauses):
    clauses = []
    for _ in range(num_clauses):
        vars = random.sample(range(1, num_vars+1), 3)
        clause = []
        for v in vars:
            lit = v if random.choice([True, False]) else -v
            clause.append(lit)
        clauses.append(clause)
    return {"num_vars": num_vars, "clauses": clauses}


def run_tests(num_tests=200):
    passed = 0
    for _ in range(num_tests):
        m = random.randint(0, 5)  # keep small for brute force
        # ensure if clauses >0 then m>=3 per spec, but allow smaller for testing
        c = random.randint(0, 5)
        if c > 0 and m < 3:
            m = 3
        instance = random_3sat_instance(m, c)
        # validate
        ThreeSat.validate(instance)
        red = reduce(instance)
        Clique.validate(red)
        ans1 = solve_3sat(instance)
        ans2 = solve_clique(red)
        if ans1 == ans2:
            passed += 1
        else:
            print("Mismatch!", instance, red, ans1, ans2)
            break
    return passed, num_tests

if __name__ == "__main__":
    passed, total = run_tests(500)
    print(f"{passed}/{total} tests passed")
    verdict = {"verified": passed == total, "tests_run": total, "tests_passed": passed}
    with open('verdict.json', 'w') as f:
        json.dump(verdict, f)
