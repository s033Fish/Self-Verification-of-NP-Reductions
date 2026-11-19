import random
import itertools
import json
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
    # Check existence of clique of size at least k
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

def random_instance(max_n=6):
    n = random.randint(0, max_n)
    possible = [(i, j) for i in range(n) for j in range(i+1, n)]
    edges = []
    for u, v in possible:
        if random.choice([True, False]):
            edges.append([u, v])
    k = random.randint(-2, n+2)  # allow out of range values
    return {'n': n, 'edges': edges, 'k': k}


def run_tests(num_trials=200):
    passed = 0
    for _ in range(num_trials):
        src = random_instance()
        # validate source
        Clique.validate(src)
        src_ans = brute_clique(src)
        tgt = reduce(src)
        VertexCover.validate(tgt)
        tgt_ans = brute_vertex_cover(tgt)
        if src_ans == tgt_ans:
            passed += 1
        else:
            print('Mismatch!')
            print('src', src, 'src_ans', src_ans)
            print('tgt', tgt, 'tgt_ans', tgt_ans)
            break
    return passed, num_trials

if __name__ == '__main__':
    passed, total = run_tests(500)
    verdict = {
        'verified': passed == total,
        'tests_run': total,
        'tests_passed': passed,
    }
    print(json.dumps(verdict, indent=2))
    with open('verdict.json', 'w') as f:
        json.dump(verdict, f)
