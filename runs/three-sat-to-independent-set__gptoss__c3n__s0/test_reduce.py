import itertools
import random
import json
from problems import ThreeSat, IndependentSet
from reduce import reduce


def solve_three_sat(instance):
    m = instance["num_vars"]
    clauses = instance["clauses"]
    # iterate over all assignments
    for bits in itertools.product([False, True], repeat=m):
        ok = True
        for clause in clauses:
            clause_ok = False
            for lit in clause:
                var = abs(lit) - 1
                val = bits[var]
                if lit > 0 and val:
                    clause_ok = True
                if lit < 0 and not val:
                    clause_ok = True
                if clause_ok:
                    break
            if not clause_ok:
                ok = False
                break
        if ok:
            return True
    return False


def solve_independent_set(instance):
    n = instance["n"]
    edges = set()
    for u, v in instance["edges"]:
        if u > v:
            u, v = v, u
        edges.add((u, v))
    k = instance["k"]
    # check all subsets of size >= k (but we can early exit)
    # brute force all subsets
    for r in range(k, n + 1):
        for subset in itertools.combinations(range(n), r):
            good = True
            for i in range(len(subset)):
                for j in range(i + 1, len(subset)):
                    if (subset[i], subset[j]) in edges:
                        good = False
                        break
                if not good:
                    break
            if good:
                return True
    return False


def random_three_sat(num_vars, num_clauses):
    clauses = []
    for _ in range(num_clauses):
        # pick 3 distinct vars
        vars = random.sample(range(1, num_vars + 1), 3)
        clause = []
        for v in vars:
            lit = v if random.choice([True, False]) else -v
            clause.append(lit)
        clauses.append(clause)
    return {"num_vars": num_vars, "clauses": clauses}


def run_tests(num_trials=200):
    passed = 0
    for _ in range(num_trials):
        # small sizes
        m = random.randint(0, 4)
        c = random.randint(0, 5)
        # ensure if clauses>0 then m>=3 per spec, but we can still generate with m<3, but validation may reject.
        if c > 0 and m < 3:
            m = 3
        inst = random_three_sat(m, c)
        # validate
        ThreeSat.validate(inst)
        red = reduce(inst)
        IndependentSet.validate(red)
        ans1 = solve_three_sat(inst)
        ans2 = solve_independent_set(red)
        if ans1 == ans2:
            passed += 1
        else:
            print("Mismatch!", inst, red, ans1, ans2)
            break
    return passed, num_trials

if __name__ == "__main__":
    passed, total = run_tests(200)
    result = {"verified": passed == total, "tests_run": total, "tests_passed": passed}
    print(json.dumps(result))
    with open("verdict.json", "w") as f:
        json.dump(result, f)
