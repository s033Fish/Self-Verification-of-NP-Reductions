import random
import itertools
import json
from problems import IndependentSet, VertexCover
from reduce import reduce

def solve_independent_set(instance):
    n = instance['n']
    edges = [tuple(e) for e in instance['edges']]
    k = instance['k']
    if k <= 0:
        return True
    if k > n:
        return False
    # brute force all subsets of size >= k
    vertices = list(range(n))
    for size in range(k, n+1):
        for subset in itertools.combinations(vertices, size):
            ok = True
            s = set(subset)
            for u, v in edges:
                if u in s and v in s:
                    ok = False
                    break
            if ok:
                return True
    return False

def solve_vertex_cover(instance):
    n = instance['n']
    edges = [tuple(e) for e in instance['edges']]
    k = instance['k']
    if k < 0:
        return False
    if k >= n:
        return True
    vertices = list(range(n))
    for size in range(0, k+1):
        for subset in itertools.combinations(vertices, size):
            s = set(subset)
            ok = True
            for u, v in edges:
                if u not in s and v not in s:
                    ok = False
                    break
            if ok:
                return True
    return False

def random_instance(max_n=6):
    n = random.randint(0, max_n)
    possible_edges = [(i, j) for i in range(n) for j in range(i+1, n)]
    edges = []
    for (u, v) in possible_edges:
        if random.random() < 0.3:
            edges.append([u, v])
    k = random.randint(-2, n+2)
    return {"n": n, "edges": edges, "k": k}

random.seed(0)
tests = 200
passed = 0
for _ in range(tests):
    inst = random_instance()
    # validate source
    IndependentSet.validate(inst)
    reduced = reduce(inst)
    VertexCover.validate(reduced)
    ans_src = solve_independent_set(inst)
    ans_tgt = solve_vertex_cover(reduced)
    if ans_src == ans_tgt:
        passed += 1
    else:
        print('FAIL')
        print('src', inst)
        print('reduced', reduced)
        print('src ans', ans_src, 'tgt ans', ans_tgt)
        break
print('Tests run:', tests, 'passed:', passed)

# write verdict
verdict = {
    "verified": passed == tests,
    "tests_run": tests,
    "tests_passed": passed,
}
with open('verdict.json', 'w') as f:
    json.dump(verdict, f)
