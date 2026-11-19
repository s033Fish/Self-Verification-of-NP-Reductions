import random
import itertools
import json
from problems import VertexCover, DominatingSet
from reduce import reduce


def vertex_cover_bruteforce(inst):
    n = inst["n"]
    edges = inst["edges"]
    k = inst["k"]
    if k < 0:
        return False
    # any subset of vertices up to size k
    vertices = list(range(n))
    for r in range(k + 1):
        for subset in itertools.combinations(vertices, r):
            covered = True
            s = set(subset)
            for u, v in edges:
                if u not in s and v not in s:
                    covered = False
                    break
            if covered:
                return True
    return False


def dominating_set_bruteforce(inst):
    n = inst["n"]
    edges = inst["edges"]
    k = inst["k"]
    if k < 0:
        return False
    # adjacency list
    adj = [set() for _ in range(n)]
    for u, v in edges:
        adj[u].add(v)
        adj[v].add(u)
    vertices = list(range(n))
    for r in range(k + 1):
        for subset in itertools.combinations(vertices, r):
            D = set(subset)
            ok = True
            for v in vertices:
                if v not in D and not (adj[v] & D):
                    ok = False
                    break
            if ok:
                return True
    return False


def random_instance(max_n=5):
    n = random.randint(0, max_n)
    possible_edges = [(i, j) for i in range(n) for j in range(i + 1, n)]
    edges = []
    for (u, v) in possible_edges:
        if random.random() < 0.3:
            edges.append([u, v])
    k = random.randint(-1, n + 2)
    return {"n": n, "edges": edges, "k": k}


def run_tests(num=200):
    passed = 0
    for _ in range(num):
        src = random_instance()
        # validate source
        VertexCover.validate(src)
        # compute answers
        ans_src = vertex_cover_bruteforce(src)
        tgt = reduce(src)
        DominatingSet.validate(tgt)
        ans_tgt = dominating_set_bruteforce(tgt)
        if ans_src != ans_tgt:
            print("Mismatch!", src, tgt, ans_src, ans_tgt)
            return False, passed
        passed += 1
    return True, passed

if __name__ == "__main__":
    ok, cnt = run_tests(500)
    verdict = {"verified": ok, "tests_run": cnt, "tests_passed": cnt if ok else 0}
    print(json.dumps(verdict))
    # also write verdict.json file
    with open('verdict.json', 'w') as f:
        json.dump(verdict, f)
