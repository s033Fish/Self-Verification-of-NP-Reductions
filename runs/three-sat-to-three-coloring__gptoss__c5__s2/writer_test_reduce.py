import itertools
import random
import json
from problems import ThreeSat, ThreeColoring
from reduce import reduce

def solve_3sat(instance):
    m = instance["num_vars"]
    clauses = instance["clauses"]
    for bits in itertools.product([False, True], repeat=m):
        ok = True
        for clause in clauses:
            sat = False
            for lit in clause:
                var = abs(lit) - 1
                val = bits[var]
                if lit > 0 and val:
                    sat = True
                if lit < 0 and not val:
                    sat = True
                if sat:
                    break
            if not sat:
                ok = False
                break
        if ok:
            return True
    return False

def solve_3coloring(instance):
    n = instance["n"]
    edges = [(u, v) for u, v in instance["edges"]]
    for colors in itertools.product(range(3), repeat=n):
        good = True
        for u, v in edges:
            if colors[u] == colors[v]:
                good = False
                break
        if good:
            return True
    return False

def random_3sat(m, clause_count):
    clauses = []
    for _ in range(clause_count):
        vars = random.sample(range(1, m+1), 3)
        clause = []
        for v in vars:
            lit = v if random.choice([True, False]) else -v
            clause.append(lit)
        clauses.append(clause)
    return {"num_vars": m, "clauses": clauses}

def run_tests(num_tests=200):
    passed = 0
    for _ in range(num_tests):
        # keep graph small for exhaustive coloring
        while True:
            m = random.randint(0, 3)
            clause_cnt = random.randint(0, 3)
            if clause_cnt > 0 and m < 3:
                m = 3
            n_vertices = 3 + 2 * m + 3 * clause_cnt
            if n_vertices <= 10:
                break
        instance = random_3sat(m, clause_cnt)
        ThreeSat.validate(instance)
        sat_ans = solve_3sat(instance)
        red = reduce(instance)
        ThreeColoring.validate(red)
        col_ans = solve_3coloring(red)
        if sat_ans == col_ans:
            passed += 1
        else:
            print("Mismatch!", instance, sat_ans, col_ans)
            break
    return passed, num_tests

if __name__ == "__main__":
    passed, total = run_tests(200)
    result = {"verified": passed == total, "tests_run": total, "tests_passed": passed}
    print(json.dumps(result))
    with open("verdict.json", "w") as f:
        json.dump(result, f)
