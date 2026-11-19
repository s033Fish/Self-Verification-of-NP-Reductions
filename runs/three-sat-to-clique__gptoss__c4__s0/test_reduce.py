import itertools
import random
import json
import sys
from pathlib import Path

# Import the reduction
from reduce import reduce as reduce_fn

# Import problem validators (optional)
from problems import ThreeSat, Clique


def solve_three_sat(instance):
    m = instance["num_vars"]
    clauses = instance["clauses"]
    # iterate all assignments 0/1 for variables 1..m
    for bits in itertools.product([False, True], repeat=m):
        assignment = {i+1: bits[i] for i in range(m)}
        ok = True
        for clause in clauses:
            clause_ok = False
            for lit in clause:
                var = abs(lit)
                val = assignment[var]
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


def solve_clique(instance):
    n = instance["n"]
    edges = set()
    for u, v in instance["edges"]:
        if u > v:
            u, v = v, u
        edges.add((u, v))
    k = instance["k"]
    if k <= 0:
        return True
    if k == 1:
        return n >= 1
    if k > n:
        return False
    # check all subsets of size k (since we only need at least k, we can check exactly k)
    for subset in itertools.combinations(range(n), k):
        good = True
        for i in range(k):
            for j in range(i+1, k):
                u, v = subset[i], subset[j]
                if u > v:
                    u, v = v, u
                if (u, v) not in edges:
                    good = False
                    break
            if not good:
                break
        if good:
            return True
    # also need to consider larger cliques, but if no clique of size k, larger also not exist
    return False


def random_three_sat(max_vars=4, max_clauses=4):
    m = random.randint(0, max_vars)
    # ensure at least 3 vars if there are clauses, per spec
    if m < 3:
        m = 3
    c = random.randint(0, max_clauses)
    clauses = []
    for _ in range(c):
        # pick 3 distinct variables from 1..m
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
        inst = random_three_sat()
        # validate using problem classes (may raise)
        try:
            ThreeSat.validate(inst)
        except Exception as e:
            print("Invalid generated instance", inst, e)
            continue
        sat = solve_three_sat(inst)
        red = reduce_fn(inst)
        # validate target instance
        Clique.validate(red)
        clique_ans = solve_clique(red)
        if sat == clique_ans:
            passed += 1
        else:
            print("Mismatch!", json.dumps(inst), json.dumps(red), sat, clique_ans)
            return passed, False
    return passed, True

if __name__ == "__main__":
    total, ok = run_tests(300)
    result = {
        "verified": ok,
        "tests_run": 300,
        "tests_passed": total,
    }
    Path("verdict.json").write_text(json.dumps(result, indent=2))
    print(json.dumps(result, indent=2))
    sys.exit(0 if ok else 1)

