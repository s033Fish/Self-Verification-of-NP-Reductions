import itertools, random, json
from problems import Clique, VertexCover
from reduce import reduce


def solve_clique(instance):
    n = instance['n']
    edges = set(frozenset(e) for e in instance['edges'])
    k = instance['k']
    # Edge cases
    if k <= 0:
        return True
    if k == 1:
        return n >= 1
    if k > n:
        return False
    # brute force
    vertices = list(range(n))
    for size in range(k, n+1):
        for combo in itertools.combinations(vertices, size):
            ok = True
            for u, v in itertools.combinations(combo, 2):
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
    if k < 0:
        return False
    if not edges:
        return k >= 0
    if k >= n:
        return True
    vertices = list(range(n))
    for size in range(0, k+1):
        for combo in itertools.combinations(vertices, size):
            covered = True
            cover_set = set(combo)
            for u, v in edges:
                if u not in cover_set and v not in cover_set:
                    covered = False
                    break
            if covered:
                return True
    return False


def random_instance(max_n=6):
    n = random.randint(0, max_n)
    possible = [(i, j) for i in range(n) for j in range(i+1, n)]
    edges = []
    for u, v in possible:
        if random.choice([True, False]):
            edges.append([u, v])
    k = random.randint(-2, n+2)
    return {"n": n, "edges": edges, "k": k}


def run_tests(num=200):
    passed = 0
    for _ in range(num):
        inst = random_instance()
        # validate input
        Clique.validate(inst)
        # compute answers
        ans_clique = solve_clique(inst)
        reduced = reduce(inst)
        ans_vc = solve_vertex_cover(reduced)
        # reduction correctness: ans_clique == ans_vc
        if ans_clique == ans_vc:
            passed += 1
        else:
            print('FAIL')
            print('orig', inst, ans_clique)
            print('reduced', reduced, ans_vc)
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
