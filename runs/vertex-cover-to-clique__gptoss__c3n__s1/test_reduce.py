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
    # any subset up to k
    for r in range(k + 1):
        for subset in itertools.combinations(range(n), r):
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
    edge_set = {frozenset(e) for e in instance['edges']}
    k = instance['k']
    if k <= 0:
        return True
    if k > n:
        return False
    # need any subset of size >= k that is a clique
    for r in range(k, n + 1):
        for subset in itertools.combinations(range(n), r):
            ok = True
            for u, v in itertools.combinations(subset, 2):
                if frozenset((u, v)) not in edge_set:
                    ok = False
                    break
            if ok:
                return True
    return False


def random_instance(max_n=6, edge_prob=0.5, k_range=(-2, 8)):
    n = random.randint(0, max_n)
    edges = []
    for u in range(n):
        for v in range(u + 1, n):
            if random.random() < edge_prob:
                edges.append([u, v])
    k = random.randint(k_range[0], k_range[1])
    return {'n': n, 'edges': edges, 'k': k}


def run_tests(num=200):
    passed = 0
    for i in range(num):
        inst = random_instance()
        # validate source
        try:
            VertexCover.validate(inst)
        except Exception as e:
            # skip invalid generated instances (shouldn't happen)
            continue
        src_ans = vertex_cover_bruteforce(inst)
        red = reduce(inst)
        # validate target
        Clique.validate(red)
        tgt_ans = clique_bruteforce(red)
        if src_ans == tgt_ans:
            passed += 1
        else:
            print('Mismatch!')
            print('src', inst, src_ans)
            print('red', red, tgt_ans)
            return False, passed, i+1
    return True, passed, num

if __name__ == '__main__':
    ok, passed, total = run_tests(500)
    result = {
        'verified': ok,
        'tests_run': total,
        'tests_passed': passed,
    }
    print(json.dumps(result))
    with open('verdict.json', 'w') as f:
        json.dump(result, f)
