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
        return True  # empty set covers
    for size in range(k+1):
        for combo in itertools.combinations(range(n), size):
            covered = True
            for u,v in edges:
                if u not in combo and v not in combo:
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
    if n == 0:
        return True
    # build adjacency list
    adj = {i:set() for i in range(n)}
    for u,v in edges:
        adj[u].add(v)
        adj[v].add(u)
    for size in range(k+1):
        for combo in itertools.combinations(range(n), size):
            dominated = set(combo)
            for v in combo:
                dominated.update(adj[v])
            if len(dominated) == n:
                return True
    return False

# generate random small instances and test reduction
random.seed(0)
tests = 0
passed = 0
for n in range(0,5):
    # generate all possible edge subsets up to n choose 2
    vertices = list(range(n))
    possible_edges = [(i,j) for i in vertices for j in vertices if i<j]
    for edges_subset in itertools.chain.from_iterable(itertools.combinations(possible_edges, r) for r in range(len(possible_edges)+1)):
        edges = [list(e) for e in edges_subset]
        for k in range(-1, n+2):
            vc_instance = {"n": n, "edges": edges, "k": k}
            # validate
            try:
                VertexCover.validate(vc_instance)
            except Exception as e:
                continue
            vc_ans = vertex_cover_bruteforce(vc_instance)
            reduced = reduce(vc_instance)
            ds_ans = dominating_set_bruteforce(reduced)
            tests += 1
            if vc_ans == ds_ans:
                passed += 1
            else:
                print('Mismatch', vc_instance, reduced, vc_ans, ds_ans)

print('Tests run:', tests, 'Passed:', passed)
# write verdict
verdict = {"verified": passed==tests, "tests_run": tests, "tests_passed": passed}
with open('verdict.json','w') as f:
    json.dump(verdict, f)
