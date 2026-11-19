import itertools
import json
import random
import sys
from typing import List, Dict

# Import the reduction
from reduce import reduce

# Brute-force solver for Dominating Set
def dominating_set_bruteforce(instance: Dict) -> bool:
    n = instance["n"]
    edges = instance["edges"]
    k = instance["k"]
    if k < 0:
        return False
    if n == 0:
        return True
    if k >= n:
        return True
    # adjacency list
    adj = [set() for _ in range(n)]
    for u, v in edges:
        adj[u].add(v)
        adj[v].add(u)
    # check all subsets up to size k
    vertices = list(range(n))
    for r in range(k + 1):
        for combo in itertools.combinations(vertices, r):
            D = set(combo)
            ok = True
            for v in range(n):
                if v not in D and not (adj[v] & D):
                    ok = False
                    break
            if ok:
                return True
    return False

# Brute-force SAT solver
def sat_bruteforce(instance: Dict) -> bool:
    m = instance["num_vars"]
    clauses = instance["clauses"]
    # empty clause -> unsat
    for clause in clauses:
        if len(clause) == 0:
            return False
    # iterate assignments
    for bits in itertools.product([False, True], repeat=m):
        assign = {i+1: bits[i] for i in range(m)}
        satisfied = True
        for clause in clauses:
            clause_sat = False
            for lit in clause:
                var = abs(lit)
                val = assign[var]
                if lit > 0 and val:
                    clause_sat = True
                    break
                if lit < 0 and not val:
                    clause_sat = True
                    break
            if not clause_sat:
                satisfied = False
                break
        if satisfied:
            return True
    return False

def random_instance(max_n=5):
    n = random.randint(0, max_n)
    # generate random edges without duplicates
    possible = [(i, j) for i in range(n) for j in range(i+1, n)]
    edges = []
    for (u, v) in possible:
        if random.choice([True, False]):
            edges.append([u, v])
    k = random.randint(-1, n+1)
    return {"n": n, "edges": edges, "k": k}


def main():
    tests = 200
    passed = 0
    for _ in range(tests):
        inst = random_instance()
        # reduce
        sat_inst = reduce(inst)
        ds_ans = dominating_set_bruteforce(inst)
        sat_ans = sat_bruteforce(sat_inst)
        if ds_ans == sat_ans:
            passed += 1
        else:
            print("Mismatch!", inst, sat_inst, ds_ans, sat_ans)
            sys.exit(1)
    print(f"All {passed}/{tests} tests passed")
    # write verdict
    verdict = {"verified": True, "tests_run": tests, "tests_passed": passed}
    with open('verdict.json', 'w') as f:
        json.dump(verdict, f)

if __name__ == '__main__':
    main()
