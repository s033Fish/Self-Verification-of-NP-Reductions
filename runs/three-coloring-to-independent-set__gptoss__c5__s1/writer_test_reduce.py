import itertools
import random
import json
from problems import ThreeColoring, IndependentSet, InvalidInstance
from reduce import reduce


def brute_three_coloring(instance):
    n = instance['n']
    edges = instance['edges']
    # Edge cases per definition
    if n == 0:
        return True
    if n <= 3:
        return True
    # check for K4
    # simple check: if there are 4 vertices all pairwise connected, reject
    # but brute will also handle.
    for coloring in itertools.product(range(3), repeat=n):
        ok = True
        for u, v in edges:
            if coloring[u] == coloring[v]:
                ok = False
                break
        if ok:
            return True
    return False


def brute_independent_set(instance):
    n = instance['n']
    edges_set = {frozenset(e) for e in instance['edges']}
    k = instance['k']
    if k <= 0:
        return True
    if k > n:
        return False
    # enumerate subsets of size >= k
    for r in range(k, n+1):
        for subset in itertools.combinations(range(n), r):
            ok = True
            for i in range(len(subset)):
                for j in range(i+1, len(subset)):
                    if frozenset((subset[i], subset[j])) in edges_set:
                        ok = False
                        break
                if not ok:
                    break
            if ok:
                return True
    return False


def random_graph(max_n=5, edge_prob=0.3):
    n = random.randint(0, max_n)
    edges = []
    for u in range(n):
        for v in range(u+1, n):
            if random.random() < edge_prob:
                edges.append([u, v])
    return {"n": n, "edges": edges}


def run_tests(num_tests=200):
    passed = 0
    for _ in range(num_tests):
        src = random_graph()
        # validate source
        try:
            ThreeColoring.validate(src)
        except InvalidInstance:
            continue
        src_ans = brute_three_coloring(src)
        tgt = reduce(src)
        # validate target
        IndependentSet.validate(tgt)
        tgt_ans = brute_independent_set(tgt)
        if src_ans == tgt_ans:
            passed += 1
        else:
            print('FAIL')
            print('src', src)
            print('src_ans', src_ans)
            print('tgt', tgt)
            print('tgt_ans', tgt_ans)
            break
    return passed, num_tests

if __name__ == '__main__':
    passed, total = run_tests(200)
    result = {
        "verified": passed == total,
        "tests_run": total,
        "tests_passed": passed,
    }
    print(json.dumps(result))
    open('verdict.json', 'w').write(json.dumps(result))
