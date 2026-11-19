import itertools
import random
import json
from problems import VertexCover, IndependentSet
from reduce import reduce

def solve_vertex_cover(instance):
    n = instance['n']
    edges = [(u, v) for u, v in instance['edges']]
    k = instance['k']
    # Edge cases per definition
    if k < 0:
        return False
    if k >= n:
        return True
    if not edges:
        return True
    # brute force subsets up to size k
    for r in range(k + 1):
        for subset in itertools.combinations(range(n), r):
            cover = set(subset)
            if all(u in cover or v in cover for u, v in edges):
                return True
    return False

def solve_independent_set(instance):
    n = instance['n']
    edges = [(u, v) for u, v in instance['edges']]
    k = instance['k']
    # Edge cases per definition
    if k <= 0:
        return True
    if k > n:
        return False
    if not edges:
        return True
    # brute force subsets of size >= k
    for r in range(k, n + 1):
        for subset in itertools.combinations(range(n), r):
            s = set(subset)
            if all(not (u in s and v in s) for u, v in edges):
                return True
    return False


def random_instance(max_n=6, max_edges=10, max_k=6):
    n = random.randint(0, max_n)
    possible_edges = [(i, j) for i in range(n) for j in range(i+1, n)]
    m = random.randint(0, min(len(possible_edges), max_edges))
    edges = random.sample(possible_edges, m)
    edges = [list(e) for e in edges]
    k = random.randint(-2, max_k)
    return {'n': n, 'edges': edges, 'k': k}


def run_tests(num=200):
    passed = 0
    for _ in range(num):
        src = random_instance()
        # validate source
        VertexCover.validate(src)
        src_ans = solve_vertex_cover(src)
        tgt = reduce(src)
        IndependentSet.validate(tgt)
        tgt_ans = solve_independent_set(tgt)
        if src_ans == tgt_ans:
            passed += 1
        else:
            print('FAIL')
            print('src', src, 'src_ans', src_ans)
            print('tgt', tgt, 'tgt_ans', tgt_ans)
            break
    return passed, num

if __name__ == '__main__':
    passed, total = run_tests(500)
    result = {
        'verified': passed == total,
        'tests_run': total,
        'tests_passed': passed,
    }
    print(json.dumps(result))
    with open('verdict.json', 'w') as f:
        json.dump(result, f)
