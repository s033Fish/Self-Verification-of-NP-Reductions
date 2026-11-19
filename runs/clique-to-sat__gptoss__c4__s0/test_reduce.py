import itertools
import random
import json
from typing import Dict
import problems
from reduce import reduce

# Brute-force Clique solver

def clique_yes(instance: Dict) -> bool:
    n = instance["n"]
    edges = set(frozenset(e) for e in instance["edges"])
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
            ok = True
            for u, v in itertools.combinations(subset, 2):
                if frozenset((u, v)) not in edges:
                    ok = False
                    break
            if ok:
                return True
    return False

# Brute-force SAT solver

def sat_yes(instance: Dict) -> bool:
    m = instance["num_vars"]
    clauses = instance["clauses"]
    for clause in clauses:
        if len(clause) == 0:
            return False
    for bits in range(1 << m):
        assign = [(bits >> i) & 1 == 1 for i in range(m)]
        ok = True
        for clause in clauses:
            clause_ok = False
            for lit in clause:
                var = abs(lit) - 1
                val = assign[var]
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


def run_tests(num_trials=200):
    passed = 0
    total = 0
    for _ in range(num_trials):
        # small graphs for brute force speed
        n = random.randint(0, 4)
        possible = [(i, j) for i in range(n) for j in range(i + 1, n)]
        edges = []
        for (i, j) in possible:
            if random.choice([True, False]):
                edges.append([i, j])
        k = random.randint(-1, n + 2)
        cli = {"n": n, "edges": edges, "k": k}
        try:
            problems.Clique.validate(cli)
        except Exception as e:
            print("Invalid clique instance", cli, e)
            continue
        sat_inst = reduce(cli)
        problems.Sat.validate(sat_inst)
        c = clique_yes(cli)
        s = sat_yes(sat_inst)
        total += 1
        if c == s:
            passed += 1
        else:
            print("Mismatch!", cli, "->", sat_inst, c, s)
            break
    # deterministic edge cases
    edge_cases = [
        {"n": 0, "edges": [], "k": 0},
        {"n": 1, "edges": [], "k": 1},
        {"n": 1, "edges": [], "k": 2},
        {"n": 3, "edges": [[0,1],[1,2],[0,2]], "k": 3},
        {"n": 3, "edges": [[0,1],[1,2]], "k": 3},
    ]
    for ci in edge_cases:
        problems.Clique.validate(ci)
        si = reduce(ci)
        problems.Sat.validate(si)
        total += 1
        if clique_yes(ci) == sat_yes(si):
            passed += 1
        else:
            print("Edge case mismatch", ci, si)
            break
    return passed, total

if __name__ == "__main__":
    passed, total = run_tests()
    result = {"verified": passed == total, "tests_run": total, "tests_passed": passed}
    print(json.dumps(result, indent=2))
    with open("verdict.json", "w") as f:
        json.dump(result, f)
