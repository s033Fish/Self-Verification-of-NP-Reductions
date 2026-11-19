import itertools
import random
import json
from problems import VertexCover, DominatingSet
from reduce import reduce

def vertex_cover_bruteforce(instance):
    n = instance['n']
    edges = instance['edges']
    k = instance['k']
    if k < 0:
        return False
    if not edges:
        return True
    if k >= n:
        return True
    vertices = list(range(n))
    for r in range(k+1):
        for subset in itertools.combinations(vertices, r):
            s = set(subset)
            ok = True
            for u,v in edges:
                if u not in s and v not in s:
                    ok = False
                    break
            if ok:
                return True
    return False

def dominating_set_bruteforce(instance):
    n = instance['n']
    edges = instance['edges']
    k = instance['k']
    if k < 0:
        return False
    if n == 0:
        return True
    if k >= n:
        return True
    # build adjacency list
    adj = {i: set() for i in range(n)}
    for u,v in edges:
        adj[u].add(v)
        adj[v].add(u)
    vertices = list(range(n))
    for r in range(k+1):
        for subset in itertools.combinations(vertices, r):
            D = set(subset)
            dominated = set(D)
            for v in D:
                dominated.update(adj[v])
            if len(dominated) == n:
                return True
    return False


def generate_all_graphs(n):
    verts = list(range(n))
    possible_edges = [(i,j) for i in range(n) for j in range(i+1,n)]
    for mask in range(1 << len(possible_edges)):
        edges = []
        for idx, (u,v) in enumerate(possible_edges):
            if mask & (1<<idx):
                edges.append([u,v])
        yield edges


def run_tests():
    total = 0
    passed = 0
    for n in range(0,5):
        for edges in generate_all_graphs(n):
            for k in range(-1, n+2):
                vc_instance = {"n": n, "edges": edges, "k": k}
                # validate source
                try:
                    VertexCover.validate(vc_instance)
                except Exception:
                    continue
                vc_ans = vertex_cover_bruteforce(vc_instance)
                ds_instance = reduce(vc_instance)
                ds_ans = dominating_set_bruteforce(ds_instance)
                total += 1
                if vc_ans == ds_ans:
                    passed += 1
                else:
                    print('Mismatch', vc_instance, ds_instance, vc_ans, ds_ans)
    return total, passed

if __name__ == '__main__':
    total, passed = run_tests()
    verdict = {
        "verified": total == passed,
        "tests_run": total,
        "tests_passed": passed,
    }
    print(json.dumps(verdict))
    with open('verdict.json','w') as f:
        json.dump(verdict, f)
