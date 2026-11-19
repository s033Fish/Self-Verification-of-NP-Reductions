import itertools
import random
import json
from problems import Clique, Sat
from reduce import reduce


def solve_clique(instance):
    n = instance["n"]
    edges = set()
    for u, v in instance["edges"]:
        edges.add(frozenset((u, v)))
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
            if all(frozenset((u, v)) in edges for u, v in itertools.combinations(subset, 2)):
                return True
    return False


def solve_sat(instance):
    m = instance["num_vars"]
    clauses = instance["clauses"]
    for clause in clauses:
        if len(clause) == 0:
            return False
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


def random_instance(max_n=4, max_k=2):
    """Generate a small random Clique instance suitable for brute‑force SAT."""
    n = random.randint(0, max_n)
    possible = [(i, j) for i in range(n) for j in range(i + 1, n)]
    edges = []
    for u, v in possible:
        if random.choice([True, False]):
            edges.append([u, v])
    k = random.randint(-1, max(n, max_k) + 1)
    return {"n": n, "edges": edges, "k": k}


def run_tests(num=200):
    passed = 0
    for _ in range(num):
        inst = random_instance()
        Clique.validate(inst)
        sat_inst = reduce(inst)
        Sat.validate(sat_inst)
        ans1 = solve_clique(inst)
        ans2 = solve_sat(sat_inst)
        if ans1 == ans2:
            passed += 1
        else:
            print("Mismatch!", inst, sat_inst, ans1, ans2)
            break
    return num, passed

if __name__ == "__main__":
    total, ok = run_tests(200)
    verdict = {"verified": ok == total, "tests_run": total, "tests_passed": ok}
    print(json.dumps(verdict))
    with open("verdict.json", "w") as f:
        json.dump(verdict, f)
