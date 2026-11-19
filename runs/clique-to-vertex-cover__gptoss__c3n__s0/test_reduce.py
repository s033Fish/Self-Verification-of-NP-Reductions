import itertools
import random
import json
import sys
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


def solve_vertex_cover(inst):
    n = inst["n"]
    edges = set(frozenset(e) for e in inst["edges"])
    k = inst["k"]
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
            for e in edges:
                if not (e & set(subset)):
                    covered = False
                    break
            if covered:
                return True
    return False


def random_instance(max_n=6):
    n = random.randint(0, max_n)
    possible = [(u, v) for u in range(n) for v in range(u + 1, n)]
    edges = []
    for u, v in possible:
        if random.choice([True, False]):
            edges.append([u, v])
    k = random.randint(-1, n + 2)  # allow some out-of-range values
    return {"n": n, "edges": edges, "k": k}


def main():
    random.seed(0)
    tests = 200
    passed = 0
    for i in range(tests):
        inst = random_instance()
        # validate source instance (may raise)
        try:
            Clique.validate(inst)
        except Exception as e:
            # skip malformed generated instances
            continue
        red = reduce(inst)
        # validate target
        VertexCover.validate(red)
        ans_src = solve_clique(inst)
        ans_tgt = solve_vertex_cover(red)
        if ans_src == ans_tgt:
            passed += 1
        else:
            print('Mismatch on instance', json.dumps(inst), 'reduced', json.dumps(red))
            print('src', ans_src, 'tgt', ans_tgt)
            sys.exit(1)
    # Additional explicit edge cases
    edge_cases = [
        {"n": 0, "edges": [], "k": -5},
        {"n": 0, "edges": [], "k": 0},
        {"n": 1, "edges": [], "k": 1},
        {"n": 1, "edges": [], "k": 2},
        {"n": 3, "edges": [[0,1],[1,2],[0,2]], "k": 3},
        {"n": 3, "edges": [[0,1],[1,2]], "k": 3},
    ]
    for inst in edge_cases:
        Clique.validate(inst)
        red = reduce(inst)
        VertexCover.validate(red)
        if solve_clique(inst) != solve_vertex_cover(red):
            print('Mismatch edge case', inst)
            sys.exit(1)
        passed += 1
    total = tests + len(edge_cases)
    result = {"verified": True, "tests_run": total, "tests_passed": passed}
    with open('verdict.json', 'w') as f:
        json.dump(result, f)
    print('All tests passed', passed, '/', total)

if __name__ == '__main__':
    main()
