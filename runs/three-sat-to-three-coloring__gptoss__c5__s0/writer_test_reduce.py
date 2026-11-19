import itertools
import random
import json
from problems import ThreeSat, ThreeColoring
from reduce import reduce

def solve_three_sat(instance):
    m = instance["num_vars"]
    clauses = instance["clauses"]
    for bits in itertools.product([False, True], repeat=m):
        assign = {i+1: bits[i] for i in range(m)}
        ok = True
        for clause in clauses:
            clause_ok = False
            for lit in clause:
                var = abs(lit)
                val = assign[var]
                if lit > 0 and val:
                    clause_ok = True
                if lit < 0 and not val:
                    clause_ok = True
            if not clause_ok:
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

def random_three_sat(m, clause_count):
    """Generate a random 3‑SAT instance.
    For ``m < 3`` the definition of the problem allows formulas with no
    clauses only, because a clause must contain three distinct variables.
    In that case we simply ignore ``clause_count`` and return an empty clause
    list.
    """
    clauses = []
    if m >= 3:
        vars_list = list(range(1, m + 1))
        for _ in range(clause_count):
            vars_chosen = random.sample(vars_list, 3)
            clause = []
            for v in vars_chosen:
                lit = v if random.choice([True, False]) else -v
                clause.append(lit)
            clauses.append(clause)
    return {"num_vars": m, "clauses": clauses}

def run_tests():
    random.seed(0)
    total = 0
    passed = 0
    cases = []
    cases.append({"num_vars": 0, "clauses": []})
    cases.append({"num_vars": 3, "clauses": []})
    cases.append({"num_vars": 3, "clauses": [[1,2,3]]})
    for m in range(0,4):
        for c in range(0,4):
            cases.append(random_three_sat(m, c))
    for inst in cases:
        try:
            ThreeSat.validate(inst)
        except Exception as e:
            print("Invalid SAT instance", inst, e)
            continue
        sat = solve_three_sat(inst)
        graph = reduce(inst)
        ThreeColoring.validate(graph)
        col = solve_three_coloring(graph)
        total += 1
        if sat == col:
            passed += 1
        else:
            print("Mismatch!", inst, sat, col)
    print(f"Tests run: {total}, passed: {passed}")
    verdict = {"verified": passed==total, "tests_run": total, "tests_passed": passed}
    with open('verdict.json','w') as f:
        json.dump(verdict, f)

if __name__ == "__main__":
    run_tests()
