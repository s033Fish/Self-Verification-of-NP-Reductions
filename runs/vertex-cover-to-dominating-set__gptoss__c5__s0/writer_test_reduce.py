import random
import itertools
import sys
from reduce import reduce
from problems import VertexCover, DominatingSet, InvalidInstance

def vertex_cover_bruteforce(instance):
    n = instance["n"]
    edges = [tuple(e) for e in instance["edges"]]
    k = instance["k"]
    if k < 0:
        return False
    if k >= n:
        return True
    if not edges:
        return True
    # try all subsets up to size k
    for r in range(k+1):
        for subset in itertools.combinations(range(n), r):
            covered = True
            s = set(subset)
            for u, v in edges:
                if u not in s and v not in s:
                    covered = False
                    break
            if covered:
                return True
    return False

def dominating_set_bruteforce(instance):
    n = instance["n"]
    edges = [tuple(e) for e in instance["edges"]]
    k = instance["k"]
    if k < 0:
        return False
    if k >= n:
        return True
    if n == 0:
        return True
    # adjacency list including self
    adj = [set() for _ in range(n)]
    for i in range(n):
        adj[i].add(i)
    for u, v in edges:
        adj[u].add(v)
        adj[v].add(u)
    for r in range(k+1):
        for subset in itertools.combinations(range(n), r):
            dominated = set()
            for v in subset:
                dominated.update(adj[v])
            if len(dominated) == n:
                return True
    return False

def random_instance(max_n=5):
    n = random.randint(0, max_n)
    possible_edges = [(i, j) for i in range(n) for j in range(i+1, n)]
    edges = []
    for (u, v) in possible_edges:
        if random.choice([True, False]):
            edges.append([u, v])
    k = random.randint(-1, n+1)
    return {"n": n, "edges": edges, "k": k}

def main():
    total = 200
    passed = 0
    for _ in range(total):
        src = random_instance()
        # validate source
        try:
            VertexCover.validate(src)
        except InvalidInstance:
            continue
        tgt = reduce(src)
        try:
            DominatingSet.validate(tgt)
        except InvalidInstance:
            print("Reduced instance invalid", src, tgt)
            sys.exit(1)
        ans_src = vertex_cover_bruteforce(src)
        ans_tgt = dominating_set_bruteforce(tgt)
        if ans_src != ans_tgt:
            print("Mismatch!", src, tgt, ans_src, ans_tgt)
            sys.exit(1)
        passed += 1
    print(f"All {passed} random tests passed.")

if __name__ == "__main__":
    main()
