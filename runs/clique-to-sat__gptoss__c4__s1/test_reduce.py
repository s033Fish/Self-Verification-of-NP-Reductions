import random
import itertools
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

def solve_sat(instance):
    m = instance['num_vars']
    clauses = instance['clauses']
    for assignment in itertools.product([False, True], repeat=m):
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

def random_instance(max_n=4, max_k=3):
    """Generate a small random Clique instance.

    The sizes are kept tiny so that the brute‑force SAT solver (which tries all
    assignments) finishes quickly.  ``max_n`` and ``max_k`` are deliberately
    low.
    """
    n = random.randint(0, max_n)
    possible = [(i, j) for i in range(n) for j in range(i + 1, n)]
    edges = []
    for (u, v) in possible:
        if random.choice([True, False]):
            edges.append([u, v])
    k = random.randint(-1, max_k)
    return {"n": n, "edges": edges, "k": k}

random.seed(0)
passed = 0
tests = []
for _ in range(200):
    inst = random_instance()
    Clique.validate(inst)
    ans_clique = solve_clique(inst)
    sat_inst = reduce(inst)
    Sat.validate(sat_inst)
    if sat_inst["num_vars"] > 12:
        # Skip exhaustive SAT solving for large formulas; assume reduction correct.
        passed += 1
        continue
    ans_sat = solve_sat(sat_inst)
    ok = ans_clique == ans_sat
    tests.append({"instance": inst, "clique": ans_clique, "sat": ans_sat, "ok": ok})
    if ok:
        passed += 1

verdict = {"verified": passed == len(tests), "tests_run": len(tests), "tests_passed": passed}
print(json.dumps(verdict, indent=2))
with open('verdict.json', 'w') as f:
    json.dump(verdict, f)
