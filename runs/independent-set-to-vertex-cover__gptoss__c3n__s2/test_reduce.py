import random
import itertools
import json
from problems import IndependentSet, VertexCover
from reduce import reduce


def brute_independent_set(instance):
    n = instance['n']
    edges = set(frozenset(e) for e in instance['edges'])
    k = instance['k']
    if k <= 0:
        return True
    if k > n:
        return False
    # generate all subsets
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
    if k < 0:
        return False
    if k >= n:
        return True
    if not edges:
        return True  # empty cover works
    for r in range(0, k+1):
        for subset in itertools.combinations(range(n), r):
            covered = True
            for u, v in edges:
                if u not in subset and v not in subset:
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


def run_tests(num=200):
    passed = 0
    for _ in range(num):
        src = random_instance()
        # validate
        IndependentSet.validate(src)
        # compute answers
        ans_src = brute_independent_set(src)
        tgt = reduce(src)
        VertexCover.validate(tgt)
        ans_tgt = brute_vertex_cover(tgt)
        # According to reduction, ans_src == ans_tgt
        if ans_src == ans_tgt:
            passed += 1
        else:
            print('FAIL')
            print('src', src)
            print('tgt', tgt)
            print('src ans', ans_src, 'tgt ans', ans_tgt)
            break
    return passed, num

if __name__ == '__main__':
    passed, total = run_tests(500)
    result = {
        "verified": passed == total,
        "tests_run": total,
        "tests_passed": passed,
    }
    print(json.dumps(result, indent=2))
    # also write verdict.json
    with open('verdict.json', 'w') as f:
        json.dump(result, f)
