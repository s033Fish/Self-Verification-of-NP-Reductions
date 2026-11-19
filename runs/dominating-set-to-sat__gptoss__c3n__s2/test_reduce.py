import random
import itertools
import json
from problems import DominatingSet, Sat
from reduce import reduce


def dominating_set_bruteforce(instance):
    n = instance['n']
    edges = instance['edges']
    k = instance['k']
    # Edge cases per definition
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
    # check all subsets of size <= k
    vertices = list(range(n))
    for r in range(k+1):
        for subset in itertools.combinations(vertices, r):
            D = set(subset)
            # verify domination
            ok = True
            for v in range(n):
                if v in D:
                    continue
                if not (adj[v] & D):
                    ok = False
                    break
            if ok:
                return True
    return False


def sat_bruteforce(instance):
    m = instance['num_vars']
    clauses = instance['clauses']
    # empty clause => unsat
    for clause in clauses:
        if len(clause) == 0:
            return False
    # try all assignments
    for bits in range(1 << m):
        assignment = [(bits >> i) & 1 == 1 for i in range(m)]  # index 0 -> var1
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


def run_tests(num_tests=200):
    passed = 0
    for _ in range(num_tests):
        n = random.randint(0, 5)
        # generate random edges without duplicates
        possible = [(i, j) for i in range(n) for j in range(i+1, n)]
        edges = []
        for (u, v) in possible:
            if random.random() < 0.3:
                edges.append([u, v])
        k = random.randint(-1, n+1)
        src = {'n': n, 'edges': edges, 'k': k}
        # validate source
        DominatingSet.validate(src)
        src_ans = dominating_set_bruteforce(src)
        red = reduce(src)
        Sat.validate(red)
        tgt_ans = sat_bruteforce(red)
        if src_ans == tgt_ans:
            passed += 1
        else:
            print('Mismatch!')
            print('src', src, 'src_ans', src_ans)
            print('red', red, 'tgt_ans', tgt_ans)
            break
    return passed, num_tests

if __name__ == '__main__':
    passed, total = run_tests(500)
    verdict = {
        'verified': passed == total,
        'tests_run': total,
        'tests_passed': passed,
    }
    print(json.dumps(verdict, indent=2))
    with open('verdict.json', 'w') as f:
        json.dump(verdict, f)
