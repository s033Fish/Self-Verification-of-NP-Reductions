import itertools
import random
import sys

from problems import DominatingSet, Sat
from reduce import reduce

def dominating_set_bruteforce(instance):
    n = instance['n']
    edges = instance['edges']
    k = instance['k']
    # adjacency
    neigh = [set() for _ in range(n)]
    for u, v in edges:
        neigh[u].add(v)
        neigh[v].add(u)
    # check all subsets of size <= k
    for r in range(k+1):
        for subset in itertools.combinations(range(n), r):
            D = set(subset)
            # every vertex either in D or adjacent to D
            ok = True
            for v in range(n):
                if v not in D and not (neigh[v] & D):
                    ok = False
                    break
            if ok:
                return True
    return False

def sat_bruteforce(instance):
    m = instance['num_vars']
    clauses = instance['clauses']
    # empty clause -> unsat
    for c in clauses:
        if len(c) == 0:
            return False
    for bits in range(1 << m):
        assignment = [(bits >> i) & 1 == 1 for i in range(m)]  # var i+1
        satisfied = True
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
    for (i, j) in possible:
        if random.random() < 0.3:
            edges.append([i, j])
    k = random.randint(-1, n+1)
    return {"n": n, "edges": edges, "k": k}


def main():
    random.seed(0)
    total = 0
    passed = 0
    for _ in range(200):
        inst = random_instance()
        # validate
        DominatingSet.validate(inst)
        # compute answers
        ans_src = dominating_set_bruteforce(inst)
        red = reduce(inst)
        Sat.validate(red)
        ans_tgt = sat_bruteforce(red)
        total += 1
        if ans_src == ans_tgt:
            passed += 1
        else:
            print('Mismatch!')
            print('src', inst, ans_src)
            print('red', red, ans_tgt)
            sys.exit(1)
    print('All tests passed', passed, '/', total)
    # write verdict
    import json
    verdict = {"verified": True, "tests_run": total, "tests_passed": passed}
    with open('verdict.json', 'w') as f:
        json.dump(verdict, f)

if __name__ == '__main__':
    main()
