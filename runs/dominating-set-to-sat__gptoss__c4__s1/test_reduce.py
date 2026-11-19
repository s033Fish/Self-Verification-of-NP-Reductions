import random
import itertools
import json
import sys
from problems import DominatingSet, Sat
from reduce import reduce


def solve_dominating_set(inst):
    n = inst["n"]
    edges = inst["edges"]
    k = inst["k"]
    # Edge cases
    if k < 0:
        return False
    if n == 0:
        return True
    if k >= n:
        return True
    # adjacency
    adj = [set() for _ in range(n)]
    for u, v in edges:
        adj[u].add(v)
        adj[v].add(u)
    # check all subsets up to size k
    vertices = list(range(n))
    for r in range(k + 1):
        for subset in itertools.combinations(vertices, r):
            D = set(subset)
            ok = True
            for v in vertices:
                if v not in D and not (adj[v] & D):
                    ok = False
                    break
            if ok:
                return True
    return False


def solve_sat(inst):
    m = inst["num_vars"]
    clauses = inst["clauses"]
    # any empty clause -> unsat
    for cl in clauses:
        if len(cl) == 0:
            return False
    # iterate assignments
    for bits in range(1 << m):
        assign = [(bits >> i) & 1 == 1 for i in range(m)]  # index 0 -> var1
        good = True
        for cl in clauses:
            sat = False
            for lit in cl:
                var = abs(lit) - 1
                val = assign[var]
                if lit > 0 and val:
                    sat = True
                    break
                if lit < 0 and not val:
                    sat = True
                    break
            if not sat:
                good = False
                break
        if good:
            return True
    return False


def random_instance(max_n=5):
    n = random.randint(0, max_n)
    # generate random edges without duplicates
    possible = [(i, j) for i in range(n) for j in range(i+1, n)]
    edges = []
    for (u, v) in possible:
        if random.random() < 0.3:
            edges.append([u, v])
    k = random.randint(-1, n+1)
    return {"n": n, "edges": edges, "k": k}


def main():
    random.seed(0)
    tests = 200
    passed = 0
    for _ in range(tests):
        inst = random_instance()
        # validate
        DominatingSet.validate(inst)
        sat_inst = reduce(inst)
        Sat.validate(sat_inst)
        ans1 = solve_dominating_set(inst)
        ans2 = solve_sat(sat_inst)
        if ans1 == ans2:
            passed += 1
        else:
            print("Mismatch!", inst, sat_inst, ans1, ans2)
            sys.exit(1)
    verdict = {"verified": True, "tests_run": tests, "tests_passed": passed}
    with open('verdict.json', 'w') as f:
        json.dump(verdict, f)
    print(json.dumps(verdict))

if __name__ == '__main__':
    main()
