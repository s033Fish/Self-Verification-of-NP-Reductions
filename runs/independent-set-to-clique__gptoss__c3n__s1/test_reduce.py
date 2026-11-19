import random
import itertools
import json
from problems import IndependentSet, Clique
from reduce import reduce


def brute_independent_set(instance):
    n = instance['n']
    edges = set(frozenset(e) for e in instance['edges'])
    k = instance['k']
    if k <= 0:
        return True
    if k > n:
        return False
    # enumerate subsets of size >= k
    for size in range(k, n+1):
        for subset in itertools.combinations(range(n), size):
            ok = True
            for u, v in itertools.combinations(subset, 2):
                if frozenset((u, v)) in edges:
                    ok = False
                    break
            if ok:
                return True
    return False


def brute_clique(instance):
    n = instance['n']
    edges = set(frozenset(e) for e in instance['edges'])
    k = instance['k']
    if k <= 0:
        return True
    if k == 1:
        return n >= 1
    if k > n:
        return False
    for size in range(k, n+1):
        for subset in itertools.combinations(range(n), size):
            ok = True
            for u, v in itertools.combinations(subset, 2):
                if frozenset((u, v)) not in edges:
                    ok = False
                    break
            if ok:
                return True
    return False


def random_instance(max_n=6):
    n = random.randint(0, max_n)
    possible = [(u, v) for u in range(n) for v in range(u+1, n)]
    edges = []
    for (u, v) in possible:
        if random.choice([True, False]):
            edges.append([u, v])
    k = random.randint(-1, n+2)  # include out of range values
    return {"n": n, "edges": edges, "k": k}


def run_tests(num=200):
    passed = 0
    for _ in range(num):
        inst = random_instance()
        # validate source
        IndependentSet.validate(inst)
        src_ans = brute_independent_set(inst)
        tgt = reduce(inst)
        Clique.validate(tgt)
        tgt_ans = brute_clique(tgt)
        if src_ans != tgt_ans:
            print('Mismatch!')
            print('source', inst, src_ans)
            print('target', tgt, tgt_ans)
            return False, passed
        passed += 1
    return True, passed

if __name__ == '__main__':
    ok, count = run_tests(500)
    result = {
        "verified": ok,
        "tests_run": count,
        "tests_passed": count if ok else count
    }
    print(json.dumps(result))
    # write verdict file
    with open('verdict.json', 'w') as f:
        json.dump(result, f)
