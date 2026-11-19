import random
import itertools
import json
from reduce import reduce
from problems import VertexCover, Clique


def solve_vertex_cover(instance):
    n = instance["n"]
    edges = [tuple(e) for e in instance["edges"]]
    k = instance["k"]
    if k < 0:
        return False
    # trivial yes cases
    if not edges:
        return True
    if k >= n:
        return True
    vertices = list(range(n))
    for r in range(k + 1):
        for subset in itertools.combinations(vertices, r):
            covered = set()
            for u, v in edges:
                if u in subset or v in subset:
                    covered.add((u, v))
            if len(covered) == len(edges):
                return True
    return False


def solve_clique(instance):
    n = instance["n"]
    edges_set = {tuple(sorted(e)) for e in instance["edges"]}
    k = instance["k"]
    if k <= 0:
        return True
    if n == 0:
        return k <= 0
    if k == 1:
        return n >= 1
    if k > n:
        return False
    vertices = list(range(n))
    # check all subsets of size >=k
    for size in range(k, n + 1):
        for subset in itertools.combinations(vertices, size):
            ok = True
            for u, v in itertools.combinations(subset, 2):
                if tuple(sorted((u, v))) not in edges_set:
                    ok = False
                    break
            if ok:
                return True
    return False


def random_instance(max_n=5):
    n = random.randint(0, max_n)
    possible = [(u, v) for u in range(n) for v in range(u + 1, n)]
    edges = []
    for (u, v) in possible:
        if random.choice([True, False]):
            edges.append([u, v])
    k = random.randint(-1, n + 1)
    return {"n": n, "edges": edges, "k": k}


def main():
    tests = 200
    passed = 0
    for i in range(tests):
        src = random_instance()
        # validate source
        VertexCover.validate(src)
        tgt = reduce(src)
        Clique.validate(tgt)
        ans_src = solve_vertex_cover(src)
        ans_tgt = solve_clique(tgt)
        if ans_src == ans_tgt:
            passed += 1
        else:
            print("Mismatch on test", i)
            print("src", src)
            print("tgt", tgt)
            print("src ans", ans_src, "tgt ans", ans_tgt)
            break
    verdict = {"verified": passed == tests, "tests_run": tests, "tests_passed": passed}
    with open('verdict.json', 'w') as f:
        json.dump(verdict, f)
    print(json.dumps(verdict))

if __name__ == '__main__':
    main()
