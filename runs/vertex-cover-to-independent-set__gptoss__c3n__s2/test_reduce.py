import itertools
import random
import json
from problems import VertexCover, IndependentSet
from reduce import reduce

def solve_vertex_cover(instance):
    n = instance["n"]
    edges = [(u, v) for u, v in instance["edges"]]
    k = instance["k"]
    if k < 0:
        return False
    if not edges:
        return True
    if k >= n:
        return True
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

def solve_independent_set(instance):
    n = instance["n"]
    edges = {(u, v) for u, v in instance["edges"]}
    k = instance["k"]
    if k <= 0:
        return True
    if k > n:
        return False
    vertices = list(range(n))
    # try all subsets of size >= k
    for r in range(k, n+1):
        for subset in itertools.combinations(vertices, r):
            ok = True
            for i in range(len(subset)):
                for j in range(i+1, len(subset)):
                    if (subset[i], subset[j]) in edges or (subset[j], subset[i]) in edges:
                        ok = False
                        break
                if not ok:
                    break
            if ok:
                return True
    return False


def random_instance(max_n=6):
    n = random.randint(0, max_n)
    possible_edges = [(i, j) for i in range(n) for j in range(i+1, n)]
    edges = []
    for (u, v) in possible_edges:
        if random.choice([True, False]):
            edges.append([u, v])
    k = random.randint(-1, n+1)
    return {"n": n, "edges": edges, "k": k}


def run_tests(num=200):
    passed = 0
    for _ in range(num):
        src = random_instance()
        # validate source
        VertexCover.validate(src)
        tgt = reduce(src)
        IndependentSet.validate(tgt)
        ans_src = solve_vertex_cover(src)
        ans_tgt = solve_independent_set(tgt)
        if ans_src == ans_tgt:
            passed += 1
        else:
            print("Mismatch!", src, tgt, ans_src, ans_tgt)
            break
    return passed, num

if __name__ == "__main__":
    passed, total = run_tests(500)
    result = {"verified": passed == total, "tests_run": total, "tests_passed": passed}
    print(json.dumps(result))
    with open("verdict.json", "w") as f:
        json.dump(result, f)
