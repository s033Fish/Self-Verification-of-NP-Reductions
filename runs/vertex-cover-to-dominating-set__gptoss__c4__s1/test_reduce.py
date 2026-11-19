import itertools
import random
import json
from problems import VertexCover, DominatingSet
from reduce import reduce

def brute_vertex_cover(instance):
    n = instance['n']
    edges = [tuple(e) for e in instance['edges']]
    k = instance['k']
    # Edge cases per definition
    if k < 0:
        return False
    if not edges:
        return True  # empty set covers
    if k >= n:
        return True
    # brute force subsets up to k
    vertices = list(range(n))
    for r in range(k+1):
        for subset in itertools.combinations(vertices, r):
            covered = True
            for u, v in edges:
                if u not in subset and v not in subset:
                    covered = False
                    break
            if covered:
                return True
    return False

def brute_dominating_set(instance):
    n = instance['n']
    edges = [tuple(e) for e in instance['edges']]
    k = instance['k']
    if k < 0:
        return False
    if n == 0:
        return True
    if k >= n:
        return True
    # adjacency list including self
    adj = {i: set([i]) for i in range(n)}
    for u, v in edges:
        adj[u].add(v)
        adj[v].add(u)
    vertices = list(range(n))
    for r in range(k+1):
        for subset in itertools.combinations(vertices, r):
            dominated = set()
            for v in subset:
                dominated.update(adj[v])
            if len(dominated) == n:
                return True
    return False


def random_instance(max_n=5, edge_prob=0.4):
    n = random.randint(0, max_n)
    edges = []
    for u in range(n):
        for v in range(u+1, n):
            if random.random() < edge_prob:
                edges.append([u, v])
    k = random.randint(-1, n+1)
    return {"n": n, "edges": edges, "k": k}


def test_one(instance):
    # validate source
    VertexCover.validate(instance)
    src_ans = brute_vertex_cover(instance)
    red = reduce(instance)
    # validate target
    DominatingSet.validate(red)
    tgt_ans = brute_dominating_set(red)
    if src_ans != tgt_ans:
        return False, instance, red, src_ans, tgt_ans
    return True, None, None, None, None


def main():
    random.seed(0)
    total = 0
    passed = 0
    for _ in range(200):
        inst = random_instance()
        ok, src, red, s_ans, t_ans = test_one(inst)
        total += 1
        if ok:
            passed += 1
        else:
            print('FAIL')
            print('src', src)
            print('red', red)
            print('src ans', s_ans, 'tgt ans', t_ans)
            break
    # also exhaustive for n up to 4
    for n in range(5):
        verts = list(range(n))
        all_edges = [(u, v) for u in verts for v in verts if u < v]
        for r in range(len(all_edges)+1):
            for edges in itertools.combinations(all_edges, r):
                for k in range(-1, n+2):
                    inst = {"n": n, "edges": [list(e) for e in edges], "k": k}
                    ok, src, red, s_ans, t_ans = test_one(inst)
                    total += 1
                    if ok:
                        passed += 1
                    else:
                        print('FAIL exhaustive')
                        print('inst', inst)
                        print('red', red)
                        print('src ans', s_ans, 'tgt ans', t_ans)
                        raise SystemExit(1)
    # write verdict
    verdict = {"verified": passed == total, "tests_run": total, "tests_passed": passed}
    with open('verdict.json', 'w') as f:
        json.dump(verdict, f)
    print('All tests passed', passed, '/', total)

if __name__ == '__main__':
    main()
