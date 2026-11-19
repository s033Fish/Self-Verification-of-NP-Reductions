import itertools
import random
import json
from problems import VertexCover, Clique
from reduce import reduce


def vertex_cover_bruteforce(instance):
    n = instance['n']
    edges = [(u, v) for u, v in instance['edges']]
    k = instance['k']
    if k < 0:
        return False
    if not edges:
        return True  # empty set covers
    if k >= n:
        return True
    vertices = list(range(n))
    # check any subset of size <= k
    for r in range(k + 1):
        for subset in itertools.combinations(vertices, r):
            covered = True
            for u, v in edges:
                if u not in subset and v not in subset:
                    covered = False
                    break
            if covered:
                return True
    return False


def clique_bruteforce(instance):
    n = instance['n']
    edges_set = {frozenset((u, v)) for u, v in instance['edges']}
    k = instance['k']
    if k <= 0:
        return True
    if n == 0:
        return k <= 0
    if k == 1:
        return n >= 1
    if k > n:
        return False
    vertices = list(range(n))
    # need at least k vertices
    for r in range(k, n + 1):
        for subset in itertools.combinations(vertices, r):
            ok = True
            for u, v in itertools.combinations(subset, 2):
                if frozenset((u, v)) not in edges_set:
                    ok = False
                    break
            if ok:
                return True
    return False


def random_instance(max_n=6):
    n = random.randint(0, max_n)
    possible = [(i, j) for i in range(n) for j in range(i + 1, n)]
    edges = []
    for (u, v) in possible:
        if random.choice([True, False]):
            edges.append([u, v])
    k = random.randint(-2, n + 2)  # allow out of range
    return {"n": n, "edges": edges, "k": k}


def run_tests(num_tests=200):
    passed = 0
    for _ in range(num_tests):
        src = random_instance()
        # validate source
        VertexCover.validate(src)
        tgt = reduce(src)
        Clique.validate(tgt)
        src_ans = vertex_cover_bruteforce(src)
        tgt_ans = clique_bruteforce(tgt)
        # According to reduction, src_yes == tgt_yes
        if src_ans == tgt_ans:
            passed += 1
        else:
            print('Mismatch!')
            print('Source:', src, 'src_ans', src_ans)
            print('Target:', tgt, 'tgt_ans', tgt_ans)
            return False, passed
    return True, passed

if __name__ == '__main__':
    ok, passed = run_tests(500)
    result = {
        "verified": ok,
        "tests_run": 500,
        "tests_passed": passed
    }
    print(json.dumps(result))
    with open('verdict.json', 'w') as f:
        json.dump(result, f)
