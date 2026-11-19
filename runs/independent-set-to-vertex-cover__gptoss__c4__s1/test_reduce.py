import itertools
import random
import json
from problems import IndependentSet, VertexCover
from reduce import reduce

def solve_independent_set(instance):
    IndependentSet.validate(instance)
    n = instance['n']
    edges = set(frozenset(e) for e in instance['edges'])
    k = instance['k']
    if k <= 0:
        return True
    if k > n:
        return False
    # brute force all subsets of size >= k
    vertices = list(range(n))
    for r in range(k, n+1):
        for subset in itertools.combinations(vertices, r):
            ok = True
            for u, v in itertools.combinations(subset, 2):
                if frozenset((u, v)) in edges:
                    ok = False
                    break
            if ok:
                return True
    return False

def solve_vertex_cover(instance):
    VertexCover.validate(instance)
    n = instance['n']
    edges = [tuple(e) for e in instance['edges']]
    k = instance['k']
    if k < 0:
        return False
    if k >= n:
        return True
    # brute force all subsets of size <= k
    vertices = list(range(n))
    for r in range(0, k+1):
        for subset in itertools.combinations(vertices, r):
            covered = True
            for u, v in edges:
                if not (u in subset or v in subset):
                    covered = False
                    break
            if covered:
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


def test_one(instance):
    src = solve_independent_set(instance)
    red = reduce(instance)
    tgt = solve_vertex_cover(red)
    # Relation: Independent Set >= k  <=> Vertex Cover <= n-k
    # Our reduction sets k' = n - k, so tgt should be src.
    return src == tgt


def main():
    random.seed(0)
    total = 200
    passed = 0
    for i in range(total):
        inst = random_instance()
        try:
            ok = test_one(inst)
        except Exception as e:
            print('Error on instance', inst, e)
            ok = False
        if ok:
            passed += 1
        else:
            print('Failed instance', json.dumps(inst))
            break
    print(f'Passed {passed}/{total}')
    # write verdict
    verdict = {
        "verified": passed == total,
        "tests_run": total,
        "tests_passed": passed,
    }
    with open('verdict.json', 'w') as f:
        json.dump(verdict, f)

if __name__ == '__main__':
    main()
