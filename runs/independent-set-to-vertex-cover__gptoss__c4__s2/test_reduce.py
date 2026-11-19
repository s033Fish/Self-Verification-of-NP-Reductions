import itertools
import random
import json
from problems import IndependentSet, VertexCover, InvalidInstance
from reduce import reduce

def solve_independent_set(instance):
    IndependentSet.validate(instance)
    n = instance['n']
    edges = [(u, v) for u, v in instance['edges']]
    k = instance['k']
    # Edge cases
    if k <= 0:
        return True
    if k > n:
        return False
    # brute force all subsets of size >= k
    vertices = list(range(n))
    for size in range(k, n+1):
        for subset in itertools.combinations(vertices, size):
            s = set(subset)
            ok = True
            for u, v in edges:
                if u in s and v in s:
                    ok = False
                    break
            if ok:
                return True
    return False

def solve_vertex_cover(instance):
    VertexCover.validate(instance)
    n = instance['n']
    edges = [(u, v) for u, v in instance['edges']]
    k = instance['k']
    # Edge cases
    if k < 0:
        return False
    if k >= n:
        return True
    # brute force all subsets of size <= k
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

def random_instance(max_n=6, edge_prob=0.4):
    n = random.randint(0, max_n)
    edges = []
    for u in range(n):
        for v in range(u+1, n):
            if random.random() < edge_prob:
                edges.append([u, v])
    k = random.randint(-2, n+2)  # allow out of range values
    return {'n': n, 'edges': edges, 'k': k}


def main():
    random.seed(0)
    tests = 200
    passed = 0
    for i in range(tests):
        src = random_instance()
        # ensure source instance is valid
        try:
            IndependentSet.validate(src)
        except InvalidInstance:
            continue
        tgt = reduce(src)
        # ensure target valid
        VertexCover.validate(tgt)
        ans_src = solve_independent_set(src)
        ans_tgt = solve_vertex_cover(tgt)
        if ans_src == ans_tgt:
            passed += 1
        else:
            print('Mismatch on test', i)
            print('src', src)
            print('tgt', tgt)
            print('src ans', ans_src, 'tgt ans', ans_tgt)
            break
    result = {
        'verified': passed == tests,
        'tests_run': tests,
        'tests_passed': passed,
    }
    print(json.dumps(result, indent=2))
    with open('verdict.json', 'w') as f:
        json.dump(result, f)

if __name__ == '__main__':
    main()
