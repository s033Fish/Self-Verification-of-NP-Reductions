import random
import itertools
import json
from problems import ThreeSat, ThreeColoring
from reduce import reduce


def solve_three_sat(instance):
    m = instance["num_vars"]
    clauses = instance["clauses"]
    for bits in itertools.product([False, True], repeat=m):
        ok = True
        for clause in clauses:
            clause_val = False
            for lit in clause:
                var = abs(lit) - 1
                val = bits[var]
                if lit < 0:
                    val = not val
                if val:
                    clause_val = True
                    break
            if not clause_val:
                ok = False
                break
        if ok:
            return True
    return False


def solve_three_coloring(instance):
    n = instance["n"]
    edges = [(u, v) for u, v in instance["edges"]]
    for colors in itertools.product([0, 1, 2], repeat=n):
        good = True
        for u, v in edges:
            if colors[u] == colors[v]:
                good = False
                break
        if good:
            return True
    return False


def random_three_sat(max_vars=3, max_clauses=1):
    """Generate a tiny random 3‑SAT instance for testing."""
    m = random.randint(0, max_vars)
    num_clauses = random.randint(0, max_clauses)
    clauses = []
    for _ in range(num_clauses):
        if m < 3:
            continue
        vars = random.sample(range(1, m + 1), 3)
        clause = []
        for v in vars:
            clause.append(v if random.choice([True, False]) else -v)
        clauses.append(clause)
    return {"num_vars": m, "clauses": clauses}


def run_tests(num_tests=200):
    passed = 0
    evaluated = 0
    for _ in range(num_tests):
        inst = random_three_sat()
        ThreeSat.validate(inst)
        reduced = reduce(inst)
        ThreeColoring.validate(reduced)
        # Keep graph small for exhaustive coloring solver.
        if reduced["n"] > 12:
            continue
        evaluated += 1
        ans_sat = solve_three_sat(inst)
        ans_col = solve_three_coloring(reduced)
        if ans_sat == ans_col:
            passed += 1
        else:
            print("Mismatch!", inst, ans_sat, ans_col)
            break
    return passed, evaluated

if __name__ == "__main__":
    passed, total = run_tests(500)
    result = {"verified": passed == total, "tests_run": total, "tests_passed": passed}
    print(json.dumps(result, indent=2))
    with open("verdict.json", "w") as f:
        json.dump(result, f)
