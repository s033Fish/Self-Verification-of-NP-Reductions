import itertools
import random
import json
from problems import VertexCover, Clique
from reduce import reduce

def vertex_cover_bruteforce(instance):
    n = instance['n']
    edges = [tuple(e) for e in instance['edges']]
    k = instance['k']
    if k < 0:
        return False
    if not edges:
        return True  # empty set covers
    if k >= n:
        return True
    # try all subsets of size up to k
    vertices = list(range(n))
    for r in range(k+1):
        for subset in itertools.combinations(vertices, r):
            covered = True
            subset_set = set(subset)
            for u, v in edges:
                if u not in subset_set and v not in subset_set:
                    covered = False
                    break
            if covered:
                return True
    return False

def clique_bruteforce(instance):
    n = instance['n']
    edges_set = {frozenset(e) for e in instance['edges']}
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
    # check all subsets of size >= k
    for r in range(k, n+1):
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
    possible = [(u, v) for u in range(n) for v in range(u+1, n)]
    edges = []
    for (u, v) in possible:
        if random.choice([True, False]):
            edges.append([u, v])
    k = random.randint(-1, n+2)
    return {'n': n, 'edges': edges, 'k': k}

def run_tests(num=200):
    passed = 0
    for i in range(num):
        src = random_instance()
        # validate source
        VertexCover.validate(src)
        src_ans = vertex_cover_bruteforce(src)
        tgt = reduce(src)
        Clique.validate(tgt)
        tgt_ans = clique_bruteforce(tgt)
        if src_ans == tgt_ans:
            passed += 1
        else:
            print('Mismatch on instance', src)
            print('Reduced to', tgt)
            print('src_ans', src_ans, 'tgt_ans', tgt_ans)
            break
    return passed, num

if __name__ == '__main__':
    passed, total = run_tests(500)
    result = {
        'verified': passed == total,
        'tests_run': total,
        'tests_passed': passed,
    }
    print(json.dumps(result, indent=2))
    with open('verdict.json', 'w') as f:
        json.dump(result, f)
