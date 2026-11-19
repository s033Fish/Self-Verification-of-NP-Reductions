import itertools
import random
import json
from problems import Clique, Sat
from reduce import reduce

def solve_clique(instance):
    n = instance['n']
    edges = set(frozenset(e) for e in instance['edges'])
    k = instance['k']
    if k <= 0:
        return True
    if k == 1:
        return n >= 1
    if k > n:
        return False
    # check subsets of size >= k
    for size in range(k, n + 1):
        for subset in itertools.combinations(range(n), size):
            if all(frozenset((u, v)) in edges for u, v in itertools.combinations(subset, 2)):
                return True
    return False

def solve_sat(instance):
    m = instance['num_vars']
    clauses = instance['clauses']
    # empty clause -> unsat
    for cl in clauses:
        if len(cl) == 0:
            return False
    # no clauses -> sat
    for assign in itertools.product([False, True], repeat=m):
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

def random_clique_instance(max_n=4):
    """Generate a small random Clique instance.
+
+    Limits are chosen so that the SAT instance stays small enough for the
+    brute‑force solver.
+    """
    n = random.randint(0, max_n)
    possible = [(i, j) for i in range(n) for j in range(i + 1, n)]
    edges = []
    for (i, j) in possible:
        if random.choice([True, False]):
            edges.append([i, j])
    max_k = min(4, n + 2)
    k = random.randint(-1, max_k)
    return {"n": n, "edges": edges, "k": k}

def run_tests(num_tests=200):
    passed = 0
    for _ in range(num_tests):
        inst = random_clique_instance()
        Clique.validate(inst)
        ans1 = solve_clique(inst)
        sat_inst = reduce(inst)
        Sat.validate(sat_inst)
        ans2 = solve_sat(sat_inst)
        if ans1 == ans2:
            passed += 1
        else:
            print('Mismatch!')
            print('Clique instance:', json.dumps(inst, indent=2))
            print('Clique answer:', ans1)
            print('SAT instance:', json.dumps(sat_inst, indent=2))
            print('SAT answer:', ans2)
            break
    return passed, num_tests

if __name__ == '__main__':
    passed, total = run_tests()
    verified = passed == total
    verdict = {"verified": verified, "tests_run": total, "tests_passed": passed}
    print(json.dumps(verdict, indent=2))
    with open('verdict.json', 'w') as f:
        json.dump(verdict, f)
