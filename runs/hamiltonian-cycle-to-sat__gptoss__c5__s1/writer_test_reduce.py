import itertools
import json
import random
import sys
from pathlib import Path

sys.path.append(str(Path('.').resolve()))
from problems import HamiltonianCycle, Sat
from reduce import reduce


def solve_hamiltonian(instance):
    n = instance["n"]
    edges = set()
    for u, v in instance["edges"]:
        edges.add((u, v))
        edges.add((v, u))
    if n <= 2:
        return False
    for perm in itertools.permutations(range(n)):
        ok = True
        for i in range(n):
            u = perm[i]
            v = perm[(i + 1) % n]
            if (u, v) not in edges:
                ok = False
                break
        if ok:
            return True
    return False


def solve_sat(instance):
    m = instance["num_vars"]
    clauses = instance["clauses"]
    for assign in range(1 << m):
        ok = True
        for clause in clauses:
            clause_ok = False
            for lit in clause:
                var = abs(lit) - 1
                val = (assign >> var) & 1
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


def random_graph(max_n=4, edge_prob=0.5):
    # Limit max_n to keep SAT instance size manageable.
    n = random.randint(0, max_n)
    edges = []
    for u in range(n):
        for v in range(u + 1, n):
            if random.random() < edge_prob:
                edges.append([u, v])
    return {"n": n, "edges": edges}


def run_tests(num=200):
    passed = 0
    for _ in range(num):
        g = random_graph()
        HamiltonianCycle.validate(g)
        sat_instance = reduce(g)
        Sat.validate(sat_instance)
        ans_h = solve_hamiltonian(g)
        ans_s = solve_sat(sat_instance)
        if ans_h == ans_s:
            passed += 1
        else:
            print("Mismatch!", g, ans_h, ans_s)
            break
    return num, passed

if __name__ == "__main__":
    total, passed = run_tests(200)
    verdict = {"verified": passed == total, "tests_run": total, "tests_passed": passed}
    print(json.dumps(verdict, indent=2))
    Path("verdict.json").write_text(json.dumps(verdict))
