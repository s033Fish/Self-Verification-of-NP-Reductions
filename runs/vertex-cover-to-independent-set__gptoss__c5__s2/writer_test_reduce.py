import itertools
import random
import json
from problems import VertexCover, IndependentSet, InvalidInstance
from reduce import reduce

def solve_vertex_cover(instance):
    n = instance['n']
    edges = instance['edges']
    k = instance['k']
    if k < 0:
        return False
    if not edges:
        return True  # empty set covers
    if k >= n:
        return True
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

def solve_independent_set(instance):
    n = instance['n']
    edges = set(frozenset(e) for e in instance['edges'])
    k = instance['k']
    if k <= 0:
        return True
    if k > n:
        return False
    vertices = list(range(n))
    for r in range(k, n+1):
        for subset in itertools.combinations(vertices, r):
            ok = True
            s = set(subset)
            for e in edges:
                if e.issubset(s):
                    ok = False
                    break
            if ok:
                return True
    return False

def random_instance(max_n=5, edge_prob=0.4):
    n = random.randint(0, max_n)
    edges = []
    for u in range(n):
        for v in range(u+1, n):
            if random.random() < edge_prob:
                edges.append([u, v])
    k = random.randint(-1, n+1)
    return {"n": n, "edges": edges, "k": k}

def run_tests(num=200):
    passed = 0
    for _ in range(num):
        inst = random_instance()
        # validate source
        try:
            VertexCover.validate(inst)
        except InvalidInstance:
            continue  # skip malformed (should not happen)
        reduced = reduce(inst)
        # validate target
        IndependentSet.validate(reduced)
        ans_src = solve_vertex_cover(inst)
        ans_tgt = solve_independent_set(reduced)
        if ans_src == ans_tgt:
            passed += 1
        else:
            print('Mismatch', inst, reduced, ans_src, ans_tgt)
            break
    return passed, num

if __name__ == '__main__':
    passed, total = run_tests(500)
    result = {
        "verified": passed == total,
        "tests_run": total,
        "tests_passed": passed,
    }
    print(json.dumps(result))
    with open('verdict.json', 'w') as f:
        json.dump(result, f)
