import itertools
import json
import random
from problems import VertexCover, Clique
from reduce import reduce


def vertex_cover_bruteforce(instance):
    n = instance['n']
    edges = [tuple(e) for e in instance['edges']]
    k = instance['k']
    if k < 0:
        return False
    if not edges:
        return True  # empty edge set always covered
    # iterate subsets up to size k
    for r in range(min(k, n) + 1):
        for subset in itertools.combinations(range(n), r):
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
        return False
    if k == 1:
        return n >= 1
    # check subsets of size >= k
    for r in range(k, n + 1):
        for subset in itertools.combinations(range(n), r):
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
    m = random.randint(0, len(possible))
    edges = random.sample(possible, m)
    edges = [list(e) for e in edges]
    k = random.randint(-1, n+1)
    return {'n': n, 'edges': edges, 'k': k}


def run_tests(num=200):
    passed = 0
    for _ in range(num):
        src = random_instance()
        # validate source
        VertexCover.validate(src)
        tgt = reduce(src)
        Clique.validate(tgt)
        src_ans = vertex_cover_bruteforce(src)
        tgt_ans = clique_bruteforce(tgt)
        if src_ans == tgt_ans:
            passed += 1
        else:
            print('FAIL')
            print('src', src)
            print('tgt', tgt)
            print('src_ans', src_ans, 'tgt_ans', tgt_ans)
            break
    return passed, num

if __name__ == '__main__':
    passed, total = run_tests(500)
    result = {'verified': passed == total, 'tests_run': total, 'tests_passed': passed}
    print(json.dumps(result))
    with open('verdict.json', 'w') as f:
        json.dump(result, f)
