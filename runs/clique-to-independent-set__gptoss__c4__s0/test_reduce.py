import itertools
import random
import json
from problems import Clique, IndependentSet
from reduce import reduce


def brute_clique(instance):
    n = instance['n']
    edges = set(frozenset(e) for e in instance['edges'])
    k = instance['k']
    if k <= 0:
        return True
    if k == 1:
        return n >= 1
    if k > n:
        return False
    # check all subsets of size >= k
    vertices = list(range(n))
    for size in range(k, n+1):
        for subset in itertools.combinations(vertices, size):
            # check all pairs are edges
            ok = True
            for u, v in itertools.combinations(subset, 2):
                if frozenset((u, v)) not in edges:
                    ok = False
                    break
            if ok:
                return True
    return False


def brute_independent(instance):
    n = instance['n']
    edges = set(frozenset(e) for e in instance['edges'])
    k = instance['k']
    if k <= 0:
        return True
    if k > n:
        return False
    vertices = list(range(n))
    for size in range(k, n+1):
        for subset in itertools.combinations(vertices, size):
            ok = True
            for u, v in itertools.combinations(subset, 2):
                if frozenset((u, v)) in edges:
                    ok = False
                    break
            if ok:
                return True
    return False


def random_instance(n_max=6, edge_prob=0.5):
    n = random.randint(0, n_max)
    edges = []
    for u in range(n):
        for v in range(u+1, n):
            if random.random() < edge_prob:
                edges.append([u, v])
    k = random.randint(-1, n+2)  # include edge cases
    return {'n': n, 'edges': edges, 'k': k}


def run_tests(num=200):
    passed = 0
    for _ in range(num):
        inst = random_instance()
        # validate source
        Clique.validate(inst)
        # compute answers
        ans_clique = brute_clique(inst)
        red = reduce(inst)
        IndependentSet.validate(red)
        ans_ind = brute_independent(red)
        if ans_clique == ans_ind:
            passed += 1
        else:
            print('FAIL')
            print('orig', inst)
            print('reduced', red)
            print('clique', ans_clique, 'ind', ans_ind)
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
    with open('verdict.json', 'w') as f:
        json.dump(result, f)
