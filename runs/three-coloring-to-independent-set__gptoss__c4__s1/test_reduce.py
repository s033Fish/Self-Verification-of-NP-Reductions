import itertools
import random
import json
from problems import ThreeColoring, IndependentSet
from reduce import reduce

def three_coloring_bruteforce(instance):
    n = instance['n']
    edges = instance['edges']
    # Edge cases
    if n == 0:
        return True
    if n <= 3:
        return True
    # check for K4 subgraph quickly (optional) but brute force will handle
    for coloring in itertools.product(range(3), repeat=n):
        ok = True
        for u, v in edges:
            if coloring[u] == coloring[v]:
                ok = False
                break
        if ok:
            return True
    return False

def independent_set_bruteforce(instance):
    n = instance['n']
    edges = set(frozenset(e) for e in instance['edges'])
    k = instance['k']
    if k <= 0:
        return True
    if k > n:
        return False
    # generate subsets of size >=k
    vertices = list(range(n))
    for r in range(k, n+1):
        for subset in itertools.combinations(vertices, r):
            # check independent
            independent = True
            for u, v in itertools.combinations(subset, 2):
                if frozenset((u, v)) in edges:
                    independent = False
                    break
            if independent:
                return True
    return False


def random_graph(n, edge_prob=0.5):
    edges = []
    for u in range(n):
        for v in range(u+1, n):
            if random.random() < edge_prob:
                edges.append([u, v])
    return {'n': n, 'edges': edges}


def test_one(instance):
    # validate source
    ThreeColoring.validate(instance)
    reduced = reduce(instance)
    IndependentSet.validate(reduced)
    src_ans = three_coloring_bruteforce(instance)
    tgt_ans = independent_set_bruteforce(reduced)
    assert src_ans == tgt_ans, f"Mismatch! src={src_ans} tgt={tgt_ans} instance={instance} reduced={reduced}"

def main():
    random.seed(0)
    tests = 0
    # edge cases
    for n in range(0, 5):
        instance = {'n': n, 'edges': []}
        test_one(instance)
        tests += 1
    # random tests
    for _ in range(50):
        n = random.randint(0, 5)
        inst = random_graph(n, edge_prob=0.4)
        test_one(inst)
        tests += 1
    print('All', tests, 'tests passed')

if __name__ == '__main__':
    main()
