import random
import itertools
import json
from problems import Clique, VertexCover
from reduce import reduce


def solve_clique(inst):
    n = inst["n"]
    edges = set(frozenset(e) for e in inst["edges"])
    k = inst["k"]
    # Edge cases
    if k <= 0:
        return True
    if k == 1:
        return n >= 1
    if k > n:
        return False
    # brute force subsets of size >= k
    vertices = list(range(n))
    for r in range(k, n+1):
        for subset in itertools.combinations(vertices, r):
            ok = True
            for u, v in itertools.combinations(subset, 2):
                if frozenset((u, v)) not in edges:
                    ok = False
                    break
            if ok:
                return True
    return False


def solve_vertex_cover(inst):
    n = inst["n"]
    edges = [tuple(e) for e in inst["edges"]]
    k = inst["k"]
    # Edge cases
    if k < 0:
        return False
    if not edges:
        return k >= 0
    if k >= n:
        return True
    vertices = list(range(n))
    for r in range(0, k+1):
        for subset in itertools.combinations(vertices, r):
            covered = True
            for u, v in edges:
                if u not in subset and v not in subset:
                    covered = False
                    break
            if covered:
                return True
    return False


def random_instance(max_n=6):
    n = random.randint(0, max_n)
    possible = [(u, v) for u in range(n) for v in range(u+1, n)]
    edges = []
    for (u, v) in possible:
        if random.choice([True, False]):
            edges.append([u, v])
    k = random.randint(-2, n+2)
    return {"n": n, "edges": edges, "k": k}


def main():
    tests = 200
    passed = 0
    for i in range(tests):
        src = random_instance()
        # Validate source
        Clique.validate(src)
        # Reduce
        tgt = reduce(src)
        VertexCover.validate(tgt)
        ans_src = solve_clique(src)
        ans_tgt = solve_vertex_cover(tgt)
        if ans_src == ans_tgt:
            passed += 1
        else:
            print("Mismatch!", src, tgt, ans_src, ans_tgt)
            break
    verdict = {
        "verified": passed == tests,
        "tests_run": tests,
        "tests_passed": passed,
    }
    print(json.dumps(verdict))
    with open("verdict.json", "w") as f:
        json.dump(verdict, f)

if __name__ == "__main__":
    main()
