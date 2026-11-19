import itertools
import random
import json
import sys
from problems import IndependentSet, VertexCover
from reduce import reduce

def brute_independent_set(instance):
    n = instance['n']
    edges = set(frozenset(e) for e in instance['edges'])
    k = instance['k']
    # Edge cases
    if k <= 0:
        return True
    if k > n:
        return False
    # brute force
    for r in range(k, n+1):
        for subset in itertools.combinations(range(n), r):
            ok = True
            for u, v in itertools.combinations(subset, 2):
                if frozenset((u, v)) in edges:
                    ok = False
                    break
            if ok:
                return True
    return False

def brute_vertex_cover(instance):
    n = instance['n']
    edges = [tuple(e) for e in instance['edges']]
    k = instance['k']
    # Edge cases
    if k < 0:
        return False
    if k >= n:
        return True
    # brute force
    for r in range(0, k+1):
        for subset in itertools.combinations(range(n), r):
            covered = True
            subset_set = set(subset)
            for u, v in edges:
                if u not in subset_set and v not in subset_set:
                    covered = False
                    break
            if covered:
                return True
    return False

def random_instance(n, edge_prob=0.5, k_range=None):
    edges = []
    for i in range(n):
        for j in range(i+1, n):
            if random.random() < edge_prob:
                edges.append([i, j])
    if k_range is None:
        k_range = (-1, n+2)
    k = random.randint(*k_range)
    return {"n": n, "edges": edges, "k": k}

def run_tests(num_tests=200):
    passed = 0
    for _ in range(num_tests):
        n = random.randint(0, 6)
        inst = random_instance(n)
        # validate
        IndependentSet.validate(inst)
        # reduce
        red = reduce(inst)
        VertexCover.validate(red)
        # compare answers
        ans_src = brute_independent_set(inst)
        ans_tgt = brute_vertex_cover(red)
        if ans_src == ans_tgt:
            passed += 1
        else:
            print('FAIL')
            print('src', json.dumps(inst))
            print('red', json.dumps(red))
            print('src ans', ans_src, 'tgt ans', ans_tgt)
            return passed, False
    return passed, True

if __name__ == '__main__':
    total, ok = run_tests(500)
    print(f"Tests run: {total}, passed: {total if ok else total-1}")
    verdict = {"verified": ok, "tests_run": total, "tests_passed": total if ok else total-1}
    with open('verdict.json', 'w') as f:
        json.dump(verdict, f)
    sys.exit(0 if ok else 1)
