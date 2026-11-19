import itertools
import json
import random
import sys
from problems import Clique, VertexCover
from reduce import reduce


def brute_clique(instance):
    n = instance['n']
    edges = set(frozenset(e) for e in instance['edges'])
    k = instance['k']
    # Edge cases per definition
    if k <= 0:
        return True
    if k == 1:
        return n >= 1
    if k > n:
        return False
    # try all subsets of size >= k
    vertices = list(range(n))
    for size in range(k, n+1):
        for subset in itertools.combinations(vertices, size):
            ok = True
            for u, v in itertools.combinations(subset, 2):
                if frozenset((u, v)) not in edges:
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
    if not edges:
        return k >= 0
    if k >= n:
        return True
    vertices = list(range(n))
    for size in range(0, k+1):
        for subset in itertools.combinations(vertices, size):
            covered = True
            subset_set = set(subset)
            for u, v in edges:
                if u not in subset_set and v not in subset_set:
                    covered = False
                    break
            if covered:
                return True
    return False


def random_instance(n_max=6):
    n = random.randint(0, n_max)
    # generate random edge set
    possible = [(u, v) for u in range(n) for v in range(u+1, n)]
    edges = []
    for (u, v) in possible:
        if random.choice([True, False]):
            edges.append([u, v])
    k = random.randint(-1, n+2)  # allow out of range values
    return {'n': n, 'edges': edges, 'k': k}


def run_tests(num=2000):
    passed = 0
    for i in range(num):
        inst = random_instance()
        # validate source
        try:
            Clique.validate(inst)
        except Exception as e:
            # invalid instance, skip
            continue
        reduced = reduce(inst)
        # validate target
        VertexCover.validate(reduced)
        ans_src = brute_clique(inst)
        ans_tgt = brute_vertex_cover(reduced)
        if ans_src == ans_tgt:
            passed += 1
        else:
            print('Mismatch!')
            print('src', inst)
            print('reduced', reduced)
            print('src ans', ans_src, 'tgt ans', ans_tgt)
            sys.exit(1)
    return passed, num

if __name__ == '__main__':
    passed, total = run_tests(2000)
    result = {
        "verified": passed == total,
        "tests_run": total,
        "tests_passed": passed,
    }
    print(json.dumps(result, indent=2))
    with open('verdict.json', 'w') as f:
        json.dump(result, f)
