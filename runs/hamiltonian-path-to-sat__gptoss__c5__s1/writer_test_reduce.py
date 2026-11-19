import itertools
import random
import json
from problems import HamiltonianPath, Sat
from reduce import reduce

def solve_hamiltonian_path(instance):
    n = instance["n"]
    edges = set(frozenset(e) for e in instance["edges"])
    if n == 0:
        return False
    if n == 1:
        return True
    for perm in itertools.permutations(range(n)):
        ok = True
        for i in range(n-1):
            if frozenset((perm[i], perm[i+1])) not in edges:
                ok = False
                break
        if ok:
            return True
    return False

def solve_sat(instance):
    m = instance["num_vars"]
    clauses = instance["clauses"]
    for cl in clauses:
        if len(cl) == 0:
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

def random_graph(n, p=0.5):
    edges = []
    for u in range(n):
        for v in range(u+1, n):
            if random.random() < p:
                edges.append([u, v])
    return {"n": n, "edges": edges}

def run_tests():
    total = 0
    passed = 0
    cases = [
        {"n": 0, "edges": []},
        {"n": 1, "edges": []},
        {"n": 2, "edges": []},
        {"n": 2, "edges": [[0,1]]},
    ]
    # random small graphs up to n=4 (larger n would make brute-force SAT too slow)
    for n in range(0,5):
        for _ in range(10):
            cases.append(random_graph(n, p=0.4))
    for case in cases:
        total += 1
        HamiltonianPath.validate(case)
        hp_ans = solve_hamiltonian_path(case)
        sat_inst = reduce(case)
        sat_ans = solve_sat(sat_inst)
        if hp_ans == sat_ans:
            passed += 1
        else:
            print("Mismatch!", case, hp_ans, sat_ans)
    return total, passed

if __name__ == "__main__":
    total, passed = run_tests()
    verdict = {"verified": passed == total, "tests_run": total, "tests_passed": passed}
    print(json.dumps(verdict))
    with open('verdict.json', 'w') as f:
        json.dump(verdict, f)
