import itertools
import random
import json
from problems import ThreeSat, NaeThreeSat
from reduce import reduce

def solve_three_sat(instance):
    m = instance["num_vars"]
    clauses = instance["clauses"]
    for assign in itertools.product([False, True], repeat=m):
        ok = True
        for clause in clauses:
            # clause literals
            val = False
            for lit in clause:
                var = abs(lit) - 1
                lit_val = assign[var]
                if lit < 0:
                    lit_val = not lit_val
                if lit_val:
                    val = True
                    break
            if not val:
                ok = False
                break
        if ok:
            return True
    return False

def solve_nae_three_sat(instance):
    m = instance["num_vars"]
    clauses = instance["clauses"]
    for assign in itertools.product([False, True], repeat=m):
        ok = True
        for clause in clauses:
            vals = []
            for lit in clause:
                var = abs(lit) - 1
                lit_val = assign[var]
                if lit < 0:
                    lit_val = not lit_val
                vals.append(lit_val)
            # NAE condition: not all equal, i.e., at least one True and one False
            if all(vals) or not any(vals):
                ok = False
                break
        if ok:
            return True
    return False

def random_instance(max_vars=4, max_clauses=5):
    m = random.randint(0, max_vars)
    # ensure at least 3 vars if we generate clauses
    if m < 3:
        m = 3
    num_clauses = random.randint(0, max_clauses)
    clauses = []
    for _ in range(num_clauses):
        # pick 3 distinct vars
        vars = random.sample(range(1, m+1), 3)
        clause = []
        for v in vars:
            lit = v if random.choice([True, False]) else -v
            clause.append(lit)
        clauses.append(clause)
    return {"num_vars": m, "clauses": clauses}

def test_random():
    for _ in range(200):
        inst = random_instance()
        ThreeSat.validate(inst)
        reduced = reduce(inst)
        NaeThreeSat.validate(reduced)
        ans1 = solve_three_sat(inst)
        ans2 = solve_nae_three_sat(reduced)
        if ans1 != ans2:
            print("Mismatch!", inst, reduced, ans1, ans2)
            return False
    return True

if __name__ == "__main__":
    ok = test_random()
    print({"tests_passed": ok, "tests_run": 200})
    # write verdict.json
    verdict = {"verified": ok, "tests_run": 200, "tests_passed": 200 if ok else 0}
    with open('verdict.json', 'w') as f:
        json.dump(verdict, f)
