import itertools
import random
import json
from problems import VertexCover, Clique
from reduce import reduce

def vertex_cover_bruteforce(instance):
    n = instance['n']
    edges = [(u, v) for u, v in instance['edges']]
    k = instance['k']
    # Edge cases per definition
    if k < 0:
        return False
    if not edges:
        return True  # empty set covers any k>=0, but if k<0 already handled
    if k >= n:
        return True
    # brute force subsets up to size k
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

def clique_bruteforce(instance):
    n = instance['n']
    edge_set = {frozenset((u, v)) for u, v in instance['edges']}
    k = instance['k']
    # Edge cases
    if k <= 0:
        return True
    if k == 1:
        return n >= 1
    if k > n:
        return False
    vertices = list(range(n))
    # Check subsets of size >= k
    for r in range(k, n+1):
        for subset in itertools.combinations(vertices, r):
            # check all pairs
            ok = True
            for i in range(len(subset)):
                for j in range(i+1, len(subset)):
                    if frozenset((subset[i], subset[j])) not in edge_set:
                        ok = False
                        break
                if not ok:
                    break
            if ok:
                return True
    return False

def random_instance(max_n=6, edge_prob=0.5, k_range=(-2, 8)):
    n = random.randint(0, max_n)
    edges = []
    for u in range(n):
        for v in range(u+1, n):
            if random.random() < edge_prob:
                edges.append([u, v])
    k = random.randint(k_range[0], k_range[1])
    return {"n": n, "edges": edges, "k": k}

def run_tests(num=200):
    passed = 0
    for i in range(num):
        inst = random_instance()
        # validate source
        VertexCover.validate(inst)
        reduced = reduce(inst)
        Clique.validate(reduced)
        src_ans = vertex_cover_bruteforce(inst)
        tgt_ans = clique_bruteforce(reduced)
        if src_ans == tgt_ans:
            passed += 1
        else:
            print('Mismatch on instance', inst)
            print('Reduced', reduced)
            print('src', src_ans, 'tgt', tgt_ans)
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
