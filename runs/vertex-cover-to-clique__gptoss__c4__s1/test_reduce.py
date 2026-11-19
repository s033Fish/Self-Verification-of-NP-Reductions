import random
import itertools
import json
from problems import VertexCover, Clique
from reduce import reduce

def vertex_cover_bruteforce(inst):
    n = inst['n']
    edges = [(u, v) for u, v in inst['edges']]
    k = inst['k']
    if k < 0:
        return False
    if not edges:
        return True
    for r in range(k + 1):
        for subset in itertools.combinations(range(n), r):
            covered = True
            subset_set = set(subset)
            for u, v in edges:
                if u not in subset_set and v not in subset_set:
                    covered = False
                    break
            if covered:
                return True
    return False

def clique_bruteforce(inst):
    n = inst['n']
    edges_set = {tuple(sorted(e)) for e in inst['edges']}
    k = inst['k']
    if k <= 0:
        return True
    if k == 1:
        return n >= 1
    for size in range(k, n + 1):
        for subset in itertools.combinations(range(n), size):
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
    possible = [(i, j) for i in range(n) for j in range(i+1, n)]
    edges = []
    for (u, v) in possible:
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
        Clique.validate(tgt)
        src_ans = vertex_cover_bruteforce(src)
        tgt_ans = clique_bruteforce(tgt)
        if src_ans != tgt_ans:
            print('Mismatch!')
            print('src', src)
            print('tgt', tgt)
            print('src_ans', src_ans, 'tgt_ans', tgt_ans)
            return False, passed
        passed += 1
    return True, passed

if __name__ == '__main__':
    ok, count = run_tests(500)
    verdict = {"verified": ok, "tests_run": count, "tests_passed": count if ok else 0}
    print(json.dumps(verdict))
    with open('verdict.json', 'w') as f:
        json.dump(verdict, f)
