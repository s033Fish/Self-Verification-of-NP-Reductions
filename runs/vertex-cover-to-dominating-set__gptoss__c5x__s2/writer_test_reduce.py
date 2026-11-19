import itertools
import json
import sys
from problems import VertexCover, DominatingSet
import reduce

def vertex_cover_bruteforce(instance):
    n = instance['n']
    edges = instance['edges']
    k = instance['k']
    if k < 0:
        return False
    # any subset up to k
    vertices = list(range(n))
    for r in range(min(k, n) + 1):
        for subset in itertools.combinations(vertices, r):
            covered = True
            subset_set = set(subset)
            for u, v in edges:
                if u not in subset_set and v not in subset_set:
                    covered = False
                    break
            if covered:
                return True
    return False

def dominating_set_bruteforce(instance):
    n = instance['n']
    edges = instance['edges']
    k = instance['k']
    if k < 0:
        return False
    # adjacency list
    adj = {i: set() for i in range(n)}
    for u, v in edges:
        adj[u].add(v)
        adj[v].add(u)
    vertices = list(range(n))
    for r in range(min(k, n) + 1):
        for subset in itertools.combinations(vertices, r):
            dominated = set(subset)
            for v in subset:
                dominated.update(adj[v])
            if len(dominated) == n:
                return True
    return False

def generate_random_instance(max_n=5, max_edges=7):
    import random
    n = random.randint(0, max_n)
    possible = [(i, j) for i in range(n) for j in range(i+1, n)]
    random.shuffle(possible)
    m = random.randint(0, min(len(possible), max_edges))
    edges = [list(possible[i]) for i in range(m)]
    k = random.randint(-1, n+1)
    return {"n": n, "edges": edges, "k": k}

def run_tests(num=200):
    passed = 0
    for _ in range(num):
        src = generate_random_instance()
        # validate source
        VertexCover.validate(src)
        # reduce
        tgt = reduce.reduce(src)
        DominatingSet.validate(tgt)
        src_ans = vertex_cover_bruteforce(src)
        tgt_ans = dominating_set_bruteforce(tgt)
        if src_ans == tgt_ans:
            passed += 1
        else:
            print('Mismatch!')
            print('src', src, src_ans)
            print('tgt', tgt, tgt_ans)
            return False, passed, num
    return True, passed, num

if __name__ == '__main__':
    ok, passed, total = run_tests(200)
    result = {
        "verified": ok,
        "tests_run": total,
        "tests_passed": passed,
    }
    print(json.dumps(result))
    sys.exit(0 if ok else 1)
