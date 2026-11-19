import itertools
import random
import json
import sys
from problems import ThreeSat, Clique
from reduce import reduce


def solve_3sat(instance):
    m = instance["num_vars"]
    clauses = instance["clauses"]
    if not clauses:
        return True
    for bits in range(1 << m):
        assignment = [(bits >> i) & 1 == 1 for i in range(m)]
        ok = True
        for clause in clauses:
            clause_ok = False
            for lit in clause:
                var = abs(lit) - 1
                val = assignment[var]
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


def solve_clique(instance):
    n = instance["n"]
    edges_set = {frozenset(e) for e in instance["edges"]}
    k = instance["k"]
    if k <= 0:
        return True
    if k == 1:
        return n >= 1
    if k > n:
        return False
    vertices = list(range(n))
    for size in range(k, n + 1):
        for subset in itertools.combinations(vertices, size):
            good = True
            for u, v in itertools.combinations(subset, 2):
                if frozenset((u, v)) not in edges_set:
                    good = False
                    break
            if good:
                return True
    return False


def random_three_sat(max_vars=5, max_clauses=5):
    """Generate a valid random 3‑SAT instance respecting the spec."""
    num_clauses = random.randint(0, max_clauses)
    if num_clauses == 0:
        m = random.randint(0, max_vars)
        return {"num_vars": m, "clauses": []}
    # ensure at least 3 vars when clauses exist
    m = random.randint(3, max_vars)
    clauses = []
    for _ in range(num_clauses):
        vars_pool = list(range(1, m + 1))
        chosen = random.sample(vars_pool, 3)
        clause = []
        for v in chosen:
            lit = v if random.choice([True, False]) else -v
            clause.append(lit)
        clauses.append(clause)
    return {"num_vars": m, "clauses": clauses}


def run_tests(num_tests=500):
    passed = 0
    for _ in range(num_tests):
        inst = random_three_sat()
        # validate source
        ThreeSat.validate(inst)
        reduced = reduce(inst)
        Clique.validate(reduced)
        ans_src = solve_3sat(inst)
        ans_tgt = solve_clique(reduced)
        if ans_src == ans_tgt:
            passed += 1
        else:
            print("Mismatch!", inst, reduced, ans_src, ans_tgt)
            return False, passed
    return True, passed

if __name__ == "__main__":
    ok, passed = run_tests()
    result = {"verified": ok, "tests_run": 500, "tests_passed": passed}
    print(json.dumps(result, indent=2))
    with open('verdict.json', 'w') as f:
        json.dump(result, f)
    sys.exit(0 if ok else 1)
