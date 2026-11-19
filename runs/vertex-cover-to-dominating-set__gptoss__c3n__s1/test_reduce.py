import random
import itertools
import json
from problems import VertexCover, DominatingSet
from reduce import reduce

def brute_vertex_cover(instance):
    n = instance['n']
    edges = [tuple(e) for e in instance['edges']]
    k = instance['k']
    if k < 0:
        return False
    if not edges:
        return True  # empty set covers
    if k >= n:
        return True
    # iterate subsets up to size k
    vertices = list(range(n))
    for r in range(k+1):
        for subset in itertools.combinations(vertices, r):
            s = set(subset)
            ok = all(u in s or v in s for u,v in edges)
            if ok:
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
    adj = [set([i]) for i in range(n)]
    for u,v in edges:
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

def random_instance(max_n=5, edge_prob=0.4, k_range=(-1,5)):
    n = random.randint(0, max_n)
    edges = []
    for u in range(n):
        for v in range(u+1, n):
            if random.random() < edge_prob:
                edges.append([u,v])
    k = random.randint(k_range[0], k_range[1])
    return {"n": n, "edges": edges, "k": k}

def test_one():
    inst = random_instance()
    # validate
    VertexCover.validate(inst)
    ds_inst = reduce(inst)
    DominatingSet.validate(ds_inst)
    vc_ans = brute_vertex_cover(inst)
    ds_ans = brute_dominating_set(ds_inst)
    return vc_ans == ds_ans

def main():
    trials = 200
    passed = 0
    for i in range(trials):
        if test_one():
            passed += 1
    print(f"Passed {passed}/{trials} trials")
    # write verdict
    verdict = {
        "verified": passed == trials,
        "tests_run": trials,
        "tests_passed": passed,
    }
    with open('verdict.json', 'w') as f:
        json.dump(verdict, f)
    print(json.dumps(verdict))

if __name__ == '__main__':
    main()
