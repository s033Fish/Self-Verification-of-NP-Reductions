import itertools
import random
import json
from problems import VertexCover, IndependentSet
from reduce import reduce

def brute_vertex_cover(instance):
    n = instance['n']
    edges = [tuple(e) for e in instance['edges']]
    k = instance['k']
    if k < 0:
        return False
    # trivial yes cases
    if not edges:
        return True
    if k >= n:
        return True
    # check all subsets up to size k
    vertices = list(range(n))
    for r in range(k+1):
        for subset in itertools.combinations(vertices, r):
            covered = True
            subset_set = set(subset)
            for u,v in edges:
                if u not in subset_set and v not in subset_set:
                    covered = False
                    break
            if covered:
                return True
    return False

def brute_independent_set(instance):
    n = instance['n']
    edges = {frozenset(e) for e in instance['edges']}
    k = instance['k']
    if k <= 0:
        return True
    if k > n:
        return False
    vertices = list(range(n))
    # check subsets of size >= k
    for r in range(k, n+1):
        for subset in itertools.combinations(vertices, r):
            ok = True
            subset_set = set(subset)
            for u,v in edges:
                if u in subset_set and v in subset_set:
                    ok = False
                    break
            if ok:
                return True
    return False

def random_instance(n, edge_prob=0.3, k_range=(-2, None)):
    edges = []
    for i in range(n):
        for j in range(i+1, n):
            if random.random() < edge_prob:
                edges.append([i,j])
    if k_range[1] is None:
        maxk = n
    else:
        maxk = k_range[1]
    k = random.randint(k_range[0], maxk)
    return {"n": n, "edges": edges, "k": k}

def run_tests(num=200):
    passed = 0
    for _ in range(num):
        n = random.randint(0,5)
        inst = random_instance(n)
        # validate source
        VertexCover.validate(inst)
        # compute answers
        ans_src = brute_vertex_cover(inst)
        red = reduce(inst)
        IndependentSet.validate(red)
        ans_tgt = brute_independent_set(red)
        if ans_src == ans_tgt:
            passed += 1
        else:
            print('FAIL')
            print('src', inst, ans_src)
            print('red', red, ans_tgt)
            break
    return passed, num

if __name__ == '__main__':
    passed, total = run_tests(500)
    print(f"{passed}/{total} tests passed")
    import json, os
    verdict = {"verified": passed==total, "tests_run": total, "tests_passed": passed}
    with open('verdict.json','w') as f:
        json.dump(verdict, f)
    print('verdict written')
