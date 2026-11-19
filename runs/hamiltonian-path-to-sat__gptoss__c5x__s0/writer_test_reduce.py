import itertools
import random
import json
from problems import HamiltonianPath, Sat
from reduce import reduce

def hamiltonian_path_bruteforce(instance):
    n = instance['n']
    edges = set(frozenset(e) for e in instance['edges'])
    if n == 0:
        return False
    if n == 1:
        return True
    # generate all permutations of vertices
    for perm in itertools.permutations(range(n)):
        ok = True
        for i in range(n-1):
            if frozenset((perm[i], perm[i+1])) not in edges:
                ok = False
                break
        if ok:
            return True
    return False

def sat_bruteforce(instance):
    m = instance['num_vars']
    clauses = instance['clauses']
    # any empty clause -> unsat
    for c in clauses:
        if len(c) == 0:
            return False
    for assignment in itertools.product([False, True], repeat=m):
        ok = True
        for clause in clauses:
            clause_sat = False
            for lit in clause:
                var = abs(lit) - 1
                val = assignment[var]
                if lit > 0 and val:
                    clause_sat = True
                    break
                if lit < 0 and not val:
                    clause_sat = True
                    break
            if not clause_sat:
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

def run_tests(num_cases=200):
    passed = 0
    for _ in range(num_cases):
        n = random.randint(0,4)
        inst = random_graph(n, p=0.5)
        # validate
        HamiltonianPath.validate(inst)
        # compute answers
        ans_src = hamiltonian_path_bruteforce(inst)
        red = reduce(inst)
        Sat.validate(red)
        ans_tgt = sat_bruteforce(red)
        if ans_src == ans_tgt:
            passed += 1
        else:
            print('FAIL')
            print('src', inst, ans_src)
            print('red', red, ans_tgt)
            break
    return passed, num_cases

if __name__ == '__main__':
    passed, total = run_tests(200)
    print(f"Passed {passed}/{total} tests")
    verdict = {"verified": passed==total, "tests_run": total, "tests_passed": passed}
    with open('verdict.json', 'w') as f:
        json.dump(verdict, f)
