import itertools
import random
import json
from problems import Clique, VertexCover
from reduce import reduce


def solve_clique(instance):
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
    # brute force: check all subsets of size >= k
    for size in range(k, n + 1):
        for subset in itertools.combinations(range(n), size):
            # check if every pair is an edge
            ok = True
            for u, v in itertools.combinations(subset, 2):
                if frozenset((u, v)) not in edges:
                    ok = False
                    break
            if ok:
                return True
    return False


def solve_vertex_cover(instance):
    n = instance['n']
    edges = [tuple(e) for e in instance['edges']]
    k = instance['k']
    # edge cases
    if k < 0:
        return False
    if not edges:
        return k >= 0
    if k >= n:
        return True
    # brute force subsets up to size k
    for size in range(0, k + 1):
        for subset in itertools.combinations(range(n), size):
            covered = True
            for u, v in edges:
                if u not in subset and v not in subset:
                    covered = False
                    break
            if covered:
                return True
    return False


def random_instance(n_max=5, edge_prob=0.5):
    n = random.randint(0, n_max)
    edges = []
    for u in range(n):
        for v in range(u + 1, n):
            if random.random() < edge_prob:
                edges.append([u, v])
    # choose k in range -1..n+1
    k = random.randint(-1, n + 1)
    return {'n': n, 'edges': edges, 'k': k}


def main():
    random.seed(0)
    total = 0
    passed = 0
    for _ in range(200):
        inst = random_instance()
        # validate source
        Clique.validate(inst)
        # compute answers
        ans_clique = solve_clique(inst)
        red = reduce(inst)
        VertexCover.validate(red)
        ans_vc = solve_vertex_cover(red)
        if ans_clique == ans_vc:
            passed += 1
        else:
            print('Mismatch!')
            print('orig', json.dumps(inst))
            print('reduced', json.dumps(red))
            print('clique', ans_clique, 'vc', ans_vc)
            break
        total += 1
    # write verdict
    verdict = {'verified': passed == total, 'tests_run': total, 'tests_passed': passed}
    with open('verdict.json', 'w') as f:
        json.dump(verdict, f)
    print('Done', verdict)

if __name__ == '__main__':
    main()
