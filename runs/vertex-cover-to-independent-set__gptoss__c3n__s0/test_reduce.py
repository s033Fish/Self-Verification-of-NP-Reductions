import random
import itertools
import sys
from problems import VertexCover, IndependentSet
from reduce import reduce

def solve_vertex_cover(inst):
    n = inst['n']
    edges = inst['edges']
    k = inst['k']
    # Edge cases per definition
    if k < 0:
        return False
    if k >= n:
        return True
    if not edges:
        return True  # empty set covers
    # brute force subsets up to size k
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

def solve_independent_set(inst):
    n = inst['n']
    edges = inst['edges']
    k = inst['k']
    if k <= 0:
        return True
    if k > n:
        return False
    if not edges:
        return True
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

def random_instance(max_n=6, edge_prob=0.3):
    n = random.randint(0, max_n)
    edges = []
    seen = set()
    for u in range(n):
        for v in range(u+1, n):
            if random.random() < edge_prob:
                edges.append([u, v])
                seen.add((u,v))
    k = random.randint(-1, n+1)  # allow some out of range
    return {"n": n, "edges": edges, "k": k}

def main():
    tests = 200
    passed = 0
    for i in range(tests):
        inst = random_instance()
        # validate source
        try:
            VertexCover.validate(inst)
        except Exception as e:
            print('Invalid source instance generated', e)
            sys.exit(1)
        ans_vc = solve_vertex_cover(inst)
        red = reduce(inst)
        # validate target
        try:
            IndependentSet.validate(red)
        except Exception as e:
            print('Invalid reduced instance', e)
            sys.exit(1)
        ans_is = solve_independent_set(red)
        if ans_vc == ans_is:
            passed += 1
        else:
            print('Mismatch!')
            print('Source:', inst, 'vc answer', ans_vc)
            print('Reduced:', red, 'is answer', ans_is)
            sys.exit(1)
    print(f'All {passed}/{tests} tests passed')
    # write verdict
    import json
    verdict = {"verified": True, "tests_run": tests, "tests_passed": passed}
    with open('verdict.json', 'w') as f:
        json.dump(verdict, f)

if __name__ == '__main__':
    main()
