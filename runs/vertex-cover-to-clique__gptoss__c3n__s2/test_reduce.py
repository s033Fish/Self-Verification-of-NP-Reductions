import random
import itertools
import json
from problems import VertexCover, Clique
from reduce import reduce


def brute_vertex_cover(instance):
    n = instance["n"]
    edges = [(u, v) for u, v in instance["edges"]]
    k = instance["k"]
    # Edge cases per definition
    if k < 0:
        return False
    if not edges:
        return True  # empty set covers
    if k >= n:
        return True
    for r in range(k + 1):
        for subset in itertools.combinations(range(n), r):
            covered = True
            for u, v in edges:
                if u not in subset and v not in subset:
                    covered = False
                    break
            if covered:
                return True
    return False


def brute_clique(instance):
    n = instance["n"]
    edges_set = {frozenset(e) for e in instance["edges"]}
    k = instance["k"]
    # Edge cases
    if k <= 0:
        return True
    if n == 0:
        return k <= 0
    if k == 1:
        return n >= 1
    if k > n:
        return False
    # check subsets of size >= k
    for size in range(k, n + 1):
        for subset in itertools.combinations(range(n), size):
            ok = True
            for u, v in itertools.combinations(subset, 2):
                if frozenset((u, v)) not in edges_set:
                    ok = False
                    break
            if ok:
                return True
    return False


def generate_random_instance(max_n=6):
    n = random.randint(0, max_n)
    possible_edges = [(i, j) for i in range(n) for j in range(i+1, n)]
    edges = []
    for u, v in possible_edges:
        if random.choice([True, False]):
            edges.append([u, v])
    k = random.randint(-1, n+1)
    return {"n": n, "edges": edges, "k": k}


def run_tests(num=200):
    passed = 0
    for _ in range(num):
        src = generate_random_instance()
        # validate source
        VertexCover.validate(src)
        src_ans = brute_vertex_cover(src)
        tgt = reduce(src)
        Clique.validate(tgt)
        tgt_ans = brute_clique(tgt)
        # According to reduction, src_ans == tgt_ans
        if src_ans == tgt_ans:
            passed += 1
        else:
            print("Mismatch!", src, src_ans, tgt, tgt_ans)
            break
    return passed, num

if __name__ == "__main__":
    passed, total = run_tests(500)
    result = {"verified": passed == total, "tests_run": total, "tests_passed": passed}
    print(json.dumps(result))
    with open("verdict.json", "w") as f:
        json.dump(result, f)
