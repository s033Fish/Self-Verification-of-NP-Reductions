import itertools
import random
import json
from typing import List, Dict

from reduce import reduce
from problems import Clique, VertexCover


def brute_clique(instance: Dict) -> bool:
    n = instance["n"]
    edges = set(frozenset(e) for e in instance["edges"])
    k = instance["k"]
    # Edge cases
    if k <= 0:
        return True
    if k == 1:
        return n >= 1
    if k > n:
        return False
    # check all subsets of size >= k
    vertices = list(range(n))
    for size in range(k, n + 1):
        for subset in itertools.combinations(vertices, size):
            ok = True
            for u, v in itertools.combinations(subset, 2):
                if frozenset((u, v)) not in edges:
                    ok = False
                    break
            if ok:
                return True
    return False


def brute_vertex_cover(instance: Dict) -> bool:
    n = instance["n"]
    edges = [tuple(e) for e in instance["edges"]]
    k = instance["k"]
    # Edge cases
    if k < 0:
        return False
    if not edges:
        return k >= 0
    if k >= n:
        return True
    vertices = list(range(n))
    for size in range(0, k + 1):
        for subset in itertools.combinations(vertices, size):
            covered = True
            for u, v in edges:
                if u not in subset and v not in subset:
                    covered = False
                    break
            if covered:
                return True
    return False


def random_instance(max_n=5):
    n = random.randint(0, max_n)
    possible_edges = [(u, v) for u in range(n) for v in range(u + 1, n)]
    edges = []
    for u, v in possible_edges:
        if random.choice([True, False]):
            edges.append([u, v])
    # choose k in range -1..n+2
    k = random.randint(-1, n + 2)
    return {"n": n, "edges": edges, "k": k}


def run_tests(num=200):
    passed = 0
    for i in range(num):
        src = random_instance()
        # validate source
        Clique.validate(src)
        tgt = reduce(src)
        VertexCover.validate(tgt)
        ans_src = brute_clique(src)
        ans_tgt = brute_vertex_cover(tgt)
        if ans_src == ans_tgt:
            passed += 1
        else:
            print("Mismatch!", src, tgt, ans_src, ans_tgt)
            break
    return passed, num

if __name__ == "__main__":
    passed, total = run_tests(500)
    result = {
        "verified": passed == total,
        "tests_run": total,
        "tests_passed": passed,
    }
    print(json.dumps(result, indent=2))
    with open("verdict.json", "w") as f:
        json.dump(result, f)
