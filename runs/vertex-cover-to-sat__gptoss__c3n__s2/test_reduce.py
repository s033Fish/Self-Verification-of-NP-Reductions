import itertools
import json
import random
from problems import VertexCover, Sat
from reduce import reduce


def vertex_cover_bruteforce(instance):
    n = instance['n']
    edges = instance['edges']
    k = instance['k']
    if k < 0:
        return False
    # any subset of vertices up to k
    for r in range(k+1):
        for subset in itertools.combinations(range(n), r):
            covered = True
            for u,v in edges:
                if u not in subset and v not in subset:
                    covered = False
                    break
            if covered:
                return True
    return False

def sat_bruteforce(instance):
    m = instance['num_vars']
    clauses = instance['clauses']
    # empty clause -> unsat
    for clause in clauses:
        if not clause:
            return False
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
    return True if not clauses else False


def test_random(num_tests=200):
    for _ in range(num_tests):
        n = random.randint(0,5)
        # generate random edges without duplicates
        possible = [(i,j) for i in range(n) for j in range(i+1,n)]
        edges = []
        for (i,j) in possible:
            if random.random() < 0.3:
                edges.append([i,j])
        k = random.randint(-1, n+1)
        vc_instance = {"n": n, "edges": edges, "k": k}
        VertexCover.validate(vc_instance)
        sat_instance = reduce(vc_instance)
        # compare answers
        vc_ans = vertex_cover_bruteforce(vc_instance)
        sat_ans = sat_bruteforce(sat_instance)
        if vc_ans != sat_ans:
            print('Mismatch!')
            print('VC instance', vc_instance)
            print('SAT instance', sat_instance)
            print('VC ans', vc_ans, 'SAT ans', sat_ans)
            return False
    return True

if __name__ == '__main__':
    ok = test_random(500)
    print('All tests passed' if ok else 'Some tests failed')
