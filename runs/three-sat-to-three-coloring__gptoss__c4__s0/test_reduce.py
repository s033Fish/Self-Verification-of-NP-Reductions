import itertools
import random
import json
from problems import ThreeSat, ThreeColoring
from reduce import reduce


def sat_bruteforce(instance):
    m = instance["num_vars"]
    clauses = instance["clauses"]
    for bits in itertools.product([False, True], repeat=m):
        ok = True
        for clause in clauses:
            clause_ok = False
            for lit in clause:
                var = abs(lit) - 1
                val = bits[var]
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


def coloring_bruteforce(instance):
    n = instance["n"]
    edges = instance["edges"]
    for colors in itertools.product([0,1,2], repeat=n):
        good = True
        for u, v in edges:
            if colors[u] == colors[v]:
                good = False
                break
        if good:
            return True
    return False


def generate_random_sat(max_vars=3, max_clauses=1):
    """Generate a tiny random 3‑SAT instance suitable for exhaustive testing."""
    m = random.randint(0, max_vars)
    clauses = []
    num_clauses = random.randint(0, max_clauses)
    for _ in range(num_clauses):
        if m < 3:
            break
        vars = random.sample(range(1, m + 1), 3)
        clause = []
        for v in vars:
            lit = v if random.choice([True, False]) else -v
            clause.append(lit)
        clauses.append(clause)
    return {"num_vars": m, "clauses": clauses}


def run_tests(num_tests=50):
    passed = 0
    for _ in range(num_tests):
        inst = generate_random_sat()
        ThreeSat.validate(inst)
        sat_ans = sat_bruteforce(inst)
        graph = reduce(inst)
        ThreeColoring.validate(graph)
        col_ans = coloring_bruteforce(graph)
        if sat_ans == col_ans:
            passed += 1
        else:
            print("Mismatch on instance", inst)
            print("SAT answer", sat_ans, "Coloring answer", col_ans)
            print("Reduced graph", graph)
            break
    result = {"verified": passed == num_tests, "tests_run": num_tests, "tests_passed": passed}
    print(json.dumps(result, indent=2))
    with open("verdict.json", "w") as f:
        json.dump(result, f)

if __name__ == "__main__":
    run_tests()
