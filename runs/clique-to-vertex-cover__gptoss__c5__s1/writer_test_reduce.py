import random
import itertools
import json
from problems import Clique, VertexCover
from reduce import reduce


def solve_clique(instance):
    n = instance['n']
    edges = set(frozenset(e) for e in instance['edges'])
    k = instance['k']
    # Edge cases per definition
    if k <= 0:
        return True
    if k == 1:
        return n >= 1
    if k > n:
        return False
    # brute force subsets
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


def solve_vertex_cover(instance):
    n = instance['n']
    edges = [tuple(e) for e in instance['edges']]
    k = instance['k']
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
    k = random.randint(-1, n+2)  # allow out of range
    return {"n": n, "edges": edges, "k": k}


def run_tests(num=200):
    passed = 0
    for i in range(num):
        inst = random_instance()
        # validate inputs (may raise)
        Clique.validate(inst)
        # solve original
        ans_clique = solve_clique(inst)
        # reduce
        red = reduce(inst)
        VertexCover.validate(red)
        ans_vc = solve_vertex_cover(red)
        # according to reduction, ans_clique == ans_vc
        if ans_clique == ans_vc:
            passed += 1
        else:
            print('FAIL on instance', inst)
            print('Reduced', red)
            print('Answers', ans_clique, ans_vc)
            break
    return num, passed

if __name__ == '__main__':
    total, passed = run_tests(500)
    result = {
        "verified": total == passed,
        "tests_run": total,
        "tests_passed": passed,
    }
    print(json.dumps(result))
    with open('verdict.json', 'w') as f:
        json.dump(result, f)
