import random
import sys
from itertools import combinations
from problems import VertexCover, SetCover
from reduce import reduce


def vertex_cover_bruteforce(instance):
    n = instance['n']
    edges = instance['edges']
    k = instance['k']
    if k < 0:
        return False
    # trivial yes cases
    if not edges:
        return True
    if k >= n:
        return True
    vertices = list(range(n))
    for r in range(k + 1):
        for subset in combinations(vertices, r):
            covered = True
            for u, v in edges:
                if u not in subset and v not in subset:
                    covered = False
                    break
            if covered:
                return True
    return False


def set_cover_bruteforce(instance):
    u = instance['universe_size']
    sets = instance['sets']
    k = instance['k']
    if k < 0:
        return False
    if u == 0:
        return True
    # check each element appears in some set, else impossible
    all_elements = set(range(u))
    element_present = set()
    for s in sets:
        element_present.update(s)
    if not all_elements.issubset(element_present):
        return False
    m = len(sets)
    for r in range(k + 1):
        for idxs in combinations(range(m), r):
            covered = set()
            for i in idxs:
                covered.update(sets[i])
            if covered == all_elements:
                return True
    return False


def random_vertex_cover_instance(max_n=5, max_edges=7):
    n = random.randint(0, max_n)
    possible_edges = [(i, j) for i in range(n) for j in range(i+1, n)]
    m = random.randint(0, min(len(possible_edges), max_edges))
    edges = random.sample(possible_edges, m)
    k = random.randint(-1, n+1)  # allow out of range
    return {'n': n, 'edges': [list(e) for e in edges], 'k': k}


def run_tests(num=200):
    passed = 0
    for i in range(num):
        inst = random_vertex_cover_instance()
        # validate
        VertexCover.validate(inst)
        # compute answers
        ans_src = vertex_cover_bruteforce(inst)
        red = reduce(inst)
        SetCover.validate(red)
        ans_tgt = set_cover_bruteforce(red)
        if ans_src != ans_tgt:
            print('Mismatch on test', i)
            print('Source:', inst)
            print('Reduced:', red)
            print('src answer', ans_src, 'tgt answer', ans_tgt)
            return passed, i
        passed += 1
    return passed, num

if __name__ == '__main__':
    passed, total = run_tests(500)
    print(f'Tests run: {total}, passed: {passed}')
    sys.exit(0 if passed == total else 1)
