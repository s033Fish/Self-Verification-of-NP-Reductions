import itertools
import random
import json
from problems import VertexCover, DominatingSet
from reduce import reduce

def solve_vertex_cover(inst):
    n = inst['n']
    edges = inst['edges']
    k = inst['k']
    if k < 0:
        return False
    if k >= n:
        return True
    if not edges:
        return True
    vertices = list(range(n))
    for r in range(k+1):
        for combo in itertools.combinations(vertices, r):
            cover = set(combo)
            ok = True
            for u, v in edges:
                if u not in cover and v not in cover:
                    ok = False
                    break
            if ok:
                return True
    return False

def solve_dominating_set(inst):
    n = inst['n']
    edges = inst['edges']
    k = inst['k']
    if k < 0:
        return False
    if k >= n:
        return True
    if n == 0:
        return True
    # adjacency list including self
    adj = [set([i]) for i in range(n)]
    for u, v in edges:
        adj[u].add(v)
        adj[v].add(u)
    vertices = list(range(n))
    for r in range(k+1):
        for combo in itertools.combinations(vertices, r):
            dominated = set()
            for v in combo:
                dominated.update(adj[v])
            if len(dominated) == n:
                return True
    return False

def random_instance(max_n=5):
    n = random.randint(0, max_n)
    # generate possible edges
    all_edges = [(i, j) for i in range(n) for j in range(i+1, n)]
    edges = []
    for e in all_edges:
        if random.choice([True, False]):
            edges.append([e[0], e[1]])
    k = random.randint(-1, n+1)
    return {"n": n, "edges": edges, "k": k}

def run_tests(num=200):
    passed = 0
    for _ in range(num):
        src = random_instance()
        # validate source
        VertexCover.validate(src)
        src_ans = solve_vertex_cover(src)
        tgt = reduce(src)
        DominatingSet.validate(tgt)
        tgt_ans = solve_dominating_set(tgt)
        if src_ans == tgt_ans:
            passed += 1
        else:
            print('FAIL')
            print('src', src, src_ans)
            print('tgt', tgt, tgt_ans)
            break
    return passed, num

if __name__ == '__main__':
    passed, total = run_tests(500)
    result = {
        "verified": passed == total,
        "tests_run": total,
        "tests_passed": passed,
    }
    print(json.dumps(result))
    with open('verdict.json', 'w') as f:
        json.dump(result, f)
