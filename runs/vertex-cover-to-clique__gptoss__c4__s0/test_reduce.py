import itertools
import random
import json
from problems import VertexCover, Clique
from reduce import reduce

def brute_vc(instance):
    n = instance['n']
    edges = instance['edges']
    k = instance['k']
    if k < 0:
        return False
    if not edges:
        return True  # empty edge set always covered
    if k >= n:
        return True
    vertices = list(range(n))
    for r in range(k+1):
        for subset in itertools.combinations(vertices, r):
            covered = True
            for u,v in edges:
                if u not in subset and v not in subset:
                    covered = False
                    break
            if covered:
                return True
    return False

def brute_clique(instance):
    n = instance['n']
    edges_set = {frozenset(e) for e in instance['edges']}
    k = instance['k']
    if k <= 0:
        return True
    if n == 0:
        return False  # k>0 can't be satisfied
    if k == 1:
        return n >= 1
    if k > n:
        return False
    vertices = list(range(n))
    # check subsets of size >=k
    for size in range(k, n+1):
        for subset in itertools.combinations(vertices, size):
            ok = True
            for u,v in itertools.combinations(subset, 2):
                if frozenset((u,v)) not in edges_set:
                    ok = False
                    break
            if ok:
                return True
    return False

def generate_random_instance(max_n=5):
    n = random.randint(0, max_n)
    possible_edges = [(u,v) for u in range(n) for v in range(u+1,n)]
    edges = []
    for (u,v) in possible_edges:
        if random.choice([True, False]):
            edges.append([u,v])
    k = random.randint(-2, n+2)
    return {"n": n, "edges": edges, "k": k}

def run_tests(num=200):
    passed = 0
    for _ in range(num):
        src = generate_random_instance()
        # validate source
        try:
            VertexCover.validate(src)
        except Exception as e:
            print('Invalid source generated', src, e)
            continue
        tgt = reduce(src)
        # validate target
        Clique.validate(tgt)
        ans_src = brute_vc(src)
        ans_tgt = brute_clique(tgt)
        if ans_src == ans_tgt:
            passed += 1
        else:
            print('Mismatch!')
            print('src', src, 'ans_src', ans_src)
            print('tgt', tgt, 'ans_tgt', ans_tgt)
            break
    return passed, num

if __name__ == '__main__':
    passed, total = run_tests(500)
    result = {
        "verified": passed == total,
        "tests_run": total,
        "tests_passed": passed,
    }
    print(json.dumps(result, indent=2))
    with open('verdict.json', 'w') as f:
        json.dump(result, f)
