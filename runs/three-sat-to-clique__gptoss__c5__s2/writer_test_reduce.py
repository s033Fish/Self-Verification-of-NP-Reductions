import itertools
import random
import json
from problems import SOURCE, TARGET
from reduce import reduce
from typing import List

def solve_3sat(instance):
    m = instance["num_vars"]
    clauses = instance["clauses"]
    for mask in range(1 << m):
        ok = True
        for clause in clauses:
            clause_ok = False
            for lit in clause:
                var = abs(lit) - 1
                val = (mask >> var) & 1
                if lit > 0 and val == 1:
                    clause_ok = True
                    break
                if lit < 0 and val == 0:
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
    edges_set = set()
    for u, v in instance["edges"]:
        if u > v:
            u, v = v, u
        edges_set.add((u, v))
    k = instance["k"]
    if k <= 0:
        return True
    if k == 1:
        return n >= 1
    if k > n:
        return False
    for subset in itertools.combinations(range(n), k):
        good = True
        for i in range(k):
            for j in range(i + 1, k):
                a, b = subset[i], subset[j]
                if a > b:
                    a, b = b, a
                if (a, b) not in edges_set:
                    good = False
                    break
            if not good:
                break
        if good:
            return True
    return False

def random_3sat_instance(max_vars=4, max_clauses=4):
    """Generate a random, valid 3‑SAT instance.
    Ensures variables in clauses are within 1..num_vars and each clause has three distinct vars.
    """
    num_clauses = random.randint(0, max_clauses)
    if num_clauses == 0:
        m = random.randint(0, max_vars)
    else:
        m = random.randint(3, max_vars)
    clauses: List[List[int]] = []
    for _ in range(num_clauses):
        chosen = random.sample(range(1, m + 1), 3)
        clause = []
        for v in chosen:
            lit = v if random.choice([True, False]) else -v
            clause.append(lit)
        clauses.append(clause)
    return {"num_vars": m, "clauses": clauses}

def run_tests(num_trials=200):
    for _ in range(num_trials):
        inst = random_3sat_instance()
        SOURCE.validate(inst)
        reduced = reduce(inst)
        TARGET.validate(reduced)
        ans_src = solve_3sat(inst)
        ans_tgt = solve_clique(reduced)
        if ans_src != ans_tgt:
            print("Mismatch!", inst, reduced, ans_src, ans_tgt)
            return False
    edge_cases = [
        {"num_vars": 0, "clauses": []},
        {"num_vars": 5, "clauses": []},
    ]
    for inst in edge_cases:
        SOURCE.validate(inst)
        reduced = reduce(inst)
        TARGET.validate(reduced)
        if not solve_3sat(inst) or not solve_clique(reduced):
            print("Edge case failed", inst, reduced)
            return False
    return True

if __name__ == "__main__":
    ok = run_tests()
    verdict = {"verified": ok, "tests_run": 200 + 2, "tests_passed": (200 + 2) if ok else 0}
    print(json.dumps(verdict))
    with open("verdict.json", "w") as f:
        json.dump(verdict, f)
