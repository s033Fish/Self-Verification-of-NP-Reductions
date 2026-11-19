import itertools
import random
import json
from problems import ThreeColoring, IndependentSet
from reduce import reduce

def three_coloring_bruteforce(instance):
    n = instance['n']
    edges = instance['edges']
    # edge case n=0 always yes
    if n == 0:
        return True
    # any graph with <=3 vertices is yes (by definition)
    if n <= 3:
        return True
    # check for K4 (complete graph on 4 vertices) -> no
    if n == 4:
        # check if edges contain all 6 pairs
        required = {frozenset((i,j)) for i in range(4) for j in range(i+1,4)}
        present = {frozenset(e) for e in edges}
        if required.issubset(present):
            return False
    # brute force assign colors 0,1,2
    for coloring in itertools.product(range(3), repeat=n):
        ok = True
        for u,v in edges:
            if coloring[u] == coloring[v]:
                ok = False
                break
        if ok:
            return True
    return False

def independent_set_bruteforce(instance):
    n = instance['n']
    edges = instance['edges']
    k = instance['k']
    if k <= 0:
        return True
    if k > n:
        return False
    # build adjacency set for quick check
    adj = {i:set() for i in range(n)}
    for u,v in edges:
        adj[u].add(v)
        adj[v].add(u)
    # check all subsets of size >=k
    for size in range(k, n+1):
        for subset in itertools.combinations(range(n), size):
            independent = True
            for u in subset:
                for v in subset:
                    if u < v and v in adj[u]:
                        independent = False
                        break
                if not independent:
                    break
            if independent:
                return True
    return False

def random_graph(max_n=5, edge_prob=0.4):
    n = random.randint(0, max_n)
    edges = []
    for i in range(n):
        for j in range(i+1, n):
            if random.random() < edge_prob:
                edges.append([i,j])
    return {"n": n, "edges": edges}

def run_tests(num=200):
    passed = 0
    for _ in range(num):
        src = random_graph()
        # validate source
        ThreeColoring.validate(src)
        src_ans = three_coloring_bruteforce(src)
        tgt = reduce(src)
        # validate target
        IndependentSet.validate(tgt)
        tgt_ans = independent_set_bruteforce(tgt)
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
    print(json.dumps(result, indent=2))
    with open('verdict.json', 'w') as f:
        json.dump(result, f)
