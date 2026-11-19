import itertools
import random
import json
import sys
from problems import VertexCover, SetCover
from reduce import reduce

def vertex_cover_bruteforce(instance):
    n = instance['n']
    edges = instance['edges']
    k = instance['k']
    if k < 0:
        return False
    if not edges:
        return k >= 0
    # iterate subsets up to size k
    vertices = list(range(n))
    for r in range(0, min(k, n) + 1):
        for subset in itertools.combinations(vertices, r):
            covered = True
            s = set(subset)
            for u, v in edges:
                if u not in s and v not in s:
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
        return k >= 0
    # check each element appears in at least one set
    all_elements = set(range(u))
    element_covered = set()
    for s in sets:
        element_covered.update(s)
    if not all_elements.issubset(element_covered):
        return False
    m = len(sets)
    for r in range(0, min(k, m) + 1):
        for combo in itertools.combinations(range(m), r):
            covered = set()
            for idx in combo:
                covered.update(sets[idx])
            if covered == all_elements:
                return True
    return False

def random_vertex_cover_instance(max_n=5, max_edges=10):
    n = random.randint(0, max_n)
    possible = [(i, j) for i in range(n) for j in range(i+1, n)]
    m = random.randint(0, min(len(possible), max_edges))
    edges = random.sample(possible, m)
    k = random.randint(-1, n+1)
    return {"n": n, "edges": [list(e) for e in edges], "k": k}

def main():
    random.seed(0)
    tests = 200
    passed = 0
    for _ in range(tests):
        src = random_vertex_cover_instance()
        # validate source
        try:
            VertexCover.validate(src)
        except Exception as e:
            print('Invalid source generated', src, e)
            sys.exit(1)
        tgt = reduce(src)
        # validate target
        try:
            SetCover.validate(tgt)
        except Exception as e:
            print('Invalid target produced', tgt, e)
            sys.exit(1)
        ans_src = vertex_cover_bruteforce(src)
        ans_tgt = set_cover_bruteforce(tgt)
        if ans_src != ans_tgt:
            print('Mismatch!')
            print('Source:', json.dumps(src))
            print('Target:', json.dumps(tgt))
            print('src ans', ans_src, 'tgt ans', ans_tgt)
            sys.exit(1)
        passed += 1
    print('All tests passed', passed)

if __name__ == '__main__':
    main()
