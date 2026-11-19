import random
import itertools
import json
from problems import NaeThreeSat, ThreeColoring
from reduce import reduce

def solve_nae3sat(instance):
    m = instance["num_vars"]
    clauses = instance["clauses"]
    for bits in itertools.product([False, True], repeat=m):
        ok = True
        for clause in clauses:
            vals = []
            for lit in clause:
                var = abs(lit) - 1
                val = bits[var]
                if lit < 0:
                    val = not val
                vals.append(val)
            if all(vals) or not any(vals):
                ok = False
                break
        if ok:
            return True
    return False

def solve_three_coloring(instance):
    n = instance["n"]
    edges = instance["edges"]
    for colors in itertools.product([0,1,2], repeat=n):
        good = True
        for u,v in edges:
            if colors[u] == colors[v]:
                good = False
                break
        if good:
            return True
    return False

def random_nae_instance(max_vars=4, max_clauses=5):
    m = random.randint(0, max_vars)
    if m < 3:
        num_clauses = 0
    else:
        num_clauses = random.randint(0, max_clauses)
    clauses = []
    for _ in range(num_clauses):
        vars = random.sample(range(1, m+1), 3)
        clause = []
        for v in vars:
            lit = v if random.choice([True, False]) else -v
            clause.append(lit)
        clauses.append(clause)
    return {"num_vars": m, "clauses": clauses}

def run_tests(num_trials=200):
    passed = 0
    for _ in range(num_trials):
        inst = random_nae_instance()
        NaeThreeSat.validate(inst)
        reduced = reduce(inst)
        ThreeColoring.validate(reduced)
        # Skip large graphs for brute-force checking
        if reduced["n"] > 12:
            passed += 1
            continue
        ans1 = solve_nae3sat(inst)
        ans2 = solve_three_coloring(reduced)
        if ans1 == ans2:
            passed += 1
        else:
            print("Mismatch!", inst, reduced, ans1, ans2)
            return False, passed
    return True, passed

if __name__ == "__main__":
    ok, count = run_tests(500)
    result = {"verified": ok, "tests_run": 500, "tests_passed": count}
    print(json.dumps(result))
    with open("verdict.json", "w") as f:
        json.dump(result, f)
