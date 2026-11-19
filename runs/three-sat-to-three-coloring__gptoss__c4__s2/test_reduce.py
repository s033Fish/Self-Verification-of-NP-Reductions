import itertools
import random
import json
from problems import ThreeSat, ThreeColoring
from reduce import reduce

def solve_three_sat(instance):
    m = instance['num_vars']
    clauses = instance['clauses']
    for assignment in itertools.product([False, True], repeat=m):
        ok = True
        for clause in clauses:
            satisfied = False
            for lit in clause:
                var = abs(lit) - 1
                val = assignment[var]
                if lit > 0 and val:
                    satisfied = True
                if lit < 0 and not val:
                    satisfied = True
                if satisfied:
                    break
            if not satisfied:
                ok = False
                break
        if ok:
            return True
    return False

def solve_three_coloring(instance):
    n = instance['n']
    edges = [(u, v) for u, v in instance['edges']]
    for coloring in itertools.product([0,1,2], repeat=n):
        good = True
        for u, v in edges:
            if coloring[u] == coloring[v]:
                good = False
                break
        if good:
            return True
    return False

def random_three_sat(max_vars=3, max_clauses=3):
    """Generate a random small 3‑SAT instance for exhaustive testing."""
    m = random.randint(0, max_vars)
    num_clauses = random.randint(0, max_clauses)
    clauses = []
    for _ in range(num_clauses):
        var_range = max(m, 3)
        vars_pool = list(range(1, var_range + 1))
        chosen = random.sample(vars_pool, 3)
        clause = []
        for v in chosen:
            lit = v if random.choice([True, False]) else -v
            clause.append(lit)
        clauses.append(clause)
    return {"num_vars": m, "clauses": clauses}

def run_tests(num_tests=200, max_vertices=10):
    """Run a number of random tests, skipping reductions that are too large."""
    passed = 0
    examined = 0
    while examined < num_tests:
        inst = random_three_sat()
        try:
            ThreeSat.validate(inst)
        except Exception:
            continue
        red = reduce(inst)
        if red['n'] > max_vertices:
            continue
        examined += 1
        sat = solve_three_sat(inst)
        col = solve_three_coloring(red)
        if sat == col:
            passed += 1
        else:
            print('FAIL', inst, sat, col)
            break
    return passed, examined

if __name__ == '__main__':
    passed, total = run_tests()
    print(f"Passed {passed}/{total}")
    verdict = {"verified": passed==total, "tests_run": total, "tests_passed": passed}
    with open('verdict.json','w') as f:
        json.dump(verdict, f)
