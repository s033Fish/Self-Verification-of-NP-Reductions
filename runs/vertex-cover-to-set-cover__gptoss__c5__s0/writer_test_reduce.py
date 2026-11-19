import itertools
import random
import json
from problems import VertexCover, SetCover
from reduce import reduce

def solve_vertex_cover(instance):
    n = instance['n']
    edges = [tuple(e) for e in instance['edges']]
    k = instance['k']
    if k < 0:
        return False
    # quick edge cases
    if not edges:
        return True
    if k >= n:
        return True
    # brute force subsets up to k
    vertices = list(range(n))
    for r in range(k+1):
        for subset in itertools.combinations(vertices, r):
            covered = True
            sset = set(subset)
            for u,v in edges:
                if u not in sset and v not in sset:
                    covered = False
                    break
            if covered:
                return True
    return False

def solve_set_cover(instance):
    u = instance['universe_size']
    sets = [set(s) for s in instance['sets']]
    k = instance['k']
    if k < 0:
        return False
    if u == 0:
        return True
    # check every element appears in some set
    all_elements = set(range(u))
    if not all_elements.issubset(set().union(*sets)):
        return False
    if k >= len(sets):
        return True
    # brute force
    for r in range(k+1):
        for combo in itertools.combinations(range(len(sets)), r):
            covered = set()
            for idx in combo:
                covered.update(sets[idx])
            if covered == all_elements:
                return True
    return False

def random_vertex_cover_instance(max_n=5, max_edges=7, max_k=5):
    n = random.randint(0, max_n)
    possible_edges = [(i,j) for i in range(n) for j in range(i+1,n)]
    m = random.randint(0, min(len(possible_edges), max_edges))
    edges = random.sample(possible_edges, m)
    k = random.randint(-1, max_k)
    return {"n": n, "edges": [list(e) for e in edges], "k": k}

def test_random_cases(num_cases=200):
    for _ in range(num_cases):
        src = random_vertex_cover_instance()
        # validate source
        VertexCover.validate(src)
        tgt = reduce(src)
        SetCover.validate(tgt)
        ans_src = solve_vertex_cover(src)
        ans_tgt = solve_set_cover(tgt)
        if ans_src != ans_tgt:
            print('Mismatch!')
            print('src', src)
            print('tgt', tgt)
            print('src ans', ans_src, 'tgt ans', ans_tgt)
            return False
    return True

if __name__ == '__main__':
    ok = test_random_cases(500)
    result = {
        "verified": ok,
        "tests_run": 500,
        "tests_passed": 500 if ok else 0
    }
    print(json.dumps(result))
    with open('verdict.json', 'w') as f:
        json.dump(result, f)
