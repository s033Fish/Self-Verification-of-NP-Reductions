import random
import itertools
import json
import sys
from problems import NaeThreeSat, ThreeColoring
from reduce import reduce

def nae3sat_bruteforce(instance):
    m = instance["num_vars"]
    clauses = instance["clauses"]
    for bits in range(1 << m):
        assign = [(bits >> i) & 1 == 1 for i in range(m)]
        ok = True
        for clause in clauses:
            vals = []
            for lit in clause:
                var = abs(lit) - 1
                val = assign[var]
                if lit < 0:
                    val = not val
                vals.append(val)
            if all(vals) or not any(vals):
                ok = False
                break
        if ok:
            return True
    return False

def threecoloring_bruteforce(instance):
    n = instance["n"]
    edges = instance["edges"]
    for coloring in itertools.product(range(3), repeat=n):
        good = True
        for u, v in edges:
            if coloring[u] == coloring[v]:
                good = False
                break
        if good:
            return True
    return False

def random_nae_instance(max_vars=3, max_clauses=3):
    """Generate a small random NAE‑3‑SAT instance suitable for brute‑force.
    The bounds are deliberately tiny so that the exhaustive 3‑coloring
    check finishes quickly.
    """
    m = random.randint(0, max_vars)
    num_clauses = random.randint(0, max_clauses)
    clauses = []
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

def run_tests(num_tests=100):
    passed = 0
    for i in range(num_tests):
        # keep graph small enough for exhaustive 3‑coloring
        while True:
            inst = random_nae_instance()
            m = inst["num_vars"]
            num_clauses = len(inst["clauses"])
            n_est = 3 + 2 * m + 3 * num_clauses
            if n_est <= 12:
                break
        NaeThreeSat.validate(inst)
        red = reduce(inst)
        ThreeColoring.validate(red)
        ans1 = nae3sat_bruteforce(inst)
        ans2 = threecoloring_bruteforce(red)
        if ans1 != ans2:
            print("Mismatch on test", i)
            print(json.dumps(inst, indent=2))
            print("Reduced graph", red)
            print("NAE answer", ans1, "3Color answer", ans2)
            sys.exit(1)
        passed += 1
    print(f"All {passed} tests passed.")
    return passed

if __name__ == "__main__":
    total = run_tests(200)
    verdict = {"verified": True, "tests_run": total, "tests_passed": total}
    with open("verdict.json", "w") as f:
        json.dump(verdict, f)
