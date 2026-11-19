import itertools
import random
import sys
import json
from problems import VertexCover, IndependentSet
from reduce import reduce

def vc_bruteforce(instance):
    n = instance['n']
    edges = instance['edges']
    k = instance['k']
    # Edge cases per definition
    if k < 0:
        return False
    if k >= n:
        return True
    if not edges:
        return True  # empty set covers any k>=0, already handled
    # Check all subsets up to size k
    vertices = list(range(n))
    for r in range(k+1):
        for subset in itertools.combinations(vertices, r):
            covered = True
            for u,v in edges:
                if u not in subset and v not in subset:
                    covered = False
                    break
            if covered:
                return True
    return False

def is_independent_set(instance, subset):
    edges = set(frozenset(e) for e in instance['edges'])
    for u,v in itertools.combinations(subset, 2):
        if frozenset((u,v)) in edges:
            return False
    return True

def is_solver(instance):
    n = instance['n']
    k = instance['k']
    if k <= 0:
        return True
    if k > n:
        return False
    if not instance['edges']:
        return True
    # brute force check any subset of size >=k that is independent
    vertices = list(range(n))
    for r in range(k, n+1):
        for subset in itertools.combinations(vertices, r):
            if is_independent_set(instance, subset):
                return True
    return False

def run_random_tests(num_tests=200):
    for _ in range(num_tests):
        n = random.randint(0,6)  # small for brute force
        # generate random edges without duplicates or self loops
        possible = [(i,j) for i in range(n) for j in range(i+1,n)]
        edges = []
        for (i,j) in possible:
            if random.random() < 0.3:
                edges.append([i,j])
        k = random.randint(-2, n+2)
        vc_instance = {'n': n, 'edges': edges, 'k': k}
        # validate
        try:
            VertexCover.validate(vc_instance)
        except Exception as e:
            print('Invalid VC instance generated', vc_instance, e)
            continue
        # reduction
        ind_instance = reduce(vc_instance)
        # validate target
        IndependentSet.validate(ind_instance)
        # compare answers
        vc_ans = vc_bruteforce(vc_instance)
        ind_ans = is_solver(ind_instance)
        # According to reduction, answers should be equal
        if vc_ans != ind_ans:
            print('Mismatch!')
            print('VC instance', vc_instance, 'ans', vc_ans)
            print('Reduced instance', ind_instance, 'ans', ind_ans)
            return False
    return True

if __name__ == '__main__':
    ok = run_random_tests(500)
    print('All tests passed' if ok else 'Some tests failed')
    sys.exit(0 if ok else 1)
